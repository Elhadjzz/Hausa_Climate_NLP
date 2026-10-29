import csv
import gzip
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[1]
CORPUS_GZ = ROOT / "data" / "HESTC10K_master.csv.gz"
CORPUS_CSV = ROOT / "data" / "HESTC10K_master.csv"


def load():
    if CORPUS_CSV.exists():
        handle = CORPUS_CSV.open("r", encoding="utf-8-sig", newline="")
    else:
        handle = gzip.open(CORPUS_GZ, "rt", encoding="utf-8-sig", newline="")
    with handle:
        return list(csv.DictReader(handle))


def normalize(value):
    return re.sub(r"\s+", " ", (value or "").strip()).casefold()


def test_record_count():
    assert len(load()) == 11034


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


def test_hausa_candidates_complete():
    assert all(row["Hausa candidate"].strip() for row in load())


def test_current_status_is_candidate_drafted():
    assert set(row["validation status"] for row in load()) == {"Candidate drafted"}
