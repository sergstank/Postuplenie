\
import re, json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_programs():
    return json.loads((DATA_DIR / "programs.json").read_text(encoding="utf-8"))

def recommend_electives(profile: str, top_n=5):
    data = load_programs()
    electives = []
    for p in data["programs"]:
        for e in p.get("electives", []):
            electives.append({"program_id": p["id"], "name": e.get("name","")})
    if not electives:
        return []

    docs = [e["name"] for e in electives]
    vec = TfidfVectorizer(max_features=5000)
    X = vec.fit_transform(docs)
    q = vec.transform([profile])
    sims = cosine_similarity(q, X)[0]
    pairs = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[:top_n]
    out = []
    for idx, score in pairs:
        e = electives[idx]
        out.append({**e, "score": float(score)})
    return out
