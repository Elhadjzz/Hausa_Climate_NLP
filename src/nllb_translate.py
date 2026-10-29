#!/usr/bin/env python3
"""English -> Hausa NLLB baseline and HESTC-constrained translation.

Uses direct model loading for current Transformers compatibility. HESTC
grounding uses lexical constraints during beam search. By default, only the
more conservative terminology strategies are eligible as constraints.

Constraints derived from candidate HESTC terminology remain provisional until
human validation.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

MODEL_DEFAULT = "facebook/nllb-200-distilled-600M"
DEFAULT_CONSTRAINT_STRATEGIES = {
    "Existing Hausa technical term",
    "Direct equivalence",
    "Descriptive translation",
}
SRC_LANG = "eng_Latn"
TGT_LANG = "hau_Latn"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_glossary(path: Path, include_hybrid: bool = False) -> list[dict[str, str]]:
    rows = load_csv(path)
    allowed = set(DEFAULT_CONSTRAINT_STRATEGIES)
    if include_hybrid:
        allowed.add("Hybrid translation")

    usable = []
    for row in rows:
        eng = norm(row.get("English term", ""))
        hau = norm(row.get("Hausa candidate", ""))
        if eng and hau and row.get("translation strategy") in allowed:
            usable.append(row)
    return sorted(usable, key=lambda r: len(r["English term"]), reverse=True)


def find_terms(text: str, glossary: list[dict[str, str]], max_terms: int = 3):
    lower = norm(text).casefold()
    hits = []
    occupied = []
    for row in glossary:
        eng = norm(row["English term"])
        match = re.search(r"(?<!\w)" + re.escape(eng.casefold()) + r"(?!\w)", lower)
        if not match:
            continue
        span = match.span()
        if any(not (span[1] <= a or span[0] >= b) for a, b in occupied):
            continue
        hits.append(row)
        occupied.append(span)
        if len(hits) >= max_terms:
            break
    return hits


def build_force_words_ids(tokenizer, hits):
    forced = []
    seen = set()
    for row in hits:
        term = norm(row["Hausa candidate"])
        if not term or term.casefold() in seen:
            continue
        ids = tokenizer(term, add_special_tokens=False).input_ids
        if ids:
            forced.append(ids)
            seen.add(term.casefold())
    return forced


def load_model(model_name: str, device: str | None = None):
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        src_lang=SRC_LANG,
        tgt_lang=TGT_LANG,
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    chosen = torch.device(device) if device else torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    model.to(chosen)
    model.eval()
    return tokenizer, model, chosen


def translate_one(
    text: str,
    tokenizer,
    model,
    device,
    *,
    force_terms=None,
    num_beams: int = 5,
    max_new_tokens: int = 128,
):
    import torch

    inputs = tokenizer(
        norm(text),
        return_tensors="pt",
        truncation=True,
        max_length=512,
    ).to(device)

    kwargs = dict(
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(TGT_LANG),
        max_new_tokens=max_new_tokens,
        do_sample=False,
    )

    if force_terms:
        force_words_ids = build_force_words_ids(tokenizer, force_terms)
        if force_words_ids:
            kwargs.update(
                force_words_ids=force_words_ids,
                num_beams=max(2, num_beams),
                early_stopping=True,
                custom_generate="transformers-community/constrained-beam-search",
                trust_remote_code=True,
                no_repeat_ngram_size=3,
                repetition_penalty=1.1,
            )

    with torch.inference_mode():
        output = model.generate(**inputs, **kwargs)
    return tokenizer.batch_decode(output, skip_special_tokens=True)[0]


def translate_batch(
    texts: list[str],
    tokenizer,
    model,
    device,
    *,
    max_new_tokens: int = 128,
):
    """Greedy batched translation for unconstrained baseline generation."""
    import torch

    inputs = tokenizer(
        [norm(text) for text in texts],
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512,
    ).to(device)

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(TGT_LANG),
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )
    return tokenizer.batch_decode(output, skip_special_tokens=True)


def translate_file(args):
    rows = load_csv(args.input)
    glossary = (
        load_glossary(args.corpus, include_hybrid=args.include_hybrid)
        if args.mode == "hestc_constrained"
        else []
    )
    tokenizer, model, device = load_model(args.model, args.device)

    output_rows = []

    if args.mode == "baseline" and args.batch_size > 1:
        for start in range(0, len(rows), args.batch_size):
            batch = rows[start : start + args.batch_size]
            sources = [norm(row[args.source_column]) for row in batch]
            translations = translate_batch(
                sources,
                tokenizer,
                model,
                device,
                max_new_tokens=args.max_new_tokens,
            )
            for row, translation in zip(batch, translations):
                record = dict(row)
                record["system"] = args.mode
                record["model"] = args.model
                record["translation"] = translation
                record["detected_hestc_ids"] = ""
                record["forced_hausa_terms"] = ""
                output_rows.append(record)
            done = min(start + len(batch), len(rows))
            print(f"Translated {done}/{len(rows)}")
    else:
        for i, row in enumerate(rows, start=1):
            source = norm(row[args.source_column])
            if args.mode == "hestc_constrained" and args.constraint_column:
                candidate = norm(row.get(args.constraint_column, ""))
                hits = [{
                    "ID": row.get("HESTC_ID", row.get("ID", "")),
                    "English term": row.get("English term", ""),
                    "Hausa candidate": candidate,
                    "translation strategy": row.get("translation strategy", ""),
                }] if candidate else []
            else:
                hits = find_terms(source, glossary, args.max_constraints) if glossary else []

            translation = translate_one(
                source,
                tokenizer,
                model,
                device,
                force_terms=hits,
                num_beams=args.num_beams,
                max_new_tokens=args.max_new_tokens,
            )
            record = dict(row)
            record["system"] = args.mode
            record["model"] = args.model
            record["translation"] = translation
            record["detected_hestc_ids"] = ";".join(r["ID"] for r in hits)
            record["forced_hausa_terms"] = ";".join(
                norm(r["Hausa candidate"]) for r in hits
            )
            output_rows.append(record)
            if i % 25 == 0:
                print(f"Translated {i}/{len(rows)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(output_rows[0].keys()) if output_rows else []
    with args.output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Wrote {len(output_rows)} translations to {args.output}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--mode", choices=["baseline", "hestc_constrained"], required=True)
    ap.add_argument("--source-column", default="English term")
    ap.add_argument("--model", default=MODEL_DEFAULT)
    ap.add_argument("--device", default=None, help="e.g. cpu, cuda, cuda:0")
    ap.add_argument("--num-beams", type=int, default=5)
    ap.add_argument("--max-new-tokens", type=int, default=128)
    ap.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Batch size for unconstrained baseline translation. Ignored for constrained decoding.",
    )
    ap.add_argument("--max-constraints", type=int, default=3)
    ap.add_argument(
        "--constraint-column",
        default=None,
        help="For benchmark rows, force only the Hausa term in this column instead of detecting all glossary terms",
    )
    ap.add_argument(
        "--include-hybrid",
        action="store_true",
        help="Allow provisional Hybrid translation candidates as lexical constraints",
    )
    args = ap.parse_args()
    translate_file(args)


if __name__ == "__main__":
    main()
