from __future__ import annotations
from abc import ABC, abstractmethod
import random
import os
import json
import hashlib
from typing import Tuple, Optional, List, Dict
from src.constants import BOARD_SIZE, HUMAN, AI_PLAYER, EMPTY, Difficulty
from src.board import Board


class Player(ABC):
    @abstractmethod
    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
        pass


class HumanPlayer(Player):
    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
        return None


class AIStrategy(ABC):
    @abstractmethod
    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        pass


class EasyStrategy(AIStrategy):
    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        empties = board.get_empty_cells()
        return random.choice(empties) if empties else (7, 7)


class MediumStrategy(AIStrategy):
    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        if move := self._find_winning_move(board, symbol):
            return move
        if move := self._find_winning_move(board, opponent):
            return move
        return self._find_near_move(board)

    def _find_winning_move(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        for r, c in board.get_near_empty_cells():
            if board.make_move(r, c, player):
                if board.check_win(player):
                    board.undo_move(r, c)
                    return (r, c)
                board.undo_move(r, c)
        return None

    def _find_near_move(self, board: Board) -> Tuple[int, int]:
        near = board.get_near_empty_cells()
        return random.choice(near) if near else random.choice(board.get_empty_cells())


class HardStrategy(AIStrategy):
    def __init__(self):
        os.makedirs('data', exist_ok=True)
        self.good_moves = self._load_data('data/good_moves.json')
        self.bad_moves = self._load_data('data/bad_moves.json')
        self.eval_cache = {}
        self.trans_table = {}

    def _load_data(self, filepath: str) -> Dict[str, Dict[str, int]]:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}

    def save_learning_data(self, moves: List[Tuple[int, int, int]], winner: int):
        if winner == AI_PLAYER:
            data = self.good_moves
            bonus = 5000
        else:
            data = self.bad_moves
            bonus = -3000

        temp_board = Board()
        for row, col, player in moves:
            current_hash = temp_board.get_hash()
            move_key = f"{row},{col}"
            if player == AI_PLAYER:
                if current_hash not in data:
                    data[current_hash] = {}
                data[current_hash][move_key] = data[current_hash].get(move_key, 0) + bonus
            temp_board.make_move(row, col, player)

        if winner == AI_PLAYER:
            filepath = 'data/good_moves.json'
        else:
            filepath = 'data/bad_moves.json'
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        self.eval_cache.clear()
        self.trans_table.clear()

        if move := self._find_winning_move(board, symbol):
            return move
        if move := self._find_winning_move(board, opponent):
            return move
        if move := self._find_double_open_four_threat(board, opponent):
            return move
        if move := self._find_double_or_critical_three_threat(board, opponent):
            return move

        total_moves = BOARD_SIZE * BOARD_SIZE - len(board.get_empty_cells())

        if total_moves < 8:
            cx, cy = BOARD_SIZE // 2, BOARD_SIZE // 2
            zone = [(cy + dr, cx + dc) for dr in range(-5, 6) for dc in range(-5, 6)
                    if
                    0 <= cy + dr < BOARD_SIZE and 0 <= cx + dc < BOARD_SIZE and board.grid[cy + dr, cx + dc] == EMPTY]
            return random.choice(zone) if zone else self._find_near_move(board)

        best_score = -float('inf')
        best_move = None
        candidates = board.get_near_empty_cells()[:40]
        if not candidates:
            candidates = board.get_empty_cells()[:60]

        for r, c in candidates:
            board.make_move(r, c, symbol)
            score = -self._minimax(board, 4, False, -float('inf'), float('inf'), opponent, symbol)
            board.undo_move(r, c)
            if score > best_score:
                best_score = score
                best_move = (r, c)

        return best_move or random.choice(candidates)

    def _minimax(self, board: Board, depth: int, maximizing: bool, alpha: float, beta: float, player: int,
                 opponent: int) -> float:
        hash_key = board.get_hash() + str(depth) + str(maximizing)
        if hash_key in self.trans_table:
            return self.trans_table[hash_key]

        if board.check_win(player if not maximizing else opponent):
            return 1000000 if maximizing else -1000000
        if board.is_full() or depth == 0:
            return self._evaluate(board, player, opponent)

        candidates = board.get_near_empty_cells() or board.get_empty_cells()[:40]

        if maximizing:
            max_eval = -float('inf')
            for r, c in candidates:
                board.make_move(r, c, player)
                eval = self._minimax(board, depth - 1, False, alpha, beta, player, opponent)
                board.undo_move(r, c)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            self.trans_table[hash_key] = max_eval
            return max_eval
        else:
            min_eval = float('inf')
            for r, c in candidates:
                board.make_move(r, c, opponent)
                eval = self._minimax(board, depth - 1, True, alpha, beta, player, opponent)
                board.undo_move(r, c)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            self.trans_table[hash_key] = min_eval
            return min_eval

    def _evaluate(self, board: Board, symbol: int, opponent: int) -> int:
        score_me = self._eval_player(board, symbol)
        score_opp = self._eval_player(board, opponent)
        return score_me - score_opp * 1.15

    def _eval_player(self, board: Board, p: int) -> int:
        score = 0
        dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] == p:
                    for dr, dc in dirs:
                        cnt, open_ends = self._count_line(board, r, c, dr, dc, p)
                        if cnt >= 5:
                            score += 1000000
                        elif cnt == 4:
                            score += 80000 if open_ends >= 2 else 15000
                        elif cnt == 3:
                            score += 12000 if open_ends >= 2 else 1500
                        elif cnt == 2:
                            score += 800 if open_ends == 2 else 100
        return score

    def _count_line(self, board: Board, r: int, c: int, dr: int, dc: int, p: int) -> Tuple[int, int]:
        cnt = 1
        open_ends = 0
        for s in (1, -1):
            nr, nc = r + dr * s, c + dc * s
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if board.grid[nr, nc] == p:
                    cnt += 1
                elif board.grid[nr, nc] == EMPTY:
                    open_ends += 1
                    break
                else:
                    break
                nr += dr * s
                nc += dc * s
        return cnt, open_ends

    def _find_winning_move(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        for r, c in board.get_near_empty_cells():
            if board.make_move(r, c, player):
                if board.check_win(player):
                    board.undo_move(r, c)
                    return (r, c)
                board.undo_move(r, c)
        return None

    def _find_double_open_four_threat(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        for r, c in board.get_near_empty_cells():
            if board.make_move(r, c, player):
                if self._count_open_fours(board, player) >= 2:
                    board.undo_move(r, c)
                    return (r, c)
                board.undo_move(r, c)
        return None

    def _find_double_or_critical_three_threat(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        for r, c in board.get_near_empty_cells():
            if board.make_move(r, c, player):
                threes = self._count_open_threes(board, player)
                board.undo_move(r, c)
                if threes >= 2 or threes >= 1:
                    return (r, c)
        return None

    def _count_open_fours(self, board: Board, player: int) -> int:
        count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] == player:
                    for dr, dc in directions:
                        stones, open_ends = self._count_in_direction(board, r, c, dr, dc, player)
                        if stones == 4 and open_ends >= 2:
                            count += 1
        return count

    def _count_open_threes(self, board: Board, player: int) -> int:
        count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] == player:
                    for dr, dc in directions:
                        stones, open_ends = self._count_in_direction(board, r, c, dr, dc, player)
                        if stones == 3 and open_ends >= 2:
                            count += 1
        return count

    def _count_in_direction(self, board: Board, r: int, c: int, dr: int, dc: int, player: int) -> Tuple[int, int]:
        count = 1
        open_ends = 0
        for sign in (1, -1):
            nr, nc = r + dr * sign, c + dc * sign
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if board.grid[nr, nc] == player:
                    count += 1
                elif board.grid[nr, nc] == EMPTY:
                    open_ends += 1
                    break
                else:
                    break
                nr += dr * sign
                nc += dc * sign
        return count, open_ends

    def _find_near_move(self, board: Board) -> Tuple[int, int]:
        near = board.get_near_empty_cells()
        return random.choice(near) if near else random.choice(board.get_empty_cells())


class AIPlayer(Player):
    def __init__(self, symbol: int, difficulty: Difficulty):
        self.symbol = symbol
        self.opponent = HUMAN if symbol == AI_PLAYER else AI_PLAYER
        self.strategy = self._get_strategy(difficulty)

    def _get_strategy(self, difficulty: Difficulty) -> AIStrategy:
        match difficulty:
            case Difficulty.EASY:
                return EasyStrategy()
            case Difficulty.MEDIUM:
                return MediumStrategy()
            case Difficulty.HARD:
                return HardStrategy()
            case _:
                return EasyStrategy()

    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
        empties = board.get_empty_cells()
        if not empties:
            return None
        return self.strategy.find_move(board, self.symbol, self.opponent)
