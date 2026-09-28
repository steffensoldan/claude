"""Erkennt Degenerations-Loops in ASR-Ausgaben (Whisper-Halluzinationen).

Whisper fällt bei informationsarmem Audio (überlappende Sprecher, Hall, Stille
mit hochgezogener AGC) in eine Wiederholungsschleife: ein Fragment wird bis zum
Ende des Zeitfensters wiederholt. Solche Segmente sind wertlos und dürfen nicht
als Protokolltext durchgehen.

Zwei Kriterien, beide sprachunabhängig:

1. Abdeckung: Wie viel Prozent der Tokens deckt das häufigste n-Gram ab?
   ">= 0.5" heißt: die Hälfte des Segments ist ein einziges wiederholtes Muster.
2. Type-Token-Ratio: unterschiedliche Tokens / alle Tokens. Kollabiert bei
   Loops gegen Null.

Reine Standardbibliothek. Direkt ausführbar für den Selbsttest:

    python loop_guard.py
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

_WORD = re.compile(r"\w+", re.UNICODE)

# Defaults: bewusst konservativ. Echte Rede wiederholt sich auch ("und dann
# kam es dann" darf zweimal vorkommen) - erst ein dominantes Muster ueber die
# halbe Laenge ist ein Loop.
COVERAGE_LIMIT = 0.50
TTR_LIMIT = 0.30
MIN_TOKENS = 12
MAX_N = 6


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _WORD.findall(text)]


@dataclass
class LoopVerdict:
    """Urteil über ein Segment."""

    degenerate: bool
    reason: str
    coverage: float          # Anteil der Tokens im häufigsten n-Gram
    type_token_ratio: float
    pattern: str             # das dominante Muster (zur Diagnose)
    tokens: int

    def __bool__(self) -> bool:  # if verdict: -> ist ein Loop
        return self.degenerate


def analyse(
    text: str,
    *,
    min_tokens: int = MIN_TOKENS,
    max_n: int = MAX_N,
    coverage_limit: float = COVERAGE_LIMIT,
    ttr_limit: float = TTR_LIMIT,
) -> LoopVerdict:
    """Prüft ein Segment auf Degeneration."""
    toks = tokenize(text)
    n_toks = len(toks)
    if n_toks == 0:
        return LoopVerdict(False, "leer", 0.0, 1.0, "", 0)

    ttr = len(set(toks)) / n_toks

    best_cov, best_pattern = 0.0, ""
    for n in range(1, min(max_n, n_toks) + 1):
        grams = [tuple(toks[i : i + n]) for i in range(n_toks - n + 1)]
        gram, count = Counter(grams).most_common(1)[0]
        if count < 2:
            continue
        coverage = min(1.0, count * n / n_toks)
        if coverage > best_cov:
            best_cov, best_pattern = coverage, " ".join(gram)

    # Kurze Segmente sind statistisch nicht beurteilbar - Ausnahme: ein
    # einziges Token, das sich mehrfach wiederholt ("ja ja ja ja").
    if n_toks < min_tokens and not (best_cov >= 0.8 and n_toks >= 4):
        return LoopVerdict(False, "zu kurz für Urteil", best_cov, ttr, best_pattern, n_toks)

    if best_cov >= coverage_limit:
        return LoopVerdict(
            True,
            f"Muster '{best_pattern}' deckt {best_cov:.0%} des Segments",
            best_cov, ttr, best_pattern, n_toks,
        )
    if ttr <= ttr_limit:
        return LoopVerdict(
            True,
            f"Type-Token-Ratio {ttr:.2f} <= {ttr_limit}",
            best_cov, ttr, best_pattern, n_toks,
        )
    return LoopVerdict(False, "unauffällig", best_cov, ttr, best_pattern, n_toks)


def collapse(text: str, max_n: int = 8) -> str:
    """Faltet unmittelbare Wiederholungen zusammen (Rettungsversuch).

    "und dann kam es dann und dann kam es dann" -> "und dann kam es dann".
    Rettet Segmente, in denen ein echter Inhalt nur vervielfacht wurde; bei
    vollständig halluzinierten Segmenten bleibt Müll übrig - deshalb immer
    zusätzlich analyse() prüfen.

    Nebenwirkung: arbeitet auf Wort-Tokens, Satzzeichen gehen verloren. Für den
    Rettungspfad hinnehmbar, für unauffällige Segmente nicht aufrufen.
    """
    words = _WORD.findall(text)
    if not words:
        return text.strip()

    out: list[str] = []
    i = 0
    while i < len(words):
        folded = False
        # Große n zuerst: sonst frisst n=1 Teile längerer Muster.
        for n in range(min(max_n, (len(words) - i) // 2), 0, -1):
            block = [w.lower() for w in words[i : i + n]]
            j = i + n
            repeats = 0
            while [w.lower() for w in words[j : j + n]] == block and block:
                repeats += 1
                j += n
            if repeats:
                out.extend(words[i : i + n])
                i = j
                folded = True
                break
        if not folded:
            out.append(words[i])
            i += 1
    return " ".join(out)


def _selftest() -> int:
    loop = (
        "...und dann kam es dann... " * 20
        + "dann kam es dann... dann... dann kam es dann..."
    )
    echt = (
        "Wir sollten die Förderlinie zuerst prüfen, bevor wir den Antrag "
        "aufsetzen. Und dann kam es dann doch zu einer Verschiebung des "
        "Termins, weil die Begutachtung länger gedauert hat."
    )
    kurz_loop = "ja ja ja ja ja"
    leise = "Vielen Dank."

    cases = [(loop, True), (echt, False), (kurz_loop, True), (leise, False)]
    failed = 0
    for text, expected in cases:
        v = analyse(text)
        mark = "ok " if v.degenerate == expected else "FEHL"
        if v.degenerate != expected:
            failed += 1
        print(
            f"{mark} degenerate={v.degenerate!s:5} cov={v.coverage:.2f} "
            f"ttr={v.type_token_ratio:.2f} tokens={v.tokens:3} | {v.reason}"
        )
    print("\ncollapse(loop) ->", collapse(loop)[:90])
    print("collapse(echt) ->", collapse(echt)[:90])
    return failed


if __name__ == "__main__":
    raise SystemExit(_selftest())
