"""Rendert den Quarto-Hausdienst auf der VM und veröffentlicht die Ausgaben
unter dem vom Web-Dienst bedienten Pfad (/wisskomm/pub/<slug>/).

Konfiguration ausschließlich über Umgebungsvariablen (siehe .env.example) — keine
Zugangsdaten oder systemspezifischen Pfade im Quellcode.

Aufruf:
    python publish_quarto.py
"""
import os
import sys
import paramiko
from dotenv import load_dotenv

load_dotenv()


def run(ssh, cmd, timeout=600):
    _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    status = stdout.channel.recv_exit_status()
    return status, (out + err).strip()


def main():
    server = os.environ.get("WISSKOMM_VM_HOST")
    user = os.environ.get("WISSKOMM_VM_USER")
    password = os.environ.get("WISSKOMM_VM_PASSWORD")
    remote_dir = os.environ.get("WISSKOMM_VM_REMOTE_DIR", "/home/sts/wisskomm-viz")
    quarto_dir = os.environ.get("WISSKOMM_QUARTO_DIR", "/home/sts/wisskomm-quarto-pilot")
    quarto_bin = os.environ.get("WISSKOMM_QUARTO_BIN", "/home/sts/opt/quarto-1.9.38/bin/quarto")

    missing = [k for k, v in {
        "WISSKOMM_VM_HOST": server, "WISSKOMM_VM_USER": user, "WISSKOMM_VM_PASSWORD": password,
    }.items() if not v]
    if missing:
        print("FEHLER: Fehlende Umgebungsvariablen: " + ", ".join(missing))
        print("Bitte .env aus .env.example anlegen und befüllen.")
        sys.exit(1)

    publish_dir = f"{remote_dir}/published"
    venv_python = f"{quarto_dir}/.venv/bin/python"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Verbinde mit {server}...")
    try:
        ssh.connect(server, 22, user, password, timeout=15)
    except Exception as e:
        print(f"Verbindung fehlgeschlagen: {e}")
        sys.exit(1)

    # 1. Quarto-Projekt rendern (venv als Python-Engine)
    print("Rendere Quarto-Projekt (alle Formate)...")
    render_cmd = (
        f"export QUARTO_PYTHON={venv_python}; "
        f"cd {quarto_dir} && {quarto_bin} render 2>&1"
    )
    status, out = run(ssh, render_cmd, timeout=600)
    print(out[-2000:])
    if status != 0:
        print("FEHLER: Quarto-Render fehlgeschlagen.")
        ssh.close()
        sys.exit(1)

    # 2. Ausgaben in den bedienten Ordner synchronisieren
    print("Veröffentliche Ausgaben nach", publish_dir)
    run(ssh, f"mkdir -p {publish_dir}")
    status, out = run(ssh, f"cp -r {quarto_dir}/_site/publications/. {publish_dir}/ && echo OK")
    print(out)

    # 3. Verifizieren
    status, out = run(ssh, f"ls -1 {publish_dir}")
    print("Veröffentlichte Slugs:", out.split())
    ssh.close()
    print("\nFertig. Erreichbar unter: http://<host>:8080/wisskomm/pub/<slug>/")


if __name__ == "__main__":
    main()
