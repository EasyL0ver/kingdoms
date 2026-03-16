"""Strategic win-condition heuristics."""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import Heuristic, _register_heuristic, _card_tag_score
from heuristics.card_hints import get_card_heuristics
from strategy import Intent

if TYPE_CHECKING:
    from state import GameState, Player, Action
    from strategy import DecisionContext


# Zone → scoring tag mapping (mirrors engine._compute_winner)
_WIN_TAGS = {"claw": "Trophy", "tree": "Nature", "wheat": "Amenity"}


def _zone_advantage(state, player, zone: str) -> float:
    """How far ahead this player is on the zone's scoring axis."""
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


def _card_helps_zone(card_name: str, zone: str) -> bool:
    """Check if a card draws from or gates the given zone."""
    ch = get_card_heuristics(card_name)
    if not ch:
        return False
    return zone in ch.draws or zone in ch.gates


@_register_heuristic
class PlayToWin(Heuristic):
    """Favor the zone where you're winning, push it to depletion.

    State-aware: evaluates each player's standing on all three scoring axes
    (Trophy/Nature/Amenity) and biases toward the zone where they lead.

    Uses CardHeuristics metadata to identify which cards draw from or gate
    the target zone, giving them activation and drafting priority.
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
                        scores[o] = 2.0 + 2.0 * depletion + 0.5 * max(advantage, 0)
                    else:
                        other_adv = _zone_advantage(state, player, o)
                        if other_adv > 0:
                            scores[o] = 0.5 + 0.5 * other_adv
                        else:
                            scores[o] = -1.0
            return scores

        # When gaining cards, prefer cards with our winning tag OR that deplete our zone
        if ctx.intent == Intent.GAIN:
            bonus = 1.5 + 2.0 * depletion
            scores = _card_tag_score(options, tag, bonus)
            for o in options:
                if hasattr(o, "name") and _card_helps_zone(o.name, best):
                    scores.append((o, 1.0 + 1.5 * depletion))
            return scores

        # When sacrificing, protect cards that help our zone
        if ctx.intent == Intent.SACRIFICE:
            penalty = -(1.5 + 2.0 * depletion)
            scores = _card_tag_score(options, tag, penalty)
            for o in options:
                if hasattr(o, "name") and _card_helps_zone(o.name, best):
                    scores.append((o, -(1.0 + depletion)))
            return scores

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
            card = a.card
            # Prefer activating cards with our winning tag
            if hasattr(card, "tags") and tag in card.tags:
                scores.append((a, 1.0 + 1.5 * depletion))
            # Prefer cards that draw from or gate our zone
            if hasattr(card, "name") and _card_helps_zone(card.name, best):
                scores.append((a, 2.0 + 2.0 * depletion))
            # Prefer Domain activation when our zone is close
            if hasattr(card, "name") and card.name == "Domain":
                if depletion > 0.5:
                    scores.append((a, 1.0 + depletion))
        return scores
