\
import pickle
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
INDEX_PATH = DATA_DIR / "tfidf_index.pkl"

class Retriever:
    def __init__(self, threshold=0.15):
        store = pickle.load(open(INDEX_PATH, "rb"))
        self.vec = store["vectorizer"]
        self.X = store["X"]
        self.meta = store["meta"]
        self.docs = store["docs"]
        self.threshold = threshold

    def search(self, query, k=5):
        q = self.vec.transform([query])
        sims = cosine_similarity(q, self.X)[0]
        pairs = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[:k]
        results = []
        for idx, score in pairs:
            if score < self.threshold:
                continue
            results.append({
                "text": self.docs[idx],
                "score": float(score),
                "meta": self.meta[idx],
            })
        return results
