import spacy
from pathlib import Path
import json

nlp = spacy.load("en_core_web_sm")

PROJECT_ROOT = Path(__file__).resolve().parent
if PROJECT_ROOT.name == "scripts":
    PROJECT_ROOT = PROJECT_ROOT.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

sentences = []

for file in RAW_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    doc = nlp(text)

    for sent in doc.sents:
        s = sent.text.strip()
        if len(s) > 30:
            sentences.append({
                "source": file.name,
                "sentence": s
            })

(PROCESSED_DIR / "sentences.json").write_text(
    json.dumps(sentences, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Sentence count:", len(sentences))
