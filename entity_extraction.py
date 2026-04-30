import json
import spacy
from pathlib import Path
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")

DOMAIN_TERMS = {
    "Turing Machine": "Concept",
    "Universal Turing Machine": "Concept",
    "Turing Test": "Concept",
    "Imitation Game": "Concept",
    "Computability": "Concept",
    "Halting Problem": "Concept",
    "Church-Turing Thesis": "Concept",
    "Artificial Intelligence": "Field",
    "Cryptanalysis": "Field",
    "Computer Science": "Field",
    "Enigma": "Machine",
    "Bombe": "Machine",
    "ACE": "Machine",
    "Automatic Computing Engine": "Machine",
    "On Computable Numbers": "Work",
    "Computing Machinery and Intelligence": "Work",
    "Systems of Logic Based on Ordinals": "Work",
    "Bletchley Park": "Organization",
    "King's College": "Organization",
    "King's College Cambridge": "Organization",
    "National Physical Laboratory": "Organization",
    "Princeton University": "Organization",
    "University of Cambridge": "Organization",
    "Alan Turing": "Person",
    "Alonzo Church": "Person",
    "Joan Clarke": "Person",
    "Max Newman": "Person",
    "Gordon Welchman": "Person",
}

matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(term) for term in DOMAIN_TERMS]
matcher.add("DOMAIN_TERMS", patterns)


def map_spacy_label(label: str) -> str:
    mapping = {
        "PERSON": "Person",
        "ORG": "Organization",
        "GPE": "Place",
        "LOC": "Place",
        "WORK_OF_ART": "Work",
        "EVENT": "Event",
    }
    return mapping.get(label, "Entity")


sentences = json.loads(Path("data/processed/sentences.json").read_text(encoding="utf-8"))

entities = []

for item in sentences:
    sent = item["sentence"]
    doc = nlp(sent)

    # spaCy 通用实体
    for ent in doc.ents:
        label = map_spacy_label(ent.label_)
        if label != "Entity":
            entities.append({
                "name": ent.text.strip(),
                "label": label,
                "source": item["source"],
                "sentence": sent,
                "method": "spacy"
            })

    # 领域词典实体
    matches = matcher(doc)
    for _, start, end in matches:
        span = doc[start:end]
        name = span.text.strip()
        canonical = next(
            term for term in DOMAIN_TERMS
            if term.lower() == name.lower()
        )
        entities.append({
            "name": canonical,
            "label": DOMAIN_TERMS[canonical],
            "source": item["source"],
            "sentence": sent,
            "method": "dictionary"
        })

Path("data/processed/entities_raw.json").write_text(
    json.dumps(entities, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Raw entity mentions:", len(entities))