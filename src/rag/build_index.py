\
import os, json, re, pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_DIR / "raw"
INDEX_PATH = DATA_DIR / "tfidf_index.pkl"

def load_corpus():
    programs = json.loads((DATA_DIR / "programs.json").read_text(encoding="utf-8"))
    docs = []
    meta = []
    for p in programs["programs"]:
        # страница summary
        docs.append(p.get("summary",""))
        meta.append({"program_id": p["id"], "source": "summary"})
        # курсы
        for c in p.get("courses", [])[:300]:
            docs.append(c.get("name",""))
            meta.append({"program_id": p["id"], "source": "course"})
    return docs, meta

def build():
    docs, meta = load_corpus()
    vec = TfidfVectorizer(max_features=10000, ngram_range=(1,2))
    X = vec.fit_transform(docs)
    pickle.dump({"vectorizer": vec, "X": X, "meta": meta, "docs": docs}, open(INDEX_PATH, "wb"))
    print(f"[OK] Index built at {INDEX_PATH} (docs={len(docs)})")

if __name__ == "__main__":
    build()
