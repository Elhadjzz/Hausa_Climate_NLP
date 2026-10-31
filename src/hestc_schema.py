"""Controlled schema and vocabularies for HESTC-10K."""

SCHEMA = [
    "ID",
    "English term",
    "Hausa term (Google Translate)",
    "synonym/abbreviation",
    "terminology type",
    "domain",
    "subdomain",
    "concise definition",
    "source institution",
    "source identifier/link",
    "Hausa candidate",
    "translation strategy",
    "preferred Hausa",
    "validation status",
    "reviewer notes",
]

TERMINOLOGY_TYPES = {
    "Scientific",
    "Technical",
    "Policy",
    "Legal/governance",
    "Operational",
    "Economic/finance",
    "Social/development",
}

TRANSLATION_STRATEGIES = {
    "Deferred — English-source curation phase",
    "Direct equivalence",
    "Descriptive translation",
    "Borrowing/transliteration",
    "Hybrid translation",
    "Existing Hausa technical term",
    "Needs expert coinage",
}

VALIDATION_STATUSES = {
    "Not translated",
    "Candidate drafted",
    "Under linguistic review",
    "Under domain review",
    "Validated",
    "Rejected/revise",
}

DOMAIN_PREFIXES = {
    "Climate, Meteorology & Atmospheric Science": "CMA",
    "Water, Hydrology & Sanitation": "WHS",
    "Land, Soil, Drought & Desertification": "LSDD",
    "Biodiversity, Ecology & Conservation": "BEC",
    "Forestry, Agriculture & Natural Resources": "FANR",
    "Pollution, Chemicals, Waste & Circular Economy": "PCWCE",
    "Energy, Emissions & Environmental Technology": "EET",
    "Disaster Risk, Adaptation & Resilience": "DRA",
    "Environmental Policy, Law, Governance & Finance": "EPLGF",
    "Environmental Monitoring, GIS, Remote Sensing & Scientific Methods": "MGRSM",
}
