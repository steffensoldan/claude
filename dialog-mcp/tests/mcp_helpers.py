"""Testhelfer fuer dialog-mcp.

Eigener Modulname statt `conftest`, damit ein `pytest` im Repo-Wurzelverzeichnis
nicht die conftest der Schwesterprojekte erwischt.
"""

def valid_matrix(gate: str = "bestanden") -> dict:
    cell = {"rating": "gut", "note": "geprueft"}
    m = {d: dict(cell) for d in ("sicherheit", "robustheit", "wartbarkeit", "usability")}
    m["compliance"] = {"rating": "gut", "note": "kein Datenabfluss", "gate": gate}
    return m


def valid_post(**overrides) -> dict:
    payload = {
        "body": "Ein Beitrag mit Substanz.",
        "evidence": [{"path": "src/app.py", "locator": "Zeile 12"}],
        "objections": [
            {
                "claim": "Der Hardlink driftet unter NTFS.",
                "reasoning": "Ein Update ersetzt die Datei und erzeugt einen neuen inode.",
                "retract_if": "ein Hash-Vergleich zeigt nach dem Update Gleichheit",
            }
        ],
        "priorities": {"dimensions": ["robustheit"], "sacrifice": "Ich gebe die einfachere Installation auf."},
        "matrix": valid_matrix(),
    }
    payload.update(overrides)
    return payload


def valid_residual() -> dict:
    return {
        "difference": "Ob der Loesungsraum vorab klassifizierbar ist.",
        "why_unresolvable": "Beide Positionen sind widerspruchsfrei und unterscheiden sich nur empirisch.",
        "measurement": "k Sonden je Aufgabe, Artefakt-Divergenz gegen verifizierte Korrektheit.",
    }
