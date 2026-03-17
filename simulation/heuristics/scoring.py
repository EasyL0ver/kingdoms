"""Scoring-focused heuristics (card value and tag preferences)."""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import (Heuristic, _register_heuristic,
                        _card_tag_score, _claw_depletion_ratio)
from strategy import Intent

if TYPE_CHECKING:
    from state import GameState, Player
    from strategy import DecisionContext


@_register_heuristic
class PreferTrophies(Heuristic):
    """Bias toward Trophy-tagged cards when gaining.

    State-aware: bonus increases as the claw pile depletes (end-game trophy race).
    """
    name = "prefer_trophies"

    def score_resolve(self, state, player, options, ctx):
        if ctx.intent == Intent.GAIN:
            depletion = _claw_depletion_ratio(state)
            bonus = 2.0 + 3.0 * depletion  # 2.0 early → 5.0 late
            return _card_tag_score(options, "Trophy", bonus)

        if ctx.intent in (Intent.DISCARD, Intent.GIVE_AWAY):
            # Protect trophies (negate gain scores)
            depletion = _claw_depletion_ratio(state)
            bonus = 2.0 + 3.0 * depletion
            return _card_tag_score(options, "Trophy", -bonus)

        if ctx.intent == Intent.OPTION:
            scores = []
            for a in options:
                if hasattr(a, "card") and a.card and hasattr(a.card, "tags"):
                    if "Trophy" in a.card.tags:
                        depletion = _claw_depletion_ratio(state)
                        scores.append((a, 1.5 + 2.0 * depletion))
            return scores

        return {}


@_register_heuristic
class SpiritualFocus(Heuristic):
    """Favor Spiritual cards and Rites.

    State-aware: increased preference when player already has Spiritual cards
    (synergy bonus).
    """
    name = "spiritual_focus"

    def _spiritual_count(self, player) -> int:
        return sum(1 for c in player.domain if "Spiritual" in c.tags)

    def score_resolve(self, state, player, options, ctx):
        if ctx.intent == Intent.GAIN:
            synergy = 1.0 + 0.5 * self._spiritual_count(player)
            return _card_tag_score(options, "Spiritual", synergy)

        if ctx.intent in (Intent.DISCARD, Intent.GIVE_AWAY):
            # Protect spiritual cards (negate gain + explicit protection)
            synergy = 1.0 + 0.5 * self._spiritual_count(player)
            scores = _card_tag_score(options, "Spiritual", -synergy)
            for o in options:
                if hasattr(o, "tags") and "Spiritual" in o.tags:
                    scores.append((o, -2.0))
            return scores

        if ctx.intent == Intent.OPTION:
            scores = []
            # Prefer rite events
            for o in options:
                if isinstance(o, str) and o == "rite":
                    scores.append((o, 2.0 + 0.5 * self._spiritual_count(player)))
            # Prefer ordering Spiritual cards (turn actions)
            for a in options:
                if hasattr(a, "card") and a.card and hasattr(a.card, "tags"):
                    if "Spiritual" in a.card.tags:
                        scores.append((a, 1.5 + 0.5 * self._spiritual_count(player)))
            return scores

        return {}
