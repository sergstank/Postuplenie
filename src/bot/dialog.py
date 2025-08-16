\
from dataclasses import dataclass, field
from typing import Dict, Any, List
from ..rag.retriever import Retriever
from .recommend import recommend_electives

@dataclass
class UserState:
    profile: Dict[str, Any] = field(default_factory=dict)
    stage: str = "greet"  # greet -> profile -> qa -> recommend
    last_q: str = ""

class BotCore:
    def __init__(self):
        self.ret = Retriever(threshold=0.12)

    def welcome(self):
        return ("Привет! Я помогу сравнить магистратуры ИТМО: "
                "«Искусственный интеллект» и «AI Product». "
                "Коротко опиши свой бэкграунд и цели (например: «2 года data‑analyst, хочу в MLOps/продукт ИИ»).")

    def handle_profile(self, text, state: UserState):
        state.profile["freeform"] = text
        state.stage = "qa"
        return ("Спасибо! Задай вопрос по программам — я отвечаю на основе материалов ИТМО. "
                "Команды: /compare — сравнение программ, /recommend — мои рекомендованные элективы.")

    def compare_programs(self, state: UserState):
        # упрощённое резюме через ретривер
        a = self.ret.search("цели программы Искусственный интеллект ядро дисциплины", k=3)
        b = self.ret.search("цели программы AI Product продуктовые треки", k=3)
        def lines(res):
            return "\n".join([f"• {r['text']}" for r in res]) if res else "— (данные не найдены, попробуйте обновить индекс)"
        return ("Сравнение (черновик на основе корпуса):\n\n"
                "AI:\n" + lines(a) + "\n\nAI Product:\n" + lines(b))

    def recommend(self, state: UserState):
        prof = state.profile.get("freeform", "")
        recs = recommend_electives(prof, top_n=5)
        if not recs:
            return "Пока не нашёл элективы в планах. Запусти сбор данных ещё раз или уточни профиль."
        lines = [f"• [{r['program_id']}] {r['name']} (релевантность {r['score']:.2f})" for r in recs]
        return "Рекомендованные элективы:\n" + "\n".join(lines)

    def answer(self, text, state: UserState):
        # Guardrail: проверка релевантности
        hits = self.ret.search(text, k=5)
        if not hits:
            return ("Я отвечаю только по двум магистерским программам ИТМО (AI и AI Product). "
                    "Задайте вопрос о программах, учебных планах, элективах или поступлении.")
        # соберём краткий ответ из найденных фрагментов
        bullets = [f"• {h['text']} (источник: {h['meta']['source']}, {h['meta']['program_id']})" for h in hits]
        return "\n".join(bullets)
