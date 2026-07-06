import os
import sys
import time
import paramiko
from dotenv import load_dotenv

# Konfiguration wird aus Umgebungsvariablen (bzw. lokaler .env) geladen — keine
# Zugangsdaten oder systemspezifischen Pfade im Quellcode. Vorlage: .env.example.
load_dotenv()

def safe_print(label, text):
    if not text:
        return
    encoding = sys.stdout.encoding or 'utf-8'
    safe_text = text.encode(encoding, errors='replace').decode(encoding)
    print(f"{label}: {safe_text}")

def run_cmd(ssh, command):
    print(f"Running command: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    err = stderr.read().decode('utf-8', errors='ignore').strip()
    
    safe_print("STDOUT", out)
    safe_print("STDERR", err)
        
    return stdout.channel.recv_exit_status(), out, err

def main():
    # Zugangsdaten und Zielpfade ausschließlich aus der Umgebung (siehe .env.example).
    server = os.environ.get("WISSKOMM_VM_HOST")
    user = os.environ.get("WISSKOMM_VM_USER")
    password = os.environ.get("WISSKOMM_VM_PASSWORD")
    remote_dir = os.environ.get("WISSKOMM_VM_REMOTE_DIR", "/home/sts/wisskomm-viz")
    quarto_dir = os.environ.get("WISSKOMM_QUARTO_DIR", "/home/sts/wisskomm-quarto-pilot")
    # Bootstrap-Pip einer vorhandenen venv auf der VM, um virtualenv zu installieren.
    bootstrap_pip = os.environ.get(
        "WISSKOMM_VM_BOOTSTRAP_PIP", "/home/sts/stellar-galaxy/venv/bin/pip"
    )

    missing = [k for k, v in {
        "WISSKOMM_VM_HOST": server,
        "WISSKOMM_VM_USER": user,
    }.items() if not v]
    if missing:
        print("FEHLER: Fehlende Umgebungsvariablen: " + ", ".join(missing))
        print("Bitte .env aus .env.example anlegen und befüllen.")
        sys.exit(1)

    # 1. SSH Verbindung aufbauen
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Verbinde mit {server}...")
    try:
        if password:
            ssh.connect(server, 22, user, password, timeout=15)
        else:
            # Versuche schlüsselspezifischen SSH-Login aus ~/.ssh/
            ssh.connect(server, 22, user, timeout=15)
        print("SSH-Verbindung erfolgreich!")
    except Exception as e:
        print(f"Verbindung fehlgeschlagen: {e}")
        sys.exit(1)
        
    # 2. Verzeichnisse auf dem Server vorbereiten
    run_cmd(ssh, f"mkdir -p {remote_dir}/templates {remote_dir}/sessions {remote_dir}/output")
    run_cmd(ssh, f"mkdir -p {quarto_dir}/templates {quarto_dir}/theme/fonts")
    
    # 3. Dateien per SFTP hochladen
    print("Lade Anwendungsdateien hoch...")
    sftp = ssh.open_sftp()
    
    local_files = [
        # Anwendungsdateien für remote_dir
        ("app.py", f"{remote_dir}/app.py"),
        ("prompt.py", f"{remote_dir}/prompt.py"),
        ("build.py", f"{remote_dir}/build.py"),
        ("build_quarto.py", f"{remote_dir}/build_quarto.py"),
        ("requirements.txt", f"{remote_dir}/requirements.txt"),
        ("templates/standalone.html", f"{remote_dir}/templates/standalone.html"),
        ("templates/dashboard.html", f"{remote_dir}/templates/dashboard.html"),
        ("templates/ui.html", f"{remote_dir}/templates/ui.html"),
        ("templates/publication.qmd.j2", f"{remote_dir}/templates/publication.qmd.j2"),
        
        # Quarto-Projektdateien für quarto_dir
        ("_quarto.yml", f"{quarto_dir}/_quarto.yml"),
        ("_brand.yml", f"{quarto_dir}/_brand.yml"),
        ("theme/zew.scss", f"{quarto_dir}/theme/zew.scss"),
        ("templates/publication.qmd.j2", f"{quarto_dir}/templates/publication.qmd.j2"),
        ("templates/reference-zew.pptx", f"{quarto_dir}/templates/reference-zew.pptx"),
        
        # Schriften für Quarto-Projekt
        ("theme/fonts/calibri.ttf", f"{quarto_dir}/theme/fonts/calibri.ttf"),
        ("theme/fonts/calibrib.ttf", f"{quarto_dir}/theme/fonts/calibrib.ttf"),
        ("theme/fonts/calibrii.ttf", f"{quarto_dir}/theme/fonts/calibrii.ttf"),
        ("theme/fonts/calibriz.ttf", f"{quarto_dir}/theme/fonts/calibriz.ttf"),
        ("theme/fonts/LinLibertine_R.ttf", f"{quarto_dir}/theme/fonts/LinLibertine_R.ttf"),
        ("theme/fonts/LinLibertine_RB.ttf", f"{quarto_dir}/theme/fonts/LinLibertine_RB.ttf"),
        ("theme/fonts/LinLibertine_RI.ttf", f"{quarto_dir}/theme/fonts/LinLibertine_RI.ttf")
    ]
    
    for local_path, remote_path in local_files:
        print(f"  Uploading {local_path} -> {remote_path}")
        sftp.put(local_path, remote_path)
        
    sftp.close()
    
    # 4. Virtuelles Environment (venv) einrichten
    print("Richte Python Virtual Environment ein (mittels virtualenv)...")
    bootstrap_dir = bootstrap_pip.rsplit("/", 1)[0]
    run_cmd(ssh, f"{bootstrap_pip} install virtualenv")
    run_cmd(ssh, f"{bootstrap_dir}/virtualenv {remote_dir}/venv")
    
    # Abhängigkeiten installieren
    print("Installiere Python-Bibliotheken...")
    run_cmd(ssh, f"{remote_dir}/venv/bin/pip install -r {remote_dir}/requirements.txt")
    
    # 5. .env Datei anlegen falls nicht vorhanden
    print("Prüfe .env-Konfiguration...")
    status, _, _ = run_cmd(ssh, f"ls -la {remote_dir}/.env")
    if status != 0:
        print("  Erstelle neue .env Datei mit Platzhalter...")
        local_key = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
        run_cmd(ssh, f"echo 'ANTHROPIC_API_KEY={local_key}' > {remote_dir}/.env")
        print(f"  [WARNUNG] .env wurde erstellt. Bitte trage Deinen echten API-Key in {remote_dir}/.env ein!")
    else:
        print("  .env Datei existiert bereits. Übersprungen.")
        
    # 6. Alten Prozess stoppen falls vorhanden (idempotent)
    print("Stoppe eventuell laufende Instanzen...")
    run_cmd(ssh, "pkill -f 'uvicorn app:app.*8090' || true")
    time.sleep(2)
    
    # 7. Starten der App im Hintergrund (Wichtig: </dev/null beugt Hängern in Paramiko vor!)
    print("Starte FastAPI-App im Hintergrund auf Port 8090...")
    start_cmd = f"cd {remote_dir} && nohup venv/bin/uvicorn app:app --host 127.0.0.1 --port 8090 --env-file .env </dev/null >uvicorn.log 2>&1 &"
    run_cmd(ssh, start_cmd)
    time.sleep(3)
    
    # 8. Autostart einrichten per user-level Crontab
    print("Richte Autostart bei Reboot ein (Crontab)...")
    cron_job = f"@reboot cd {remote_dir} && nohup venv/bin/uvicorn app:app --host 127.0.0.1 --port 8090 --env-file .env </dev/null >uvicorn.log 2>&1 &"
    run_cmd(ssh, f"(crontab -l 2>/dev/null | grep -v 'uvicorn app:app' ; echo '{cron_job}') | crontab -")
    
    # 9. Verifizieren des Status
    print("Verifiziere Port-Aktivität...")
    status, out, _ = run_cmd(ssh, "ss -tln | grep 8090")
    if "8090" in out:
        print("\n✅ DER WEB-DIENST LÄUFT ERFOLGREICH AUF PORT 8090!")
    else:
        print("\n❌ Fehler beim Starten des Dienstes. Bitte prüfe uvicorn.log auf dem Server:")
        run_cmd(ssh, f"cat {remote_dir}/uvicorn.log")
        
    ssh.close()
    # 8090 lauscht nur auf localhost; öffentlich erreichbar über den Django-Proxy auf 8080.
    print(f"\nDeployment abgeschlossen! Erreichbar über den Proxy unter: http://{server}:8080/wisskomm")

if __name__ == "__main__":
    main()
