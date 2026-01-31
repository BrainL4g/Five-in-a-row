from game import Game

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Ошибка при запуске игры: {e}")
        import traceback

        traceback.print_exc()
        input("Нажмите Enter для выхода...")
