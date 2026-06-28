#!/usr/bin/env bash
# Extrahiert die PATTERNS aus dem Hook und testet sie gegen Beispielbefehle (jq-Layer übersprungen).
PATTERNS=(
  'rm[[:space:]]+-rf?[[:space:]]+/'
  'rm[[:space:]]+-rf?[[:space:]]+~'
  'rm[[:space:]]+-rf?[[:space:]]+\*'
  'git[[:space:]]+push[[:space:]].*--force'
  'git[[:space:]]+push[[:space:]].*-f([[:space:]]|$)'
  'git[[:space:]]+reset[[:space:]]+--hard'
  'git[[:space:]]+clean[[:space:]]+-[a-z]*f'
  'mkfs'
  'dd[[:space:]]+if=.*of=/dev/'
  '>[[:space:]]*/dev/sd'
  ':\(\)\{.*\};:'
  'chmod[[:space:]]+-R[[:space:]]+777'
  'Remove-Item[[:space:]].*-Recurse.*-Force'
  'Remove-Item[[:space:]].*-Force.*-Recurse'
  '(^|[[:space:]])(rd|rmdir)[[:space:]]+/[sS]'
  '(^|[[:space:]])del[[:space:]]+/[sS]'
  'Format-Volume'
  'Clear-Disk'
  'Remove-Item[[:space:]]+.*\\\*'
  'git[[:space:]]+push[[:space:]].*-Force'
)
blocks() { local cmd="$1"; for p in "${PATTERNS[@]}"; do printf '%s' "$cmd" | grep -Eq "$p" && return 0; done; return 1; }
t() { local cmd="$1"; local want="$2"; local desc="$3"
  if blocks "$cmd"; then got=BLOCK; else got=ALLOW; fi
  [ "$got" = "$want" ] && echo "  PASS [$got] $desc" || echo "  FAIL [erwartet $want, war $got] $desc"
}
echo "=== destruktiv → BLOCK ==="
t "rm -rf /" BLOCK "rm -rf /"
t "git push origin main --force" BLOCK "git push --force"
t "powershell -c Remove-Item C:\\data -Recurse -Force" BLOCK "PS Remove-Item -Recurse -Force"
t "powershell Format-Volume -DriveLetter D" BLOCK "PS Format-Volume"
t "cmd /c rd /s /q C:\\tmp" BLOCK "rd /s"
t "git reset --hard HEAD~3" BLOCK "git reset --hard"
t "git clean -fd" BLOCK "git clean -fd"
echo "=== harmlos → ALLOW ==="
t "ls -la" ALLOW "ls"
t "git status" ALLOW "git status"
t "git push origin main" ALLOW "git push (normal)"
t "powershell Remove-Item .\\tmp.txt" ALLOW "Remove-Item einzeln"
t "npm install" ALLOW "npm install"
