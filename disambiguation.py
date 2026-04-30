import json
import re
from pathlib import Path
from rapidfuzz import process, fuzz

ALIASES = {
    "Alan Mathison Turing": "Alan Turing",
    "Turing": "Alan Turing",
    "A. M. Turing": "Alan Turing",
    "AMT": "Alan Turing",
    "King's College": "King's College Cambridge",
    "King's College, Cambridge": "King's College Cambridge",
    "NPL": "National Physical Laboratory",
    "the National Physical Laboratory": "National Physical Laboratory",
    "ACE": "Automatic Computing Engine",
    "the Bombe": "Bombe",
    "Bombe machine": "Bombe",
    "the Enigma": "Enigma",
    "Enigma machine": "Enigma",
    "the imitation game": "Turing Test",
    "Imitation Game": "Turing Test",
}

CANONICAL_TYPES = {
    "Alan Turing": "Person",
    "Alonzo Church": "Person",
    "Joan Clarke": "Person",
    "Max Newman": "Person",
    "Gordon Welchman": "Person",

    "King's College Cambridge": "Organization",
    "Bletchley Park": "Organization",
    "National Physical Laboratory": "Organization",
    "Princeton University": "Organization",
    "University of Cambridge": "Organization",

    "London": "Place",
    "Cambridge": "Place",
    "Wilmslow": "Place",

    "Turing Machine": "Concept",
    "Universal Turing Machine": "Concept",
    "Turing Test": "Concept",
    "Computability": "Concept",
    "Halting Problem": "Concept",
    "Church-Turing Thesis": "Concept",

    "Artificial Intelligence": "Field",
    "Computer Science": "Field",
    "Cryptanalysis": "Field",

    "Bombe": "Machine",
    "Enigma": "Machine",
    "Automatic Computing Engine": "Machine",

    "On Computable Numbers": "Work",
    "Computing Machinery and Intelligence": "Work",
    "Systems of Logic Based on Ordinals": "Work",
}


def normalize_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    name = name.strip(" ,.;:()[]{}\"'")
    return ALIASES.get(name, name)


def context_disambiguate(name: str, label: str, sentence: str) -> tuple[str, str] | None:
    name = normalize_name(name)
    s = sentence.lower()

    # 过滤明显噪声
    if len(name) <= 1:
        return None

    # Church 消歧
    if name == "Church":
        if "lambda" in s or "computability" in s or "turing" in s:
            return "Alonzo Church", "Person"
        return None

    # Turing Machine 不是 Machine，而是 Concept
    if name.lower() in {"turing machine", "universal turing machine"}:
        return name, "Concept"

    # ACE 消歧
    if name == "Automatic Computing Engine":
        if "computer" in s or "npl" in s or "engine" in s:
            return name, "Machine"

    if name in CANONICAL_TYPES:
        return name, CANONICAL_TYPES[name]

    return name, label


raw_entities = json.loads(Path("data/processed/entities_raw.json").read_text(encoding="utf-8"))

normalized = []

for e in raw_entities:
    result = context_disambiguate(e["name"], e["label"], e["sentence"])
    if result is None:
        continue

    cname, clabel = result

    normalized.append({
        "name": cname,
        "label": clabel,
        "source": e["source"],
        "sentence": e["sentence"],
        "mention": e["name"],
        "method": e["method"]
    })

# 模糊合并：只对未知但相似的名称做辅助，不要完全依赖
known_names = list(CANONICAL_TYPES.keys())

for e in normalized:
    match = process.extractOne(e["name"], known_names, scorer=fuzz.WRatio)
    if match and match[1] >= 92:
        e["canonical_name"] = match[0]
        e["label"] = CANONICAL_TYPES[match[0]]
    else:
        e["canonical_name"] = e["name"]

Path("data/processed/entities_normalized.json").write_text(
    json.dumps(normalized, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Normalized entity mentions:", len(normalized))
print("Unique entities:", len(set(e["canonical_name"] for e in normalized)))