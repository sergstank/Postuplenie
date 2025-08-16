\
from .dialog import BotCore, UserState

def main():
    core = BotCore()
    state = UserState()
    print(core.welcome())
    while True:
        try:
            text = input("> ").strip()
        except EOFError:
            break
        if text == "/compare":
            print(core.compare_programs(state)); continue
        if text == "/recommend":
            print(core.recommend(state)); continue
        if state.stage == "greet":
            print(core.handle_profile(text, state))
        else:
            print(core.answer(text, state))

if __name__ == "__main__":
    main()
