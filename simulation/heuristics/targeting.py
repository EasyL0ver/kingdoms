"""Targeting heuristics — smart opponent selection and event-aware activation."""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import Heuristic, _register_heuristic
from heuristics.card_hints import (
    get_card_heuristics, Draw, Activate, Take, Peek, Give, Cancel, Discard,
    Trigger,
)
from strategy import Intent

if TYPE_CHECKING:
    from state import GameState, Player
    from strategy import DecisionContext


# Tags that map to win conditions
_WIN_TAGS = {"Trophy": "claw", "Nature": "tree", "Amenity": "wheat"}

# Event type → card_hints attribute name
_EVENT_ATTRS = {
    "brawl": "on_event_brawl",
    "rite": "on_event_rite",
    "feast": "on_event_feast",
    "harvest": "on_event_harvest",
    "rumour": "on_event_rumour",
}


def _threat_score(player) -> float:
    """How close a player is to winning — max across all win-condition axes."""
    return max(
        player.count_tag("Trophy"),
        player.count_tag("Nature"),
        player.count_tag("Amenity"),
    )


def _negative_responders(player, event_type: str) -> int:
    """Count how many negative event responders a player has (Give, Discard)."""
    attr = _EVENT_ATTRS.get(event_type)
    if not attr:
        return 0
    count = 0
    for card in player.domain:
        ch = get_card_heuristics(card.name)
        if not ch:
            continue
        for effect in getattr(ch, attr, []):
            if isinstance(effect, (Give, Discard)):
                count += 1
    return count


def _positive_responders(player, event_type: str) -> int:
    """Count how many positive event responders a player has (Draw, Activate, Take, Peek)."""
    attr = _EVENT_ATTRS.get(event_type)
    if not attr:
        return 0
    count = 0
    for card in player.domain:
        ch = get_card_heuristics(card.name)
        if not ch:
            continue
        for effect in getattr(ch, attr, []):
            if isinstance(effect, (Draw, Activate, Take, Peek)):
                count += 1
    return count


@_register_heuristic
class TargetLeader(Heuristic):
    """Target the opponent closest to winning.

    Prefers targeting opponents with the highest win-condition tag count.
    When an opponent has many negative event responders (Raid, Scavenge),
    factors that in as extra incentive to brawl them.
    """
    name = "target_leader"

    def score_resolution_choice(self, state, player, options, ctx):
        if ctx.intent != Intent.PICK_TARGET:
            return {}

        scores = []
        for o in options:
            if not hasattr(o, "count_tag"):
                continue
            if o is player:
                continue

            # Base: threat level (closest to winning)
            threat = _threat_score(o)
            score = threat * 1.5

            # Bonus: target has negative Brawl responders (Raid, Scavenge)
            neg = _negative_responders(o, "brawl")
            score += neg * 1.0

            scores.append((o, score))

        return scores

    def score_activate(self, state, player, actions, ctx):
        """Prefer activating cards that trigger events hurting opponents."""
        scores = []
        for a in actions:
            if not hasattr(a, "card") or not a.card:
                continue
            ch = get_card_heuristics(getattr(a.card, "name", ""))
            if not ch:
                continue

            # Check for Trigger effects in on_activate
            for effect in ch.on_activate:
                if not isinstance(effect, Trigger):
                    continue

                if effect.scope == "target":
                    # Brawl targeting — good if opponents have negative responders
                    best_neg = max(
                        (_negative_responders(p, effect.event), _threat_score(p))
                        for p in state.players if p is not player
                    )
                    neg_count, threat = best_neg
                    if neg_count > 0:
                        scores.append((a, neg_count * 1.5 + threat * 0.5))

                elif effect.scope in ("all", "cultural"):
                    # Event fires in many domains — good if opponents have more
                    # negative responders than us
                    my_neg = _negative_responders(player, effect.event)
                    opp_neg = sum(
                        _negative_responders(p, effect.event)
                        for p in state.players if p is not player
                    )
                    my_pos = _positive_responders(player, effect.event)
                    opp_pos = sum(
                        _positive_responders(p, effect.event)
                        for p in state.players if p is not player
                    )
                    # Net: our positives + their negatives - our negatives - their positives
                    net = (my_pos + opp_neg) - (my_neg + opp_pos)
                    if net != 0:
                        scores.append((a, net * 1.5))

                elif effect.scope == "self":
                    # Event fires in our domain only — good if we have positive responders
                    my_pos = _positive_responders(player, effect.event)
                    my_neg = _negative_responders(player, effect.event)
                    net = my_pos - my_neg
                    if net != 0:
                        scores.append((a, net * 1.5))

        return scores
