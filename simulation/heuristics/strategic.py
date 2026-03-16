"""Strategic win-condition heuristics."""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import (Heuristic, _register_heuristic,
                        _card_tag_score, _player_domain_size)
from strategy import Intent

if TYPE_CHECKING:
    from state import GameState, Player, Action
    from strategy import DecisionContext


# Zone → scoring tag mapping (mirrors engine._compute_winner)
_WIN_TAGS = {"claw": "Trophy", "tree": "Nature", "wheat": "Amenity"}


def _zone_advantage(state, player, zone: str) -> float:
    """How far ahead this player is on the zone's scoring axis.

    Returns positive if leading, 0 if tied for first, negative if behind.
    """
    tag = _WIN_TAGS.get(zone)
    if not tag:
        return 0.0
    my_count = player.count_tag(tag)
    best_opponent = max(
        (p.count_tag(tag) for p in state.players if p is not player),
        default=0
    )
    return my_count - best_opponent


def _zone_depletion(state, zone: str) -> float:
    """0.0 = full pile, 1.0 = fully depleted."""
    remaining = state.pile_remaining(zone)
    zc = state.zone_cards.get(zone)
    if not zc:
        return 0.0
    total = len(zc.pile)
    if total == 0:
        return 1.0
    return 1.0 - (remaining / total)


def _best_zone(state, player) -> str | None:
    """Return the zone where this player has the strongest lead."""
    best, best_adv = None, -999
    for zone in _WIN_TAGS:
        adv = _zone_advantage(state, player, zone)
        if adv > best_adv:
            best_adv = adv
            best = zone
    return best


@_register_heuristic
class PlayToWin(Heuristic):
    """Favor the zone where you're winning, push it to depletion.

    State-aware: evaluates each player's standing on all three scoring axes
    (Trophy/Nature/Amenity) and biases toward the zone where they lead.

    Behaviors:
    - Domain activation: prefer the zone where you have most of its win tag
    - Card gaining: prefer cards with the winning tag you're leading on
    - Scoring bonus scales with depletion (stronger push when zone is close)
    - When gaining cards, also considers which tags help the most
    """
    name = "play_to_win"

    def score_option(self, state, player, options, ctx):
        best = _best_zone(state, player)
        if not best:
            return {}

        tag = _WIN_TAGS[best]
        depletion = _zone_depletion(state, best)
        advantage = _zone_advantage(state, player, best)

        # Domain zone choice: strongly prefer our best zone
        if ctx.source == "Domain" and ctx.intent == Intent.PICK_OPTION:
            scores = {}
            for o in options:
                if isinstance(o, str) and o in _WIN_TAGS:
                    if o == best:
                        # Scale with how far ahead we are and how close to depletion
                        scores[o] = 2.0 + 2.0 * depletion + 0.5 * max(advantage, 0)
                    else:
                        other_adv = _zone_advantage(state, player, o)
                        if other_adv > 0:
                            # We also lead here — mild preference
                            scores[o] = 0.5 + 0.5 * other_adv
                        else:
                            scores[o] = -1.0
            return scores

        # When gaining cards, prefer cards with our winning tag
        if ctx.intent == Intent.GAIN:
            bonus = 1.5 + 2.0 * depletion
            return _card_tag_score(options, tag, bonus)

        # When sacrificing, protect cards with our winning tag
        if ctx.intent == Intent.SACRIFICE:
            penalty = -(1.5 + 2.0 * depletion)
            return _card_tag_score(options, tag, penalty)

        return {}

    def score_action(self, state, player, actions, ctx):
        best = _best_zone(state, player)
        if not best:
            return []

        tag = _WIN_TAGS[best]
        depletion = _zone_depletion(state, best)

        scores = []
        for a in actions:
            if not hasattr(a, "card") or not a.card:
                continue
            # Prefer activating cards with our winning tag
            if hasattr(a.card, "tags") and tag in a.card.tags:
                scores.append((a, 1.0 + 1.5 * depletion))
            # Prefer Domain activation (drafting) when our zone is close
            if hasattr(a.card, "name") and a.card.name == "Domain":
                if depletion > 0.5:
                    scores.append((a, 1.0 + depletion))
        return scores
