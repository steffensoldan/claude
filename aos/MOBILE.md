# AOS — Mobile Dispatcher Setup

## Voraussetzungen
- Mobile App "Claude Desktop" auf dem Smartphone/Tablet angemeldet.
- Claude CLI auf der Windows-VM installiert und im globalen Path (`claude --version`).

## Kopplung starten
1. PowerShell-Konsole auf der Windows-VM öffnen.
2. `claude` ausführen → die CLI startet und zeigt den 6-stelligen Koppelungscode.
3. In der mobilen App auf dem Handy: *Menü → Mit Computer koppeln* → Code eingeben.

## Prozessbereinigung bei blockierten Koppelungen
Falls verwaiste `claude`-Prozesse auf der VM den Socket blockieren, führen Sie vor dem Start folgenden PowerShell-Einzeiler aus:
```powershell
Get-Process -Name "claude" -ErrorAction SilentlyContinue | Stop-Process -Force; Start-Sleep -Seconds 2; claude
```

## Datenklassifizierung (Zwingendes Compliance-Gate)
Über das Cloud-Relay des Dispatchers dürfen ausschließlich verarbeitet werden:
- Öffentlich zugängliche oder vollständig anonymisierte Forschungsdaten.
- Quellcode und Textdokumente ohne eingebettete Credentials/Secrets.

*Nicht zulässig:* Personenbezogene Primärdaten (z. B. Umfrageteilnehmer), vertrauliche ZEW-Finanz-, Vertrags- oder Personalunterlagen, Passwörter und private API-Schlüssel.

## Timeout- & Recovery-Handling
iOS und Android trennen App-Hintergrundverbindungen nach ca. 3–10 Minuten Inaktivität.
- **VM-seitig:** CLI im Terminal mit `Strg+C` beenden und `claude` neu starten.
- **Handy-seitig:** App schließen, neu öffnen und erneut koppeln.
- Laufende Hintergrundprozesse (z. B. `git` oder Builds auf der VM) laufen stabil weiter.

## Git-Workflow nach einer Session
Direkt im VM-Terminal ausführen:
```powershell
cd <AOS_ROOT>\projects\<Kategorie>\<Projektname>
git add -A
git commit -m "Session: $(Get-Date -Format 'yyyy-MM-dd') — Mobile Ergänzungen"
git push origin main
```
