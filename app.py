import os
import io
import re
import json
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

import prompt
import build

app = FastAPI()

# Verzeichnisse definieren
BASE_DIR = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
OUTPUT_DIR = BASE_DIR / "output"

SESSIONS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Templates laden
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Statische Dateien mounten unter /wisskomm/view
app.mount("/wisskomm/view", StaticFiles(directory=str(OUTPUT_DIR)), name="view")

def slugify(text: str) -> str:
    """Konvertiert den Dateinamen in einen sauberen URL-Slug."""
    text = text.lower()
    if text.endswith(".pdf"):
        text = text[:-4]
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")

def extract_pdf_text(file_bytes: bytes) -> str:
    """Extrahiert den Text aus den PDF-Bytes."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

@app.get("/wisskomm", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Zeigt die Übersicht aller Publikationen und das Upload-Formular."""
    publications = []
    
    # Durchlaufe alle Sessions und sammle Metadaten
    for session_file in SESSIONS_DIR.glob("*.json"):
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session = json.load(f)
                publications.append({
                    "slug": session_file.stem,
                    "title": session.get("data", {}).get("title", "Unbenannter Befund"),
                    "last_modified": session.get("last_modified", "Unbekannt")
                })
        except Exception as e:
            print(f"Fehler beim Laden von {session_file}: {e}")
            
    # Sortieren nach Modifikationsdatum (neueste zuerst)
    publications.sort(key=lambda x: x["last_modified"], reverse=True)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "publications": publications
    })

@app.post("/wisskomm/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    instructions: str = Form(None)
):
    """Verarbeitet den Upload, ruft Claude API auf und generiert das erste HTML."""
    file_bytes = await file.read()
    
    # 1. Text extrahieren
    try:
        paper_text = extract_pdf_text(file_bytes)
        if not paper_text.strip():
            raise ValueError("Das PDF enthält keinen extrahierbaren Text.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF-Extraktion fehlgeschlagen: {e}")
        
    # 2. Slug generieren
    slug = slugify(file.filename)
    if not slug:
        slug = f"publikation-{int(datetime.now().timestamp())}"
        
    # Eindeutigkeit sichern falls schon vorhanden
    if (SESSIONS_DIR / f"{slug}.json").exists():
        slug = f"{slug}-{int(datetime.now().timestamp())}"
        
    # 3. Verlauf aufsetzen
    initial_user_prompt = f"Hier ist das wissenschaftliche Papier:\n\n{paper_text}\n\nBitte extrahiere die Daten und erstelle den ersten Befund kompakt."
    if instructions and instructions.strip():
        initial_user_prompt += f"\n\nFolgende Sonderwünsche und Kriterien müssen unbedingt beachtet werden:\n{instructions}"
        
    history = [
        {"role": "user", "content": initial_user_prompt}
    ]
    
    # 4. Claude aufrufen
    try:
        data = await prompt.query_claude(history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude API Fehler: {e}")
        
    # Assistenten-Antwort (JSON) zur History hinzufügen
    history.append({"role": "assistant", "content": json.dumps(data, ensure_ascii=False)})
    
    # 5. Session speichern
    session = {
        "slug": slug,
        "paper_text": paper_text,
        "history": history,
        "data": data,
        "last_modified": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }
    
    with open(SESSIONS_DIR / f"{slug}.json", "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2, ensure_ascii=False)
        
    # 6. HTML generieren
    try:
        build.build_html(slug, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML-Kompilierung fehlgeschlagen: {e}")
        
    return RedirectResponse(url=f"/wisskomm/edit/{slug}", status_code=303)

@app.get("/wisskomm/edit/{slug}", response_class=HTMLResponse)
async def edit_page(request: Request, slug: str):
    """Zeigt das Side-by-Side-Refinement Interface."""
    session_file = SESSIONS_DIR / f"{slug}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Sitzung nicht gefunden.")
        
    with open(session_file, "r", encoding="utf-8") as f:
        session = json.load(f)
        
    # Wir filtern die History für die Chat-Anzeige
    display_history = []
    for msg in session["history"][1:]:
        if msg["role"] == "assistant":
            display_history.append({"role": "assistant", "content": "Template aktualisiert."})
        else:
            display_history.append(msg)
            
    return templates.TemplateResponse("ui.html", {
        "request": request,
        "slug": slug,
        "title": session["data"].get("title", "Befund"),
        "history": display_history
    })

@app.post("/wisskomm/refine/{slug}")
async def refine_page(slug: str, feedback: str = Form(...)):
    """Nimmt Feedback entgegen, fragt Claude nach Anpassungen und baut das HTML neu."""
    session_file = SESSIONS_DIR / f"{slug}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Sitzung nicht gefunden.")
        
    with open(session_file, "r", encoding="utf-8") as f:
        session = json.load(f)
        
    # 1. Feedback zur History hinzufügen
    session["history"].append({"role": "user", "content": feedback})
    
    # 2. Claude API aufrufen mit dem gesamten Verlauf
    try:
        updated_data = await prompt.query_claude(session["history"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude API Fehler bei Verfeinerung: {e}")
        
    # 3. Antwort an History anhängen
    session["history"].append({"role": "assistant", "content": json.dumps(updated_data, ensure_ascii=False)})
    
    # 4. Session aktualisieren
    session["data"] = updated_data
    session["last_modified"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2, ensure_ascii=False)
        
    # 5. HTML neu generieren
    try:
        build.build_html(slug, updated_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML-Kompilierung fehlgeschlagen: {e}")
        
    return JSONResponse(content={"status": "ok"})
