#!/usr/bin/env bash
# PreToolUse-Guardrail für Claude Code.
# Blockt offensichtlich destruktive Bash-Befehle, bevor sie ausgeführt werden.
# Aktivierung über ~/.claude/settings.json (PreToolUse). Siehe README Abschnitt 3 "Setup & Sicherheits-Hook aktivieren" — install.ps1 setzt dies automatisch.
#
# Funktionsweise: Claude Code übergibt das Tool-Event als JSON via stdin.
# Exit-Code 2 = Befehl blockieren. Exit-Code 0 = erlauben.

set -euo pipefail

# JSON vom stdin lesen
INPUT="$(cat)"

# jq ist Pflicht. Fehlt es, FAIL-CLOSED (blockieren) statt unsicher durchlassen.
if ! command -v jq >/dev/null 2>&1; then
  echo "BLOCKIERT: 'jq' nicht gefunden — Guardrail kann Befehl nicht prüfen." >&2
  echo "Installiere jq (z. B. 'winget install jqlang.jq' / 'apt install jq') und wiederhole." >&2
  exit 2
fi

# Auszuführenden Befehl extrahieren
CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null || true)"

# Wenn kein Befehl vorhanden ist (z. B. anderes Tool als Bash), durchlassen
if [ -z "$CMD" ]; then
  exit 0
fi

# Liste destruktiver Muster. Erweiterbar nach Bedarf.
PATTERNS=(
  'rm[[:space:]]+-rf?[[:space:]]+/'        # rm -rf / oder rm -r /
  'rm[[:space:]]+-rf?[[:space:]]+~'        # rm -rf ~
  'rm[[:space:]]+-rf?[[:space:]]+\*'       # rm -rf *
  'git[[:space:]]+push[[:space:]].*--force' # erzwungener Push
  'git[[:space:]]+push[[:space:]].*-f([[:space:]]|$)'
  'git[[:space:]]+reset[[:space:]]+--hard'  # Arbeitsstand verwerfen
  'git[[:space:]]+clean[[:space:]]+-[a-z]*f' # ungetrackte Dateien löschen
  'mkfs'                                     # Dateisystem formatieren
  'dd[[:space:]]+if=.*of=/dev/'              # rohe Disk-Writes
  '>[[:space:]]*/dev/sd'                     # direkt auf Block-Device schreiben
  ':\(\)\{.*\};:'                            # Fork-Bomb
  'chmod[[:space:]]+-R[[:space:]]+777'       # Rechte aufreißen
  # --- PowerShell-Destruktivmuster (Windows-Realität: Agent ruft ggf. powershell -c ...) ---
  'Remove-Item[[:space:]].*-Recurse.*-Force'  # rekursives Hard-Delete
  'Remove-Item[[:space:]].*-Force.*-Recurse'  # Reihenfolge umgekehrt
  '(^|[[:space:]])(rd|rmdir)[[:space:]]+/[sS]' # rd /s
  '(^|[[:space:]])del[[:space:]]+/[sS]'        # del /s
  'Format-Volume'                              # Volume formatieren
  'Clear-Disk'                                  # Disk leeren
  'Remove-Item[[:space:]]+.*\\\*'              # Wildcard-Delete
  'git[[:space:]]+push[[:space:]].*-Force'     # erzwungener Push (PS-Casing)
)

for pat in "${PATTERNS[@]}"; do
  if printf '%s' "$CMD" | grep -Eq "$pat"; then
    # stderr-Text erscheint für Claude und den Nutzer; Exit 2 blockt
    echo "BLOCKIERT durch Guardrail: Muster '$pat' im Befehl erkannt." >&2
    echo "Befehl: $CMD" >&2
    echo "Falls beabsichtigt, manuell im Terminal ausführen." >&2
    exit 2
  fi
done

exit 0
