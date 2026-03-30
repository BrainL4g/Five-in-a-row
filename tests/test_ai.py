from src.board import Board
from src.players import AIPlayer
from src.constants import BOARD_SIZE, Difficulty, AI_PLAYER


def test_ai_medium_move_non_destructive_on_empty_board():
    board = Board()
    ai = AIPlayer(AI_PLAYER, Difficulty.MEDIUM)
    hash_before = board.get_hash()
    move = ai.get_move(board)
    hash_after = board.get_hash()
    assert move is not None and isinstance(move, tuple) and len(move) == 2
    assert hash_before == hash_after


def test_ai_move_none_on_full_board():
    board = Board()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            player = AI_PLAYER if (r + c) % 2 else 0
            if (r + c) % 2 == 0:
                board.make_move(r, c, 1)
    empties = board.get_empty_cells()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board.grid[r, c] == 0:
                board.make_move(r, c, 2)
    ai = AIPlayer(AI_PLAYER, Difficulty.MEDIUM)
    assert board.get_empty_cells() == []
    assert ai.get_move(board) is None


def test_ai_move_bounds_on_empty_board_eas():
    board = Board()
    ai = AIPlayer(AI_PLAYER, Difficulty.EASY)
    move = ai.get_move(board)
    assert isinstance(move, tuple) and 0 <= move[0] < BOARD_SIZE and 0 <= move[1] < BOARD_SIZE
