import json
from pathlib import Path

triples = json.loads(Path("data/processed/triples_raw.json").read_text(encoding="utf-8"))

manual_high_confidence = [
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

all_triples = triples + manual_high_confidence

seen = set()
dedup = []

for t in all_triples:
    key = (t["head"], t["relation"], t["tail"])
    if key not in seen:
        seen.add(key)
        dedup.append(t)

Path("data/processed/triples_final.json").write_text(
    json.dumps(dedup, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Final triples:", len(dedup))