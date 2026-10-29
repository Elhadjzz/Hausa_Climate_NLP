#!/usr/bin/env python3
"""Create Hausa machine pretranslations for reviewer assistance.

These drafts are NOT human references and MUST NOT be used as gold-standard
BLEU/chrF targets without independent human correction and domain review.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

CONTEXT_HA = {
    "seasonal forecasting and early-warning services": "hasashen yanayi na kaka da ayyukan gargaɗin wuri",
    "climate monitoring and weather-risk communication": "sa ido kan sauyin yanayi da sadar da haɗarin yanayin sama",
    "forecast verification and climate-service delivery": "tabbatar da ingancin hasashe da isar da ayyukan yanayi",
    "preparedness for extreme weather and climate variability": "shiri don matsanancin yanayin sama da sauye-sauyen yanayi",
    "drought preparedness and water-security planning": "shirin fari da tsara tsaron ruwa",
    "flood management and freshwater-resource protection": "sarrafa ambaliya da kare albarkatun ruwan zaƙi",
    "safe water services under changing climate conditions": "ayyukan ruwa mai aminci a ƙarƙashin sauyin yanayi",
    "climate-resilient water and sanitation management": "sarrafa ruwa da tsaftar muhalli mai jure sauyin yanayi",
    "drought resilience and sustainable land management": "juriyar fari da dorewar sarrafa ƙasa",
    "soil protection and land-restoration programmes": "kare ƙasa da shirye-shiryen maido da ƙasa",
    "desertification control and climate adaptation": "shawo kan hamadar ƙasa da daidaitawa da sauyin yanayi",
    "productive landscapes under increasing climate stress": "shimfidar ƙasa mai amfani a ƙarƙashin ƙarin matsin sauyin yanayi",
    "species conservation and protected-area planning": "kiyaye nau'o'in halittu da tsara yankunan kariya",
    "ecosystem restoration and climate-impact assessment": "maido da tsarin halittu da tantance tasirin sauyin yanayi",
    "habitat protection and biodiversity monitoring": "kare muhallin halittu da sa ido kan bambancin halittu",
    "nature-based adaptation and ecological resilience": "daidaitawa bisa yanayi da juriyar tsarin halittu",
    "climate-smart agriculture and food-security planning": "noma mai la'akari da sauyin yanayi da tsara tsaron abinci",
    "forest management and climate adaptation": "sarrafa daji da daidaitawa da sauyin yanayi",
    "sustainable natural-resource management": "dorewar sarrafa albarkatun ƙasa",
    "agricultural resilience to changing rainfall and temperature": "juriyar noma ga sauyin ruwan sama da zafi",
    "pollution prevention and climate-resilient environmental services": "rigakafin gurɓatar muhalli da ayyukan muhalli masu jure sauyin yanayi",
    "chemical safety and environmental-health protection": "amincin sinadarai da kare lafiyar muhalli",
    "waste management and circular-economy planning": "sarrafa sharar gida da tsara tattalin arzikin zagaye",
    "control of environmental contamination under climate stress": "sarrafa gurɓatar muhalli a ƙarƙashin matsin sauyin yanayi",
    "low-carbon development and energy-transition planning": "ci gaba mai ƙarancin carbon da tsara sauyin tsarin makamashi",
    "emissions reduction and climate-mitigation policy": "rage fitar hayaki da manufar rage sauyin yanayi",
    "renewable-energy deployment and system resilience": "aiwatar da makamashi mai sabuntawa da juriyar tsarin makamashi",
    "climate-resilient environmental technology": "fasahar muhalli mai jure sauyin yanayi",
    "climate adaptation and disaster-risk reduction": "daidaitawa da sauyin yanayi da rage haɗarin bala'i",
    "community preparedness and early warning": "shirin al'umma da gargaɗin wuri",
    "resilience planning for climate-related hazards": "tsara juriya ga haɗurran da suka shafi sauyin yanayi",
    "recovery and risk-informed development": "farfaɗowa da ci gaban da ya dogara da bayanan haɗari",
    "climate governance and environmental policy": "shugabancin sauyin yanayi da manufar muhalli",
    "adaptation finance and accountable decision-making": "kuɗaɗen daidaitawa da yanke shawara cikin gaskiya da alhaki",
    "environmental law and climate-policy implementation": "dokar muhalli da aiwatar da manufar sauyin yanayi",
    "public investment for resilient and low-carbon development": "jarin jama'a don ci gaba mai juriya da ƙarancin carbon",
    "Earth observation and environmental monitoring": "lura da Duniya da sa ido kan muhalli",
    "spatial analysis for climate-risk assessment": "nazarin sarari don tantance haɗarin sauyin yanayi",
    "remote sensing of environmental change": "ganowa daga nesa na sauyin muhalli",
    "scientific evidence for climate and ecosystem decisions": "hujjojin kimiyya don yanke shawara kan yanayi da tsarin halittu",
}


def read(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def context_for(sentence: str) -> str:
    for english in sorted(CONTEXT_HA, key=len, reverse=True):
        if english in sentence:
            return CONTEXT_HA[english]
    raise ValueError(f"Could not identify benchmark context: {sentence}")


def draft(sentence: str, term_ha: str) -> str:
    ctx = context_for(sentence)
    t = term_ha.strip()

    if sentence.startswith("The category "):
        return f"Ana amfani da rukunin {t} wajen tantance matsayin nau'in halittu a cikin {ctx}."
    if sentence.startswith("Reliable information on "):
        return f"Ingantaccen bayani kan {t} yana tallafa wa {ctx}."
    if sentence.startswith("Decision-makers consider "):
        return f"Masu yanke shawara suna la'akari da {t} yayin tsara {ctx}."
    if sentence.startswith("Monitoring "):
        return f"Sa ido kan {t} na iya ƙarfafa {ctx}."
    if sentence.startswith("Understanding "):
        return f"Fahimtar {t} tana taimaka wa masu aiwatarwa inganta {ctx}."
    if sentence.startswith("Assessments of "):
        return f"Tantance {t} yana samar da hujjoji don {ctx}."
    if sentence.startswith("Changes in "):
        return f"Sauye-sauye a {t} na iya shafar shawarwarin da suka shafi {ctx}."
    if sentence.startswith("Field programmes track "):
        return f"Shirye-shiryen aiki a fili suna bibiyar {t} don tallafa wa {ctx}."
    if sentence.startswith("Researchers analyse "):
        return f"Masu bincike suna nazarin {t} yayin tantance {ctx}."
    if sentence.startswith("Information about "):
        return f"Bayani game da {t} na iya tallafa wa {ctx}."
    if sentence.startswith("Effective management of "):
        return f"Ingantaccen sarrafa {t} na iya taimakawa ga {ctx}."
    if sentence.startswith("Public agencies use data on "):
        return f"Hukumomin gwamnati suna amfani da bayanai kan {t} don jagorantar {ctx}."
    if " is relevant to decisions about " in sentence:
        return f"{t} yana da muhimmanci ga shawarwari game da {ctx}."
    if sentence.startswith("Planning teams evaluate "):
        return f"Ƙungiyoyin tsare-tsare suna tantance {t} yayin samar da dabarun {ctx}."
    if sentence.startswith("Evidence about "):
        return f"Hujjoji game da {t} na iya inganta {ctx}."
    if sentence.startswith("Technical specialists document "):
        return f"Kwararrun fasaha suna rubuta bayanai kan {t} don ba da haske ga {ctx}."
    if sentence.startswith("Institutions may consider "):
        return f"Cibiyoyi na iya la'akari da {t} yayin tsara shirye-shiryen {ctx}."

    raise ValueError(f"Unknown benchmark template: {sentence}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind", type=Path, required=True)
    ap.add_argument("--key", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    blind = read(args.blind)
    key = {r["sentence_id"]: r for r in read(args.key)}

    rows = []
    for b in blind:
        k = key[b["sentence_id"]]
        rows.append({
            "sentence_id": b["sentence_id"],
            "english_sentence": b["english_sentence"],
            "HESTC_ID": b["HESTC_ID"],
            "English term": b["English term"],
            "provisional Hausa candidate": k["provisional Hausa candidate"],
            "translation strategy": k["translation strategy"],
            "machine_hausa_pretranslation": draft(
                b["english_sentence"],
                k["provisional Hausa candidate"],
            ),
            "domain": b["domain"],
            "subdomain": b["subdomain"],
            "split": b["split"],
            "source institution": b["source institution"],
            "source identifier/link": b["source identifier/link"],
            "draft_status": "AI-assisted machine pretranslation; NOT a gold reference",
            "reviewer_correction": "",
            "reviewer_notes": "",
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} machine pretranslations to {args.out}")


if __name__ == "__main__":
    main()
