"""Event-aware heuristics — trigger events only when there's a payoff."""
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


# Event type → card_hints attribute name
_EVENT_ATTRS = {
    "brawl": "on_event_brawl",
    "rite": "on_event_rite",
    "feast": "on_event_feast",
    "harvest": "on_event_harvest",
    "rumour": "on_event_rumour",
}


def _count_responders(player, event_type: str) -> tuple[int, int]:
    """Count positive and negative event responders in a player's domain.

    Returns (positive_count, negative_count).
    Positive: Draw, Activate, Take, Peek, Cancel
    Negative: Give, Discard
    """
    attr = _EVENT_ATTRS.get(event_type)
    if not attr:
        return 0, 0

    pos, neg = 0, 0
    for card in player.domain:
        ch = get_card_heuristics(card.name)
        if not ch:
            continue
        effects = getattr(ch, attr, [])
        if not effects:
            continue
        for effect in effects:
            if isinstance(effect, (Draw, Activate, Take, Peek)):
                pos += 1
            elif isinstance(effect, (Give, Discard)):
                neg += 1
            elif isinstance(effect, Cancel):
                # Cancel is context-dependent — count as neutral here
                pass
    return pos, neg


def _event_payoff(state, player, event_type: str) -> float:
    """Net payoff for triggering an event.

    Positive = we benefit more than opponents.
    Considers our positive responders vs our negative responders,
    and opponents' positive responders vs their negative responders.
    """
    my_pos, my_neg = _count_responders(player, event_type)
    my_score = my_pos - my_neg

    opp_score = 0.0
    for p in state.players:
        if p is player:
            continue
        opp_pos, opp_neg = _count_responders(p, event_type)
        # Opponent gaining is bad for us, opponent losing is good for us
        opp_score += opp_pos - opp_neg

    # Our benefit minus opponents' benefit
    return my_score - opp_score


@_register_heuristic
class EventPayoff(Heuristic):
    """Only trigger events when you have more to gain than opponents.

    Evaluates each player's domain for event responders, comparing positive
    effects (draws, activations) against negative effects (gives, discards).
    Favors triggering events where the player's net payoff exceeds opponents'.
    """
    name = "event_payoff"

    def score_resolution_choice(self, state, player, options, ctx):
        if ctx.intent != Intent.PICK_OPTION:
            return {}

        scores = {}
        for o in options:
            if not isinstance(o, str):
                continue
            if o not in _EVENT_ATTRS:
                continue
            payoff = _event_payoff(state, player, o)
            # Scale: strong signal so it meaningfully biases the choice
            scores[o] = payoff * 2.0

        return scores

    def score_activate(self, state, player, actions, ctx):
        """Prefer activating cards that trigger favorable events."""
        scores = []
        for a in actions:
            if not hasattr(a, "card") or not a.card:
                continue
            ch = get_card_heuristics(getattr(a.card, "name", ""))
            if not ch:
                continue
            # Check if activation triggers events indirectly
            # (cards whose on_activate includes event-triggering aren't
            # directly encoded, but we can check if the card has event
            # responders that benefit us)
        return scores
