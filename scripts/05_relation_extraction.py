import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if PROJECT_ROOT.name == "scripts":
    PROJECT_ROOT = PROJECT_ROOT.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

entities = json.loads((PROCESSED_DIR / "entities_normalized.json").read_text(encoding="utf-8"))

# 按句子聚合实体
sent_to_entities = {}

for e in entities:
    sent_to_entities.setdefault(e["sentence"], [])
    sent_to_entities[e["sentence"]].append(e)


RELATION_PATTERNS = [
    {
        "relation": "BORN_IN",
        "keywords": ["born in", "was born in"],
        "head_type": "Person",
        "tail_type": "Place"
    },
    {
        "relation": "DIED_IN",
        "keywords": ["died in", "died at"],
        "head_type": "Person",
        "tail_type": "Place"
    },
    {
        "relation": "STUDIED_AT",
        "keywords": ["studied at", "educated at", "student at"],
        "head_type": "Person",
        "tail_type": "Organization"
    },
    {
        "relation": "WORKED_AT",
        "keywords": ["worked at", "joined", "was at", "employed at"],
        "head_type": "Person",
        "tail_type": "Organization"
    },
    {
        "relation": "AUTHORED",
        "keywords": ["wrote", "published", "paper", "article", "authored"],
        "head_type": "Person",
        "tail_type": "Work"
    },
    {
        "relation": "PROPOSED",
        "keywords": ["proposed", "introduced", "described", "devised"],
        "head_type": "Person",
        "tail_type": "Concept"
    },
    {
        "relation": "DESIGNED",
        "keywords": ["designed", "design", "developed"],
        "head_type": "Person",
        "tail_type": "Machine"
    },
    {
        "relation": "CONTRIBUTED_TO",
        "keywords": ["contributed to", "contribution", "foundations of", "pioneer"],
        "head_type": "Person",
        "tail_type": "Field"
    },
    {
        "relation": "RELATED_TO",
        "keywords": ["related to", "associated with", "concerned with", "central to"],
        "head_type": None,
        "tail_type": None
    },
]

MANUAL_HIGH_CONFIDENCE = [
    {
        "head": "Alan Turing",
        "head_label": "Person",
        "relation": "PROPOSED",
        "tail": "Turing Machine",
        "tail_label": "Concept",
        "sentence": "Turing machines were first described by Alan Turing in 1936-7.",
        "source": "domain_rule",
        "confidence": 0.95,
        "method": "curated_rule"
    },
    {
        "head": "Alan Turing",
        "head_label": "Person",
        "relation": "PROPOSED",
        "tail": "Turing Test",
        "tail_label": "Concept",
        "sentence": "Turing introduced the imitation game, later known as the Turing Test.",
        "source": "domain_rule",
        "confidence": 0.95,
        "method": "curated_rule"
    },
    {
        "head": "Alan Turing",
        "head_label": "Person",
        "relation": "WORKED_AT",
        "tail": "Bletchley Park",
        "tail_label": "Organization",
        "sentence": "Turing worked at Bletchley Park during World War II.",
        "source": "domain_rule",
        "confidence": 0.95,
        "method": "curated_rule"
    },
    {
        "head": "Alan Turing",
        "head_label": "Person",
        "relation": "DESIGNED",
        "tail": "Automatic Computing Engine",
        "tail_label": "Machine",
        "sentence": "Turing designed the Automatic Computing Engine at the National Physical Laboratory.",
        "source": "domain_rule",
        "confidence": 0.95,
        "method": "curated_rule"
    },
    {
        "head": "Turing Machine",
        "head_label": "Concept",
        "relation": "RELATED_TO",
        "tail": "Computability",
        "tail_label": "Concept",
        "sentence": "Turing machines are abstract computational devices used to investigate what can be computed.",
        "source": "domain_rule",
        "confidence": 0.95,
        "method": "curated_rule"
    },
]


def sentence_has_keyword(sentence: str, keywords: list[str]) -> bool:
    s = sentence.lower()
    return any(k in s for k in keywords)


def extract_relations_from_sentence(sentence: str, ents: list[dict]) -> list[dict]:
    triples = []
    unique_ents = {}
    for e in ents:
        unique_ents[e["canonical_name"]] = e

    ent_list = list(unique_ents.values())

    for pattern in RELATION_PATTERNS:
        if not sentence_has_keyword(sentence, pattern["keywords"]):
            continue

        for h in ent_list:
            for t in ent_list:
                if h["canonical_name"] == t["canonical_name"]:
                    continue

                if pattern["head_type"] and h["label"] != pattern["head_type"]:
                    continue
                if pattern["tail_type"] and t["label"] != pattern["tail_type"]:
                    continue

                # 简单方向控制：头实体在句子中尽量出现在尾实体之前
                h_pos = sentence.lower().find(h["mention"].lower())
                t_pos = sentence.lower().find(t["mention"].lower())
                if h_pos != -1 and t_pos != -1 and h_pos > t_pos:
                    continue

                triples.append({
                    "head": h["canonical_name"],
                    "head_label": h["label"],
                    "relation": pattern["relation"],
                    "tail": t["canonical_name"],
                    "tail_label": t["label"],
                    "sentence": sentence,
                    "source": h["source"],
                    "confidence": 0.75,
                    "method": "rule"
                })

    return triples


triples = []

for sent, ents in sent_to_entities.items():
    triples.extend(extract_relations_from_sentence(sent, ents))

# 去重
seen = set()
dedup = []

for t in triples:
    key = (t["head"], t["relation"], t["tail"])
    if key not in seen:
        seen.add(key)
        dedup.append(t)

(PROCESSED_DIR / "triples_raw.json").write_text(
    json.dumps(dedup, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

all_triples = dedup + MANUAL_HIGH_CONFIDENCE

seen = set()
final_triples = []

for t in all_triples:
    key = (t["head"], t["relation"], t["tail"])
    if key not in seen:
        seen.add(key)
        final_triples.append(t)

(PROCESSED_DIR / "triples_final.json").write_text(
    json.dumps(final_triples, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Triples:", len(dedup))
print("Final triples:", len(final_triples))
