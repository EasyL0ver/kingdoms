"""Composable heuristics for biased (but still stochastic) play.

Each Heuristic is a scoring function that adjusts weights on options.
HeuristicStrategy composes multiple heuristics: scores are summed per option,
then a weighted-random pick is made (every option always has >0 probability).

Heuristic hooks mirror game decision categories:
  score_draft:              choosing which cards to take (GAIN, TURN_ACTION)
  score_activate:           choosing which card to activate
  score_resolution_choice:  resolving effects — targets, modes, sacrifices, yes/no
  score_order:              choosing resolution sequence

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
# Intents routed to score_draft
_DRAFT_INTENTS = {Intent.GAIN, Intent.TURN_ACTION}

class Heuristic(ABC):
    """A scoring function that biases decisions.

    Return a list of (option, score_adjustment) tuples from each hook.
    Positive values make an option more likely; negative less likely.
    Omitted options get 0 adjustment (base weight 1.0 still applies).
    For hashable options, a dict {option: score} is also accepted.
    """
    name: str  # registry key, set on subclass

    def score_activate(self, state: GameState, player: Player,
                       actions: list[Action], ctx: DecisionContext) -> list | dict:
        """Score which card to activate this turn."""
        return {}

    def score_draft(self, state: GameState, player: Player,
                    options: list, ctx: DecisionContext) -> list | dict:
        """Score which cards to take/gain."""
        return {}

    def score_resolution_choice(self, state: GameState, player: Player,
                                options: list, ctx: DecisionContext) -> list | dict:
        """Score choices when resolving card effects.

        Covers: PICK_OPTION, SACRIFICE, GIVE_AWAY, PICK_TARGET, ACCEPT_REJECT.
        For yes/no decisions, options are [True, False].
        """
        return {}

    def score_order(self, state: GameState, player: Player,
                    items: list, ctx: DecisionContext) -> list | dict:
        """Higher score = earlier in order."""
        return {}


# ---------------------------------------------------------------------------
# HeuristicStrategy
# ---------------------------------------------------------------------------
class HeuristicStrategy(Strategy):
    """Composes heuristics into a weighted-random strategy.

    Routes each Strategy method to the appropriate heuristic hook based on
    intent, then merges scores and picks via weighted random.
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
        """Merge multiple scoring results into a flat (option, score) list."""
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
        raw = [h.score_activate(state, player, actions, ctx)
               for h in self.heuristics]
        scores = self._merge_scores(raw)
        return self._weighted_pick(actions, scores)

    def choose_from(self, state, player, options, ctx):
        if ctx.intent in _DRAFT_INTENTS:
            raw = [h.score_draft(state, player, options, ctx)
                   for h in self.heuristics]
        else:
            raw = [h.score_resolution_choice(state, player, options, ctx)
                   for h in self.heuristics]
        scores = self._merge_scores(raw)
        return self._weighted_pick(options, scores)

    def choose_n(self, state, player, options, min_n, max_n, ctx):
        if ctx.intent in _DRAFT_INTENTS:
            raw = [h.score_draft(state, player, options, ctx)
                   for h in self.heuristics]
        else:
            raw = [h.score_resolution_choice(state, player, options, ctx)
                   for h in self.heuristics]
        scores = self._merge_scores(raw)

        n = self.rng.randint(min_n, min(max_n, len(options)))
        if n == 0:
            return []
        if n >= len(options):
            return list(options)

        picked = []
        remaining = list(options)
        for _ in range(n):
            if not remaining:
                break
            weights = [max(1.0 + self._lookup(scores, o), self.MIN_WEIGHT)
                       for o in remaining]
            choice = self.rng.choices(remaining, weights=weights, k=1)[0]
            picked.append(choice)
            idx = next(i for i, o in enumerate(remaining) if o is choice)
            remaining.pop(idx)
        return picked

    def choose_yes_no(self, state, player, ctx):
        yes, no = True, False
        raw = [h.score_resolution_choice(state, player, [yes, no], ctx)
               for h in self.heuristics]
        scores = self._merge_scores(raw)
        return self._weighted_pick([yes, no], scores)

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


def _leader_player(state, player):
    """Return the opponent with the most domain cards (or None)."""
    opponents = [p for p in state.players if p is not player]
    if not opponents:
        return None
    return max(opponents, key=lambda p: _player_domain_size(p))


# ---------------------------------------------------------------------------
# Auto-import heuristic modules to trigger @_register_heuristic
# ---------------------------------------------------------------------------
from heuristics import combat, drafting, scoring, strategic, events, targeting, synergy, card_hints  # noqa: E402, F401
