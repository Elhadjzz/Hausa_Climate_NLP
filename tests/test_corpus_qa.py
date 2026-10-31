import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[1]
MASTER = ROOT / "data" / "HESTC10K_master.csv"
PART_DIR = ROOT / "data" / "corpus_parts"

PART_FILES = [
    "Part1A_Terms.csv", "Part1B_Terms.csv", "Part1C_Terms.csv",
    "Part2A_Terms.csv", "Part2B_Terms.csv", "Part2C_Terms.csv",
    "Part3A_Terms.csv", "Part3B_Terms.csv", "Part3C_Terms.csv",
    "Part4A_Terms.csv", "Part4B_Terms.csv", "Part4C_Terms.csv",
    "Part5A_Terms.csv", "Part5B_Terms.csv",
    "Part6A_Terms.csv", "Part6B_Terms.csv",
    "Part7A_Terms.csv", "Part7B_Terms.csv",
    "Part8A_Terms.csv", "Part8B_Terms.csv",
    "Part9A_Terms.csv", "Part9B_Terms.csv",
    "Part10A_Terms.csv", "Part10B_Terms.csv",
]


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load():
    if MASTER.exists():
        return read_csv(MASTER)

    rows = []
    for filename in PART_FILES:
        rows.extend(read_csv(PART_DIR / filename))
    return rows


def normalize(value):
    return re.sub(r"\s+", " ", (value or "").strip()).casefold()


def test_record_count():
    assert len(load()) == 11034


def test_no_duplicate_ids():
    ids = [row["ID"].strip() for row in load()]
    assert not [key for key, count in Counter(ids).items() if count > 1]


def test_no_duplicate_preferred_english_labels():
    terms = [normalize(row["English term"]) for row in load()]
    assert not [term for term, count in Counter(terms).items() if count > 1]


def test_definitions_complete():
    assert all(row["concise definition"].strip() for row in load())


def test_source_links_complete():
    assert all(
        row["source identifier/link"].startswith(("http://", "https://"))
        for row in load()
    )


def test_hausa_terms_complete():
    assert all(row["Hausa term"].strip() for row in load())


def test_hausa_candidates_complete():
    assert all(row["Hausa candidate"].strip() for row in load())


def test_current_status_is_candidate_drafted():
    assert set(row["validation status"] for row in load()) == {"Candidate drafted"}


def test_review_priority_count():
    assert sum(
        row["translation strategy"] == "Needs expert coinage"
        for row in load()
    ) == 1965


def test_agroforestry_buffer_definition_present():
    rows = load()
    row = next(r for r in rows if r["ID"] == "HESTC-FANR-0167")
    assert row["English term"] == "agroforestry buffer"
    assert row["concise definition"].strip() == (
        "Agroforestry strip designed to intercept pollutants, "
        "reduce erosion or connect habitats."
    )
