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
        self._limit_data_size(self.good_moves)
        self._limit_data_size(self.bad_moves)

    def _limit_data_size(self, data: Dict):
        if len(data) > 5000:
            keys = sorted(data.keys())[:len(data) - 3000]
            for key in keys:
                del data[key]

    def _load_data(self, filepath: str) -> Dict[str, Dict[str, int]]:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}

    def save_learning_data(self, moves: List[Tuple[int, int, int]], winner: int):
        if winner not in (AI_PLAYER, HUMAN):
            return

        data = self.good_moves if winner == AI_PLAYER else self.bad_moves
        bonus = 10 if winner == AI_PLAYER else -10

        temp_board = Board()
        seen_hashes = set()

        for i, (row, col, player) in enumerate(moves):
            current_hash = temp_board.get_hash()
            if current_hash in seen_hashes:
                continue
            seen_hashes.add(current_hash)

            move_key = f"{row},{col}"
            if player == AI_PLAYER:
                if current_hash not in data:
                    data[current_hash] = {}
                data[current_hash][move_key] = data[current_hash].get(move_key, 0) + bonus

            temp_board.make_move(row, col, player)

        if len(data) > 3000:
            oldest_keys = sorted(data.keys())[:len(data) - 2000]
            for key in oldest_keys:
                del data[key]

        filepath = 'data/good_moves.json' if winner == AI_PLAYER else 'data/bad_moves.json'
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        self.eval_cache.clear()

        if move := self._find_winning_move(board, symbol):
            return move
        if move := self._find_winning_move(board, opponent):
            return move
        if move := self._find_double_open_four_threat(board, opponent):
            return move
        if move := self._find_double_open_three_threat(board, opponent):
            return move

        total_moves = BOARD_SIZE * BOARD_SIZE - len(board.get_empty_cells())

        if total_moves < 8:
            cx, cy = BOARD_SIZE // 2, BOARD_SIZE // 2
            zone = [(cy + dr, cx + dc) for dr in range(-5, 6) for dc in range(-5, 6)
                    if
                    0 <= cy + dr < BOARD_SIZE and 0 <= cx + dc < BOARD_SIZE and board.grid[cy + dr, cx + dc] == EMPTY]
            return random.choice(zone) if zone else self._find_near_move(board)

        candidates = board.get_near_empty_cells()[:40]
        if not candidates:
            candidates = board.get_empty_cells()[:60]

        scored = []
        for r, c in candidates:
            score = self._evaluate_position(board, r, c, symbol)
            scored.append(((r, c), score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_score = scored[0][1]
        good_moves = [pos for pos, sc in scored if sc >= top_score - 4000][:8]
        return random.choice(good_moves) if good_moves else scored[0][0]

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

    def _find_double_open_three_threat(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        threats = []
        for r, c in board.get_near_empty_cells():
            if board.make_move(r, c, player):
                count = self._count_open_threes(board, player)
                board.undo_move(r, c)
                if count >= 2:
                    threats.append((r, c))
        return random.choice(threats) if threats else None

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

    def _evaluate_position(self, board: Board, r: int, c: int, symbol: int) -> int:
        key = (r, c, symbol)
        if key in self.eval_cache:
            return self.eval_cache[key]

        if not board.make_move(r, c, symbol):
            return -999999

        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            stones = 1
            open_ends = 0
            for sign in (1, -1):
                nr, nc = r + dr * sign, c + dc * sign
                while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if board.grid[nr, nc] == symbol:
                        stones += 1
                    elif board.grid[nr, nc] == EMPTY:
                        open_ends += 1
                        break
                    else:
                        break
                    nr += dr * sign
                    nc += dc * sign
            if stones >= 5:
                score += 1000000
            elif stones == 4:
                score += 60000 if open_ends >= 2 else 12000
            elif stones == 3:
                score += 10000 if open_ends >= 2 else 1200
            elif stones == 2:
                score += 600 if open_ends == 2 else 80

        board.undo_move(r, c)

        current_hash = board.get_hash()
        move_key = f"{r},{c}"
        bonus = 0
        if current_hash in self.good_moves and move_key in self.good_moves[current_hash]:
            bonus += min(self.good_moves[current_hash][move_key], 100)
        if current_hash in self.bad_moves and move_key in self.bad_moves[current_hash]:
            bonus += max(self.bad_moves[current_hash][move_key], -100)
        score += bonus

        self.eval_cache[key] = score
        return score


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
