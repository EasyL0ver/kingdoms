"""Composable heuristics for biased (but still stochastic) play.

Each Heuristic is a scoring function that adjusts weights on options.
HeuristicStrategy composes multiple heuristics: scores are summed per option,
then a weighted-random pick is made (every option always has >0 probability).

Usage (CLI):
    python sim.py -n 1000 --heuristic prefer_trophies:2 --heuristic aggressive:1
    # 2 players get prefer_trophies, 1 gets aggressive, rest stay pure random
"""
from __future__ import annotations

import random
from abc import ABC
from typing import TYPE_CHECKING, Any

from strategy import Strategy, DecisionContext, Intent

if TYPE_CHECKING:
    from state import GameState, Player, Card, Action


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
_HEURISTIC_MAP: dict[str, type[Heuristic]] = {}


def _register_heuristic(cls):
    """Decorator: auto-register a Heuristic subclass by its ``name``."""
    _HEURISTIC_MAP[cls.name] = cls
    return cls


def get_heuristic(name: str) -> Heuristic:
    """Instantiate a heuristic by name."""
    if name not in _HEURISTIC_MAP:
        available = ", ".join(sorted(_HEURISTIC_MAP))
        raise ValueError(f"Unknown heuristic '{name}'. Available: {available}")
    return _HEURISTIC_MAP[name]()


def list_heuristics() -> list[str]:
    return sorted(_HEURISTIC_MAP)


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------
class Heuristic(ABC):
    """A scoring function that biases decisions.

    Return a list of (option, score_adjustment) tuples from each hook.
    Positive values make an option more likely; negative less likely.
    Omitted options get 0 adjustment (base weight 1.0 still applies).
    For hashable options, a dict {option: score} is also accepted.
    """
    name: str  # registry key, set on subclass

    def score_action(self, state: GameState, player: Player,
                     actions: list[Action], ctx: DecisionContext) -> list | dict:
        return {}

    def score_option(self, state: GameState, player: Player,
                     options: list, ctx: DecisionContext) -> list | dict:
        return {}

    def score_yes_no(self, state: GameState, player: Player,
                     ctx: DecisionContext) -> float:
        """Positive = prefer yes, negative = prefer no. 0 = no opinion."""
        return 0.0

    def score_order(self, state: GameState, player: Player,
                    items: list, ctx: DecisionContext) -> list | dict:
        """Higher score = earlier in order."""
        return {}


