from dataclasses import dataclass, field
from typing import Dict, Any
import re
from ..rag.retriever import Retriever
from .recommend import recommend_electives

def _clean_line(s: str) -> bool:
    if not s or len(s) < 5 or len(s) > 180:
        return False
    low = s.lower()
    if re.search(r"\d{5,}", low):   # много цифр — контакты/мусор
        return False
    bad = ["личный кабинет", "показать", "партнер", "телефон", "стоимость", "общежит"]
    return not any(b in low for b in bad)

def _fmt(res, limit=5):
    out = []
    seen = set()
    for r in res:
        t = r["text"].strip()
        if not _clean_line(t): 
            continue
        if t in seen:
            continue
        seen.add(t)
        out.append(f"• {t}")
        if len(out) >= limit:
            break
    return "\n".join(out) if out else "— (фрагменты не найдены)"

@dataclass
class UserState:
    profile: Dict[str, Any] = field(default_factory=dict)
    stage: str = "greet"  # greet -> qa
    last_q: str = ""

class BotCore:
    def __init__(self):
        self.ret = Retriever(threshold=0.12)

    def help_text(self):
        return ("Команды:\n"
                "/start — начать заново\n"
                "/help — помощь\n"
                "/compare — отличие программ AI vs AI Product\n"
                "/recommend — элективы под ваш профиль\n"
                "Сначала одним сообщением опишите бэкграунд и цели.")

    def welcome(self):
        return ("Привет! Я помогу сравнить магистратуры ИТМО: «Искусственный интеллект» и «AI Product».\n"
                "Опиши свой бэкграунд и цели (например: «2 года data-analyst, хочу в MLOps/продукт ИИ»).\n"
                + self.help_text())

    def handle_profile(self, text, state: UserState):
        state.profile["freeform"] = text
        state.stage = "qa"
        return ("Спасибо! Задай вопрос по программам — я отвечаю на основе материалов ИТМО.\n"
                "Команды: /compare /recommend /help")

    def compare_programs(self, state: UserState):
        ai_a = self.ret.search('цели программы "Искусственный интеллект" ядро дисциплин профиль выпускника', k=8)
        ai_p = self.ret.search('цели программы "AI Product" продуктовые треки профиль выпускника', k=8)
        return ("Сравнение (кратко):\n\n"
                "AI:\n" + _fmt(ai_a, 5) + "\n\n"
                "AI Product:\n" + _fmt(ai_p, 5))

    def recommend(self, state: UserState):
        prof = state.profile.get("freeform", "")
        recs = recommend_electives(prof, top_n=5)
        if not recs:
            return "Пока не нашёл подходящих элективов. Попробуйте уточнить профиль."
        lines = [f"• [{r['program_id']}] {r['name']} (релевантность {r['score']:.2f})" for r in recs]
        return "Рекомендованные элективы:\n" + "\n".join(lines)

    def reset(self, state: UserState):
        state.profile.clear()
        state.stage = "greet"
        return self.welcome()

    def answer(self, text, state: UserState):
        hits = self.ret.search(text, k=5)
        if not hits:
            return ("Я отвечаю только по двум магистерским программам ИТМО (AI и AI Product). "
                    "Задайте вопрос о программах, планах, элективах или используйте /help.")
        bullets = [f"• {h['text']} (источник: {h['meta']['source']}, {h['meta']['program_id']})"
                   for h in hits if _clean_line(h['text'])]
        return "\n".join(bullets) if bullets else "Не нашёл подходящих фрагментов, переформулируйте вопрос."
