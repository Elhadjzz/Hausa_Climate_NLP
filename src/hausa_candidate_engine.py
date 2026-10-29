"""Controlled provisional Hausa candidate-generation utilities.

This module documents the rule-based component of candidate drafting used
during HESTC development. It is intentionally conservative.

Output from this module must not be promoted automatically to Validated.
Human Hausa linguistic and environmental-domain review is required.
"""

from __future__ import annotations

import re

EXACT = {
    "climate": ("yanayi", "Existing Hausa technical term"),
    "climate change": ("sauyin yanayi", "Existing Hausa technical term"),
    "weather": ("yanayin sama", "Existing Hausa technical term"),
    "rain": ("ruwan sama", "Existing Hausa technical term"),
    "drought": ("fari", "Existing Hausa technical term"),
    "flood": ("ambaliya", "Existing Hausa technical term"),
    "environment": ("muhalli", "Existing Hausa technical term"),
    "biodiversity": ("bambancin halittu", "Direct equivalence"),
    "ecosystem": ("tsarin halittu", "Direct equivalence"),
    "renewable energy": ("makamashi mai sabuntawa", "Direct equivalence"),
    "early warning system": ("tsarin gargaɗin wuri", "Existing Hausa technical term"),
    "climate adaptation": ("daidaitawa da sauyin yanayi", "Direct equivalence"),
    "climate resilience": ("juriyar sauyin yanayi", "Direct equivalence"),
    "remote sensing": ("ganowa daga nesa", "Direct equivalence"),
    "machine learning": ("koyon na'ura", "Direct equivalence"),
    "artificial intelligence": ("basirar wucin gadi", "Direct equivalence"),
}

TOKEN_MAP = {
    "climate": "yanayi",
    "environmental": "muhalli",
    "environment": "muhalli",
    "risk": "haɗari",
    "monitoring": "sa ido",
    "management": "gudanarwa",
    "assessment": "tantancewa",
    "policy": "manufa",
    "law": "doka",
    "finance": "kuɗaɗe",
    "energy": "makamashi",
    "water": "ruwa",
    "soil": "ƙasa",
    "forest": "daji",
    "biodiversity": "bambancin halittu",
    "data": "bayanai",
    "model": "samfuri",
    "analysis": "bincike",
    "system": "tsari",
    "indicator": "mai nuna",
    "adaptation": "daidaitawa",
    "resilience": "juriya",
    "pollution": "gurɓatar muhalli",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def candidate_for(term: str) -> tuple[str, str]:
    """Return a provisional Hausa candidate and its strategy."""
    term = normalize(term)
    low = term.casefold()

    if low in EXACT:
        return EXACT[low]

    compositional = [
        (" management", lambda base: f"gudanar da {base}"),
        (" monitoring", lambda base: f"sa ido kan {base}"),
        (" assessment", lambda base: f"tantance {base}"),
        (" risk", lambda base: f"haɗarin {base}"),
        (" policy", lambda base: f"manufar {base}"),
        (" law", lambda base: f"dokar {base}"),
        (" finance", lambda base: f"kuɗaɗen {base}"),
        (" indicator", lambda base: f"mai nuna {base}"),
        (" system", lambda base: f"tsarin {base}"),
        (" model", lambda base: f"samfurin {base}"),
        (" analysis", lambda base: f"binciken {base}"),
    ]

    for suffix, formatter in compositional:
        if low.endswith(suffix) and len(low) > len(suffix):
            base_candidate, _ = candidate_for(term[: -len(suffix)])
            return formatter(base_candidate), "Hybrid translation"

    parts = re.split(r"(\W+)", term)
    translated = []
    lexical_tokens = 0
    mapped_tokens = 0

    for part in parts:
        if re.fullmatch(r"[A-Za-z]+", part):
            lexical_tokens += 1
            replacement = TOKEN_MAP.get(part.casefold())
            if replacement:
                mapped_tokens += 1
                translated.append(replacement)
            else:
                translated.append(part)
        else:
            translated.append(part)

    candidate = "".join(translated)

    if lexical_tokens and mapped_tokens == lexical_tokens:
        return candidate, "Direct equivalence"
    if mapped_tokens:
        return candidate, "Hybrid translation"

    if re.search(r"[A-Z]{2,}|\d|[-()/]", term):
        return term, "Borrowing/transliteration"

    return term, "Needs expert coinage"


if __name__ == "__main__":
    for example in [
        "climate change",
        "climate risk",
        "environmental monitoring",
        "synthetic aperture radar",
    ]:
        print(example, "=>", candidate_for(example))