# ---------------------------------------------------------------------------
# HeuristicStrategy
# ---------------------------------------------------------------------------
class HeuristicStrategy(Strategy):
    """Composes heuristics into a weighted-random strategy.

    Scoring uses list-index alignment (not dict keys) so options don't need
    to be hashable.  Each heuristic returns a dict that maps *option objects*
    (by identity) to score adjustments; the strategy falls back to ``id()``
    look-ups when ``dict.get`` fails due to unhashable types.
    """

    MIN_WEIGHT = 0.01  # every option always has some probability

    def __init__(self, heuristics: list[Heuristic],
                 rng: random.Random | None = None):
        self.heuristics = heuristics
        self.rng = rng or random.Random()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _lookup(scores: list[tuple], option) -> float:
        """Look up score for *option* from a list of (option, score) pairs."""
        for o, s in scores:
            if o is option:
                return s
        return 0.0

    def _merge_scores(self, heuristic_results: list[dict | list]) -> list[tuple]:
        """Merge multiple scoring results into a flat (option, score) list.

        Each heuristic can return either:
          - a list of (option, score) tuples, OR
          - a dict {option: score} (only when options are hashable)
        """
        merged: dict[int, tuple] = {}  # id(option) → (option, total)
        for result in heuristic_results:
            items = result.items() if isinstance(result, dict) else result
            for opt, score in items:
                oid = id(opt)
                if oid in merged:
                    merged[oid] = (opt, merged[oid][1] + score)
                else:
                    merged[oid] = (opt, score)
        return list(merged.values())

    def _weighted_pick(self, options: list, scores: list[tuple]):
        weights = [max(1.0 + self._lookup(scores, o), self.MIN_WEIGHT)
                   for o in options]
        return self.rng.choices(options, weights=weights, k=1)[0]

    # ------------------------------------------------------------------
    # Strategy interface
    # ------------------------------------------------------------------
    def choose_action(self, state, player, actions, ctx):
        raw = [h.score_action(state, player, actions, ctx) for h in self.heuristics]
        scores = self._merge_scores(raw)
        return self._weighted_pick(actions, scores)

    def choose_from(self, state, player, options, ctx):
        raw = [h.score_option(state, player, options, ctx) for h in self.heuristics]
        scores = self._merge_scores(raw)
        return self._weighted_pick(options, scores)

    def choose_n(self, state, player, options, min_n, max_n, ctx):
        raw = [h.score_option(state, player, options, ctx) for h in self.heuristics]
        scores = self._merge_scores(raw)

        n = self.rng.randint(min_n, min(max_n, len(options)))
        if n == 0:
            return []
        if n >= len(options):
            return list(options)

        picked = []
        remaining = list(options)
        for _ in range(n):
            weights = [max(1.0 + self._lookup(scores, o), self.MIN_WEIGHT)
                       for o in remaining]
            choice = self.rng.choices(remaining, weights=weights, k=1)[0]
            picked.append(choice)
            remaining = [o for o in remaining if o is not choice]
        return picked

    def choose_yes_no(self, state, player, ctx):
        total = sum(h.score_yes_no(state, player, ctx) for h in self.heuristics)
        yes_weight = max(1.0 + total, self.MIN_WEIGHT)
        no_weight = max(1.0 - total, self.MIN_WEIGHT)
        return self.rng.choices([True, False], weights=[yes_weight, no_weight], k=1)[0]

    def choose_order(self, state, player, items, ctx):
        raw = [h.score_order(state, player, items, ctx) for h in self.heuristics]
        scores = self._merge_scores(raw)
        decorated = [(self._lookup(scores, item), self.rng.random(), item)
                     for item in items]
        decorated.sort(key=lambda x: (-x[0], x[1]))
        return [item for _, _, item in decorated]


# ---------------------------------------------------------------------------
# Helper utilities for heuristics
# ---------------------------------------------------------------------------
def _card_tag_score(options, tag: str, bonus: float) -> list[tuple]:
    """Score options that are Card objects with a given tag. Returns [(option, score)]."""
    result = []
    for o in options:
        if hasattr(o, "tags") and tag in o.tags:
            result.append((o, bonus))
    return result


def _player_domain_size(player) -> int:
    return len(player.domain)


def _claw_depletion_ratio(state) -> float:
    """0.0 = full pile, 1.0 = fully depleted."""
    zone = state.zone_cards.get("claw")
    if not zone:
        return 0.0
    total = len(zone.pile)
    if total == 0:
        return 1.0
    remaining = total - zone.pile_ptr
    return 1.0 - (remaining / total)


def _player_rank(state, player) -> float:
    """0.0 = first place (most cards), 1.0 = last place."""
    sizes = sorted([_player_domain_size(p) for p in state.players], reverse=True)
    my_size = _player_domain_size(player)
    if sizes[0] == sizes[-1]:
        return 0.5
    rank = sizes.index(my_size)
    return rank / (len(sizes) - 1)


def _leader_player(state, player):
    """Return the opponent with the most domain cards (or None)."""
    opponents = [p for p in state.players if p is not player]
    if not opponents:
        return None
    return max(opponents, key=lambda p: _player_domain_size(p))


# ---------------------------------------------------------------------------
# Auto-import heuristic modules to trigger @_register_heuristic
# ---------------------------------------------------------------------------
from heuristics import combat, drafting, scoring  # noqa: E402, F401
