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


class EasyStrategy(AIStrategy):
    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        empties = board.get_empty_cells()
        return random.choice(empties) if empties else (BOARD_SIZE // 2, BOARD_SIZE // 2)


class MediumStrategy(AIStrategy):
    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        if move := self._find_winning_move(board, symbol):
            return move
        if move := self._find_winning_move(board, opponent):
            return move
        return self._find_near_move(board)


class HardStrategy(AIStrategy):
    DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]
    OPEN_FOUR_SCORE = 80000
    CAPTURE_TWO_SCORE = 50000
    OPEN_THREE_SCORE = 15000
    BLOCKED_FOUR_SCORE = 12000
    OPEN_TWO_SCORE = 3000
    BLOCKED_THREE_SCORE = 800
    OPEN_ONE_SCORE = 100

    def __init__(self):
        os.makedirs('data', exist_ok=True)
        self.good_moves = self._load_data('data/good_moves.json')
        self.bad_moves = self._load_data('data/bad_moves.json')
        self.eval_cache: Dict[str, int] = {}
        self._limit_data_size(self.good_moves)
        self._limit_data_size(self.bad_moves)

    def _limit_data_size(self, data: Dict) -> None:
        max_size = 5000
        keep_size = 3000
        if len(data) > max_size:
            keys = sorted(data.keys())[:len(data) - keep_size]
            for key in keys:
                del data[key]

    def _load_data(self, filepath: str) -> Dict[str, Dict[str, int]]:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}

    def save_learning_data(self, moves: List[Tuple[int, int, int]], winner: int) -> None:
        if winner not in (AI_PLAYER, HUMAN):
            return

        data = self.good_moves if winner == AI_PLAYER else self.bad_moves
        bonus = 10 if winner == AI_PLAYER else -10

        temp_board = Board()
        seen_hashes: set[str] = set()

        for row, col, player in moves:
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
            oldest_keys = sorted(data.keys())[:1000]
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
        if move := self._find_critical_threat(board, opponent, 4, 2):
            return move
        if move := self._find_critical_threat(board, symbol, 3, 2):
            return move
        if move := self._find_critical_threat(board, opponent, 3, 2):
            return move

        total_moves = BOARD_SIZE * BOARD_SIZE - len(board.get_empty_cells())

        if total_moves < 8:
            return self._get_opening_move(board)

        candidates = board.get_near_empty_cells()[:50]
        if not candidates:
            candidates = board.get_empty_cells()[:60]

        best_moves = self._select_best_moves(candidates, board, symbol, opponent)
        if best_moves:
            return random.choice(best_moves)
        
        return candidates[0] if candidates else (BOARD_SIZE // 2, BOARD_SIZE // 2)

    def _get_opening_move(self, board: Board) -> Tuple[int, int]:
        cx, cy = BOARD_SIZE // 2, BOARD_SIZE // 2
        zone = [(cy + dr, cx + dc) for dr in range(-5, 6) for dc in range(-5, 6)
                if 0 <= cy + dr < BOARD_SIZE and 0 <= cx + dc < BOARD_SIZE 
                and board.grid[cy + dr, cx + dc] == EMPTY]
        return random.choice(zone) if zone else self._find_near_move(board)

    def _select_best_moves(self, candidates: List[Tuple[int, int]], board: Board, 
                           symbol: int, opponent: int) -> List[Tuple[int, int]]:
        scored = []
        for r, c in candidates:
            score = self._evaluate_position(board, r, c, symbol, opponent)
            scored.append(((r, c), score))

        scored.sort(key=lambda x: x[1], reverse=True)
        
        if not scored:
            return []
            
        top_score = scored[0][1]
        threshold = max(4000, top_score // 10)
        good_moves = [pos for pos, sc in scored if sc >= top_score - threshold][:8]
        
        return good_moves if good_moves else [scored[0][0]]

    def _find_critical_threat(self, board: Board, player: int, 
                              stones: int, min_open_ends: int) -> Optional[Tuple[int, int]]:
        threats = []
        for r, c in board.get_near_empty_cells():
            if board.make_move(r, c, player):
                count = self._count_pattern(board, player, stones, min_open_ends)
                board.undo_move(r, c)
                if count >= 2:
                    threats.append((r, c))
        return random.choice(threats) if threats else None

    def _count_pattern(self, board: Board, player: int, stones: int, 
                       min_open_ends: int) -> int:
        count = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] == player:
                    for dr, dc in self.DIRECTIONS:
                        _, open_ends = self._count_in_direction(board, r, c, dr, dc, player)
                        if self._count_line_length(board, r, c, dr, dc, player) == stones and open_ends >= min_open_ends:
                            count += 1
        return count

    def _count_line_length(self, board: Board, r: int, c: int, dr: int, dc: int, 
                           player: int) -> int:
        length = 1
        for sign in (1, -1):
            nr, nc = r + dr * sign, c + dc * sign
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if board.grid[nr, nc] == player:
                    length += 1
                else:
                    break
                nr += dr * sign
                nc += dc * sign
        return length

    def _count_in_direction(self, board: Board, r: int, c: int, dr: int, dc: int, 
                            player: int) -> Tuple[int, int]:
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

    def _evaluate_position(self, board: Board, r: int, c: int, symbol: int, 
                           opponent: int) -> int:
        key = f"{board.get_hash()},{r},{c}"
        if key in self.eval_cache:
            return self.eval_cache[key]

        if not board.make_move(r, c, symbol):
            return -999999

        attack_score = self._score_line(board, r, c, symbol, symbol)
        defense_score = self._score_line(board, r, c, symbol, opponent)
        
        board.undo_move(r, c)

        current_hash = board.get_hash()
        move_key = f"{r},{c}"
        bonus = 0
        if current_hash in self.good_moves and move_key in self.good_moves[current_hash]:
            bonus += min(self.good_moves[current_hash][move_key], 100)
        if current_hash in self.bad_moves and move_key in self.bad_moves[current_hash]:
            bonus += max(self.bad_moves[current_hash][move_key], -100)
        
        score = attack_score * 2 + defense_score + bonus
        self.eval_cache[key] = score
        return score

    def _score_line(self, board: Board, r: int, c: int, player: int, 
                    target: int) -> int:
        total = 0
        for dr, dc in self.DIRECTIONS:
            stones, open_ends = self._count_in_direction(board, r, c, dr, dc, target)
            if stones >= 5:
                total += 1000000
            elif stones == 4:
                total += self.OPEN_FOUR_SCORE if open_ends >= 2 else self.BLOCKED_FOUR_SCORE
            elif stones == 3:
                total += self.OPEN_THREE_SCORE if open_ends >= 2 else self.BLOCKED_THREE_SCORE
            elif stones == 2:
                total += self.OPEN_TWO_SCORE if open_ends == 2 else self.OPEN_ONE_SCORE
        return total


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
