"""Testhelfer fuer dialog-lite.

Eigener Modulname statt `conftest`, damit ein `pytest` im Repo-Wurzelverzeichnis
nicht die conftest der Schwesterprojekte erwischt.
"""

# Bewusst nicht "claude"/"antigravity": faellt auf, falls sich irgendwo eine
# Annahme ueber die Beteiligten einschleicht.
A, B = "alpha", "beta"


def obj(claim="Das driftet.", retract_if="ein Hash-Vergleich Gleichheit zeigt"):
    return [{"claim": claim, "retract_if": retract_if}]
