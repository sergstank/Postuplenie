import re, json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

BLOCKLIST_PATTERNS = [
    r"вступител", r"онлайн", r"вопрос", r"правов", r"список тем",
    r"учебн", r"кабинет", r"партнер", r"контакт", r"телефон", r"стоимост", r"общежит"
]

def _is_valid_title(name: str) -> bool:
    s = (name or "").strip()
    if len(s) < 5 or len(s) > 120:
        return False
    low = s.lower()
    if re.search(r"\d{5,}", low):  # длинные числа — скорее мусор
        return False
    if any(re.search(p, low) for p in BLOCKLIST_PATTERNS):
        return False
    return True

def load_programs():
    return json.loads((DATA_DIR / "programs.json").read_text(encoding="utf-8"))

def recommend_electives(profile: str, top_n=5):
    data = load_programs()
    electives = []
    seen = set()
    for p in data["programs"]:
        for e in p.get("electives", []):
            name = (e.get("name") or "").strip()
            if not _is_valid_title(name):
                continue
            key = (p["id"], name)
            if key in seen:
                continue
            seen.add(key)
            electives.append({"program_id": p["id"], "name": name})

    if not electives:
        return []

    docs = [e["name"] for e in electives]
    vec = TfidfVectorizer(max_features=5000)
    X = vec.fit_transform(docs)
    q = vec.transform([profile or "профиль абитуриента"])
    sims = cosine_similarity(q, X)[0]

    scored = []
    for idx, score in enumerate(sims):
        if score >= 0.05:  # отсечь почти нулевые совпадения
            e = electives[idx]
            scored.append({**e, "score": float(score)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
