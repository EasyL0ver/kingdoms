"""Synergy heuristic — respect card interactions when drafting and ordering."""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import Heuristic, _register_heuristic
from heuristics.card_hints import (
    get_card_heuristics, _CARD_HEURISTICS_MAP,
    Draw, Order, Take, Peek, Trigger,
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


def _own_event_responder_count(player, event_type: str) -> int:
    """Count cards in domain that respond to this event type."""
    attr = _EVENT_ATTRS.get(event_type)
    if not attr:
        return 0
    count = 0
    for card in player.domain:
        ch = get_card_heuristics(card.name)
        if ch and getattr(ch, attr, []):
            count += 1
    return count


def _own_trigger_count(player, event_type: str) -> int:
    """Count cards in domain that trigger this event type."""
    count = 0
    for card in player.domain:
        ch = get_card_heuristics(card.name)
        if not ch:
            continue
        for effect in ch.on_order:
            if isinstance(effect, Trigger) and effect.event == event_type:
                count += 1
    return count


def _scaling_synergy(player, card_ch) -> float:
    """Score how well a card's scaling effects are powered by existing domain."""
    score = 0.0
    all_effects = (
        card_ch.on_order
        + card_ch.on_event_brawl + card_ch.on_event_feast
        + card_ch.on_event_rite + card_ch.on_event_harvest
        + card_ch.on_event_rumour + card_ch.on_dawn
    )
    for effect in all_effects:
        sw = getattr(effect, "scales_with", "")
        if sw:
            tag_count = player.count_tag(sw)
            score += tag_count * 1.0
    return score


def _event_chain_synergy(player, card_ch) -> float:
    """Score how well a card chains with existing trigger/responder pairs.

    - Card triggers event X and we have responders for X → good
    - Card responds to event X and we have triggers for X → good
    """
    score = 0.0

    # Card triggers events — do we have responders?
    for effect in card_ch.on_order + card_ch.on_dawn:
        if isinstance(effect, Trigger):
            if effect.scope in ("self", "all"):
                responders = _own_event_responder_count(player, effect.event)
                score += responders * 1.5

    # Card responds to events — do we have triggers?
    for event_type, attr in _EVENT_ATTRS.items():
        effects = getattr(card_ch, attr, [])
        if effects:
            triggers = _own_trigger_count(player, event_type)
            score += triggers * 1.5

    return score


def _tag_enabler_synergy(player, card_name: str, card_tags: list[str]) -> float:
    """Score how well this card's tags enable scaling cards we already own."""
    score = 0.0
    for domain_card in player.domain:
        ch = get_card_heuristics(domain_card.name)
        if not ch:
            continue
        all_effects = (
            ch.on_order + ch.on_event_brawl + ch.on_event_feast
            + ch.on_event_rite + ch.on_event_harvest + ch.on_event_rumour
            + ch.on_dawn
        )
        for effect in all_effects:
            sw = getattr(effect, "scales_with", "")
            if sw and sw in card_tags:
                score += 2.0
    return score


@_register_heuristic
class Synergy(Heuristic):
    """Draft and activate cards that synergize with your existing domain.

    Considers:
    - Event chains: trigger/responder pairs between your cards
    - Tag scaling: cards that grow stronger with tags you already have
    - Tag enablers: cards whose tags power up scaling cards you own
    """
    name = "synergy"

    def score_resolve(self, state, player, options, ctx):
        if ctx.intent == Intent.GAIN:
            scores = []
            for o in options:
                if not hasattr(o, "name"):
                    continue
                ch = get_card_heuristics(o.name)
                total = 0.0

                if ch:
                    total += _scaling_synergy(player, ch)
                    total += _event_chain_synergy(player, ch)

                if hasattr(o, "tags"):
                    total += _tag_enabler_synergy(player, o.name, o.tags)

                if total > 0:
                    scores.append((o, total))
            return scores

        if ctx.intent in (Intent.DISCARD, Intent.GIVE_AWAY):
            # Protect synergistic cards (negate gain scores)
            scores = []
            for o in options:
                if not hasattr(o, "name"):
                    continue
                ch = get_card_heuristics(o.name)
                total = 0.0

                if ch:
                    total += _scaling_synergy(player, ch)
                    total += _event_chain_synergy(player, ch)

                if hasattr(o, "tags"):
                    total += _tag_enabler_synergy(player, o.name, o.tags)

                if total > 0:
                    scores.append((o, -total))
            return scores

        if ctx.intent == Intent.OPTION:
            # Prefer ordering cards with active synergies (turn actions)
            scores = []
            for a in options:
                if not hasattr(a, "card") or not a.card:
                    continue
                ch = get_card_heuristics(getattr(a.card, "name", ""))
                if not ch:
                    continue

                total = 0.0
                total += _scaling_synergy(player, ch)
                total += _event_chain_synergy(player, ch)

                if total > 0:
                    scores.append((a, total))
            return scores

        return {}
