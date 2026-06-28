---
name: sync
description: Sicherer Git-Sync-Zyklus. Status zeigen, committen, pullen, pushen. Aufruf via /sync <Commit-Nachricht>.
---

Führe einen sicheren Git-Sync aus. Halte dich strikt an diese Reihenfolge und brich bei jedem Fehler ab:

1. `git status` ausführen — fasse zusammen, was sich geändert hat.
2. Falls uncommittete Änderungen vorhanden:
   - Wurde eine Commit-Nachricht übergeben ($ARGUMENTS)? Dann: `git add -A` und `git commit -m "$ARGUMENTS"`.
   - Fehlt die Nachricht: FRAGE nach einer Nachricht. Committe nicht blind.
3. `git pull --no-rebase` ausführen.
   - Bei Merge-Konflikt: SOFORT STOPPEN. Konfliktdateien auflisten. Nichts automatisch auflösen. Auf Entscheidung warten.
4. Nur wenn pull sauber war: `git push`.
5. Abschlussstatus melden: Branch, letzter Commit, ob push erfolgreich.

Niemals `--force`. Niemals Konflikte selbst auflösen. Niemals Schritte überspringen.
