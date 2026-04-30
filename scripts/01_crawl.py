import requests
import trafilatura
from bs4 import BeautifulSoup
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if PROJECT_ROOT.name == "scripts":
    PROJECT_ROOT = PROJECT_ROOT.parent

URLS = [
    # "https://www.britannica.com/biography/Alan-Turing",
    # 这个网站有反爬虫机制，暂时放弃
    "https://en.wikipedia.org/wiki/Alan_Turing",        
    "https://plato.stanford.edu/entries/turing-machine/",
    "https://plato.stanford.edu/entries/turing/",
    "https://turingarchive.kings.cam.ac.uk/node/2",
]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_text(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 KnowledgeGraphCourseProject/1.0"
    }
    html = requests.get(url, headers=headers, timeout=20).text

    text = trafilatura.extract(html)
    if not text:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n")

    return text or ""


for i, url in enumerate(URLS, start=1):
    print(f"Fetching {url}")
    text = fetch_text(url)
    file = RAW_DIR / f"source_{i}.txt"
    file.write_text(text, encoding="utf-8")
    print(f"Saved {file}, length={len(text)}")
