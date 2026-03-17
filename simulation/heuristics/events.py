"""Event-aware heuristics — score events and Orders by their payoff.

Generic no-op detection: every event handler's effects are checked against
current game state. If an effect can't fire (empty pile, no cards to discard,
etc.) it scores negative. If ALL effects are non-viable the card is a no-op.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import Heuristic, _register_heuristic
from heuristics.card_hints import (
    get_card_heuristics, Draw, Order, Take, Peek, Give, Cancel, Discard,
    Trigger,
)
from strategy import Intent

if TYPE_CHECKING:
    from state import GameState, Player
    from strategy import DecisionContext


# Event type → card_hints attribute name
_EVENT_ATTRS = {
    "order": "on_order",
    "brawl": "on_event_brawl",
    "rite": "on_event_rite",
    "feast": "on_event_feast",
    "harvest": "on_event_harvest",
    "rumour": "on_event_rumour",
}


def _effect_viable(effect, state, player) -> bool:
    """Can this effect actually fire given current game state?"""
    if isinstance(effect, Draw):
        return state.pile_remaining(effect.zone) > 0
    if isinstance(effect, Order):
        if effect.zone == "wheat":
            return len(state.fields) > 0
        if effect.zone == "tree":
            return len(state.season) > 0
        if effect.zone == "claw":
            return state.pile_remaining("claw") > 0
        if effect.zone == "coin":
            return state.pile_remaining("coin") > 0
        return True
    if isinstance(effect, Take):
        if effect.area == "season":
            return len(state.season) > 0
        if effect.area == "discard":
            return len(player.discard) > 0
        return True
    if isinstance(effect, Peek):
        return state.pile_remaining(effect.zone) > 0
    if isinstance(effect, Discard):
        return len(player.domain) > 1
    if isinstance(effect, Give):
        return len(player.domain) > 1
    if isinstance(effect, (Trigger, Cancel)):
        return True
    return True


def _score_effects(effects: list, state, player) -> float:
    """Score effects by value. Non-viable effects score negative."""
    score = 0.0
    for effect in effects:
        if not _effect_viable(effect, state, player):
            score -= 1.0
            continue
        if isinstance(effect, (Draw, Order, Take, Peek)):
            score += 1.0
        elif isinstance(effect, Give):
            score -= 0.5
        elif isinstance(effect, Discard):
            score -= 0.5
        elif isinstance(effect, Trigger):
            score += 0.5
    return score


def _card_event_score(card_name: str, event_attr: str, state, player) -> float:
    """Score a card's response to a specific event given current state."""
    ch = get_card_heuristics(card_name)
    if not ch:
        return 0.0
    effects = getattr(ch, event_attr, [])
    if not effects:
        return 0.0
    return _score_effects(effects, state, player)


def _event_payoff(state, player, event_type: str) -> float:
    """Net payoff for triggering an event. Checks effect viability."""
    attr = _EVENT_ATTRS.get(event_type)
    if not attr:
        return 0.0

    my_score = 0.0
    for card in player.domain:
        my_score += _card_event_score(card.name, attr, state, player)

    opp_score = 0.0
    for p in state.players:
        if p is player:
            continue
        for card in p.domain:
            opp_score += _card_event_score(card.name, attr, state, p)

    return my_score - opp_score


@_register_heuristic
class EventPayoff(Heuristic):
    """Score all events by their expected payoff — broadcast and targeted.

    Uses card hints to predict each card's response to an event, checking
    effect viability against current game state. Non-viable effects (empty
    piles, nothing to discard, etc.) score negative. This generically
    prevents wasting actions on no-op event triggers.
    """
    name = "event_payoff"

    def score_resolve(self, state, player, options, ctx):
        if ctx.intent != Intent.OPTION:
            return []

        scores = []
        for o in options:
            # Broadcast event choices (string options like "brawl", "rite")
            if isinstance(o, str) and o in _EVENT_ATTRS:
                payoff = _event_payoff(state, player, o)
                scores.append((o, payoff * 2.0))
                continue

            # Order actions — score by on_order effects viability
            if hasattr(o, "card") and o.card:
                name = getattr(o.card, "name", "")
                if not name:
                    continue
                score = _card_event_score(name, "on_order", state, player)
                if score != 0.0:
                    scores.append((o, score * 2.0))
                elif name == "Presence":
                    scores.append((o, 1.0))
                else:
                    # No hints at all — likely passive, penalise
                    scores.append((o, -3.0))

        return scores
