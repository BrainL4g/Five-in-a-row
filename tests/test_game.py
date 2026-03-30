import pytest

from src.game import Game
from src.constants import BOARD_SIZE, HUMAN, AI_PLAYER, Difficulty
from src.players import AIPlayer, HardStrategy


def test_status_text_states():
    game = Game()
    assert game._get_status_text() == "Ваш ход"

    game.ai_thinking = True
    assert game._get_status_text() == "Компьютер думает..."
    game.ai_thinking = False

    game.game_over = True
    game.winner = HUMAN
    assert game._get_status_text() == "Вы победили!"

    game.winner = AI_PLAYER
    assert game._get_status_text() == "Победил компьютер"

    game.winner = None
    assert game._get_status_text() == "Ничья!"


def test_reset_game_resets_state():
    game = Game()
    game.board.make_move(0, 0, HUMAN)
    game.moves.append((0, 0, HUMAN))
    game.board.make_move(1, 1, AI_PLAYER)
    game.moves.append((1, 1, AI_PLAYER))
    game.current_player = AI_PLAYER
    game.game_over = True
    game.winner = HUMAN
    initial_hash = game.board.get_hash()
    game.reset_game()
    fresh = __import__('src.board', fromlist=['Board']).Board()
    assert game.board.get_hash() == fresh.get_hash()
    assert game.current_player == HUMAN
    assert game.game_over is False
    assert game.winner is None
    assert game.moves == []


def test_undo_move_not_enough_moves():
    game = Game()
    assert game.undo_move() is False
    game.board.make_move(0, 0, HUMAN)
    game.moves.append((0, 0, HUMAN))
    assert game.undo_move() is False


def test_undo_move_two_moves_succeeds():
    game = Game()
    game.board.make_move(0, 0, HUMAN)
    game.moves.append((0, 0, HUMAN))
    game.board.make_move(1, 1, AI_PLAYER)
    game.moves.append((1, 1, AI_PLAYER))
    assert game.undo_move() is True
    assert game.board.grid[0, 0] == 0
    assert game.board.grid[1, 1] == 0
    assert game.moves == []


def test_undo_move_undoes_two_moves():
    game = Game()
    game.board.make_move(0, 0, HUMAN)
    game.moves.append((0, 0, HUMAN))
    game.board.make_move(1, 1, AI_PLAYER)
    game.moves.append((1, 1, AI_PLAYER))

    assert game.undo_move() is True
    assert game.board.grid[1, 1] == 0
    assert game.board.grid[0, 0] == 0
    assert game.moves == []


def test_after_move_win_and_draw_and_progress_paths():
    game = Game()
    for c in range(5):
        game.board.make_move(0, c, HUMAN)
        game.moves.append((0, c, HUMAN))
    game._after_move(HUMAN)
    assert game.game_over is True
    assert game.winner == HUMAN

    game = Game()
    game.board.is_full = lambda: True
    game.board.check_win = lambda player: False
    game._after_move(HUMAN)
    assert game.game_over is True
    assert game.winner is None

    game = Game()
    game.board.make_move(0, 0, HUMAN)
    game.moves.append((0, 0, HUMAN))
    game._after_move(HUMAN)
    assert game.current_player == AI_PLAYER

    game = Game()
    game.settings.selected_difficulty = Difficulty.HARD
    game.ai = AIPlayer(AI_PLAYER, game.settings.get_difficulty())
    learning_called = {}
    if isinstance(game.ai.strategy, HardStrategy):
        def fake_save(moves, winner):
            learning_called['called'] = True
            learning_called['moves'] = moves
            learning_called['winner'] = winner
        game.ai.strategy.save_learning_data = fake_save
    moves = [(0, c, HUMAN) for c in range(5)]
    for r, c, p in moves:
        game.board.make_move(r, c, p)
    game.moves.extend(moves)
    game._after_move(HUMAN)
    assert game.game_over is True
    assert game.winner == HUMAN
    if isinstance(game.ai.strategy, HardStrategy):
        assert learning_called.get('called', False) is True


def test_get_hovered_cell():
    """Тест определения клетки под курсором"""
    from src.constants import GRID_OFFSET_X, GRID_OFFSET_Y, CELL_SIZE
    game = Game()
    
    x = GRID_OFFSET_X + CELL_SIZE // 2
    y = GRID_OFFSET_Y + CELL_SIZE // 2
    assert game._get_hovered_cell((x, y)) == (0, 0)
    
    assert game._get_hovered_cell((0, 0)) is None
    assert game._get_hovered_cell((GRID_OFFSET_X - 1, GRID_OFFSET_Y)) is None
    assert game._get_hovered_cell((GRID_OFFSET_X, GRID_OFFSET_Y - 1)) is None
    
    outside_x = GRID_OFFSET_X + BOARD_SIZE * CELL_SIZE + 1
    outside_y = GRID_OFFSET_Y + BOARD_SIZE * CELL_SIZE + 1
    assert game._get_hovered_cell((outside_x, outside_y)) is None
    
    mid_x = GRID_OFFSET_X + 7 * CELL_SIZE + CELL_SIZE // 2
    mid_y = GRID_OFFSET_Y + 7 * CELL_SIZE + CELL_SIZE // 2
    assert game._get_hovered_cell((mid_x, mid_y)) == (7, 7)


def test_after_move_ai_win():
    """Тест победы AI"""
    game = Game()
    for c in range(5):
        game.board.make_move(0, c, AI_PLAYER)
    game._after_move(AI_PLAYER)
    assert game.game_over is True
    assert game.winner == AI_PLAYER


def test_undo_move_during_ai_turn():
    """Тест undo_move когда ход AI - должен вернуть False"""
    game = Game()
    game.current_player = AI_PLAYER
    game.board.make_move(0, 0, HUMAN)
    game.moves.append((0, 0, HUMAN))
    assert game.undo_move() is False


def test_undo_move_when_game_over():
    """Тест undo_move когда игра окончена - должен вернуть False"""
    game = Game()
    game.game_over = True
    assert game.undo_move() is False
