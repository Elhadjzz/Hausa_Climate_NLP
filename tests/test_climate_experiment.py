import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_term_matching_is_case_and_punctuation_tolerant():
    ev = load_module(
        "evaluate_translation",
        ROOT / "src" / "evaluate_translation.py",
    )
    assert ev.contains_phrase(
        "Wannan ya shafi Sauyin Yanayi.",
        "sauyin yanayi",
    )


def test_glossary_finds_longer_term_first():
    tr = load_module(
        "nllb_translate",
        ROOT / "src" / "nllb_translate.py",
    )
    glossary = [
        {
            "ID": "1",
            "English term": "climate",
            "Hausa candidate": "yanayi",
            "translation strategy": "Direct equivalence",
        },
        {
            "ID": "2",
            "English term": "climate change",
            "Hausa candidate": "sauyin yanayi",
            "translation strategy": "Existing Hausa technical term",
        },
    ]
    glossary = sorted(
        glossary,
        key=lambda r: len(r["English term"]),
        reverse=True,
    )
    hits = tr.find_terms(
        "Climate change affects agriculture.",
        glossary,
        max_terms=3,
    )
    assert hits[0]["ID"] == "2"
    assert len(hits) == 1
