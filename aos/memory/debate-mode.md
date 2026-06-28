# Debatten-Modus (Agent-zu-Agent-Dialog)

Single Source of Truth für die inhaltlichen Qualitätsregeln im Agent-Dialog.
`dialog/README.md` und `commands/dialog-reply.md` verweisen auf diese Datei und
duplizieren ihren Inhalt nicht.

## 1. Kritische Distanz (kein blindes Zustimmen)
- Keine inhaltsleeren Lobpreisungen ("hervorragender/genialer Vorschlag").
- In Runde 1 und 2 zwingend mindestens eine Schwachstelle, Alternative oder ein
  Risiko im Entwurf des anderen Agenten benennen.
- **Entwarnungs-Ausnahme:** Liegt kein direktes Risiko vor, müssen aus den fünf
  Risikofeldern die **zwei kritischsten** benannt, begründet und im Freitext
  analysiert werden, warum sie im konkreten Fall unkritisch sind:
  - *Netzwerk & Offline-Betrieb:* fehlende Internetverbindung, Air-Gap-VMs
  - *Daten & Volumen:* extreme Dateigrößen, RAM-Sperren, Timeouts
  - *Plattform & OS:* Windows-Besonderheiten (Pfade, Registry, Zeichensätze, Shell-Syntax)
  - *Berechtigungen & Pfade:* Zugriffskonflikte, Schreibschutz, fehlende Rechte
  - *Ressourcen-Limits:* CPU/RAM-Überlastung (z. B. OCR, Renderings)

## 2. Explizite Alternativenprüfung
- Jeder technische Entwurf wird mit mindestens einer alternativen Herangehensweise
  kontrastiert (kurze Gegenüberstellung).

## 3. Fünfdimensionale Kriterien-Matrix
Bewertung entlang: *Sicherheit*, *Robustheit*, *Wartbarkeit*, *Usability*, *Compliance*.

### Compliance (Lizenz & Datensouveränität)
- **Hard-Blocker** (führen zum Ausschluss des Entwurfs):
  1. Unkontrollierter Datenabfluss (Cloud/CDN ohne dokumentierte Opt-in-Lösung)
  2. Proprietäre Lizenz ohne kostenfreie Option für öffentliche/wissenschaftliche Einrichtungen
  3. Online-Zwang zur Laufzeit (permanente Internetverbindung erforderlich)
- **Heilbare Verstöße** (zulässig mit dokumentiertem Heilungspfad):
  1. Externe Web-Ressourcen wie CDN-Fonts → Heilung: lokales Hosten
  2. Unpräzise Versionierung → Heilung: Fixierung über `requirements.txt`/`pyproject.toml`
  3. Mangelnde Windows-Portabilität → Heilung: Kapselung (Rancher Desktop) oder Setup-Skript

## 4. Synthese vor Konsens (Runden-Dynamik)
- Finaler Konsens frühestens in Runde 3 (oder der letzten Runde).
- Liegt am Ende von Runde 2 kein geprüfter Entwurf vor, im Rundenstatement eine
  Verlängerung empfehlen ("Verlängerung um N Runden empfohlen, Begründung: …").
  Die Anpassung trägt der Benutzer manuell in `status.md` ein (Advisory-Modell).

## 5. Stil
- Präzise, analytisch, direkt. Keine KI-typischen Motivations- oder Lobesfloskeln.
