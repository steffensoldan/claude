# CLAUDE.md (AOS - Agentic Operating System)

This file provides workspace-specific guidelines for Claude Code when working in the AOS repository.

## Global Rules
@memory/global-rules.md

## Repository Overview
The Agentic Operating System (AOS) is a private, lightweight system for managing agent environments, documentation, custom slash-commands, hooks, and active project workspaces.

- **`commands/`**: Slash-commands for Claude Code (e.g., sync, git-init, entscheidungsvorlage).
- **`dialog/`**: Dialogue history templates and active threads.
- **`hooks/`**: Claude Code safety hooks (e.g., `block-dangerous.sh`).
- **`memory/`**: Global rules and behavioral instructions.
- **`ops/`**: Deployment and operations scripts.
- **`projects/`**: Workspaces for various projects.
- **`scripts/`**: Automation scripts (e.g., skill registration).

## Common Commands

```powershell
# Install/Update AOS on the current system (idempotent symlinks & rules)
powershell .\install.ps1

# Export a clean, secret-free AOS package to ZIP for mobile/VM migration
powershell .\export-aos.ps1

# Run the deployment script for a project (based on deploy-manifest.json)
powershell .\ops\deploy.ps1 -ManifestPath <path> -TargetDir <path>
```
