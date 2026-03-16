"""Targeting heuristics — smart opponent selection and event-aware activation.

Two complementary heuristics:
  target_event:   who to target with events (Brawl, Rite, etc.)
                  + activation scoring for event-triggering cards
  target_effect:  who to target with non-event effects (placement, discard, take)
"""
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


def _cancel_responders(player, event_type: str) -> int:
    """Count how many Cancel effects a player has for an event type."""
    attr = _EVENT_ATTRS.get(event_type)
    if not attr:
        return 0
    count = 0
    for card in player.domain:
        ch = get_card_heuristics(card.name)
        if not ch:
            continue
        for effect in getattr(ch, attr, []):
            if isinstance(effect, Cancel):
                count += 1
    return count


def _get_card_tags(card_name: str) -> list[str]:
    """Look up a card's tags from the behavior registry."""
    from cards import get_behavior
    beh = get_behavior(card_name)
    return getattr(beh, "tags", [])


# -----------------------------------------------------------------------
# Heuristic 1: Event targeting
# -----------------------------------------------------------------------
@_register_heuristic
class TargetEvent(Heuristic):
    """Smart event targeting — who to hit with Brawl/Rite/etc.

    Analyses responder cards in each opponent's domain:
      - negative responders (Give, Discard) → good to brawl them
      - cancel responders (Eldership, Militia) → penalise (brawl gets blocked)
      - threat as tiebreaker
    Also scores activation of event-triggering cards.
    """
    name = "target_event"

    def score_resolution_choice(self, state, player, options, ctx):
        if ctx.intent != Intent.PICK_TARGET:
            return {}
        if "Brawl" not in ctx.consequence:
            return {}

        scores = []
        for o in options:
            if not hasattr(o, "count_tag") or o is player:
                continue
            neg = _negative_responders(o, "brawl")
            can = _cancel_responders(o, "brawl")
            threat = _threat_score(o)
            score = neg * 2.0 - can * 1.5 + threat * 0.5
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

            for effect in ch.on_activate:
                if not isinstance(effect, Trigger):
                    continue

                if effect.scope == "target":
                    best_neg = max(
                        (_negative_responders(p, effect.event), _threat_score(p))
                        for p in state.players if p is not player
                    )
                    neg_count, threat = best_neg
                    if neg_count > 0:
                        scores.append((a, neg_count * 1.5 + threat * 0.5))

                elif effect.scope in ("all", "cultural"):
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
                    net = (my_pos + opp_neg) - (my_neg + opp_pos)
                    if net != 0:
                        scores.append((a, net * 1.5))

                elif effect.scope == "self":
                    my_pos = _positive_responders(player, effect.event)
                    my_neg = _negative_responders(player, effect.event)
                    net = my_pos - my_neg
                    if net != 0:
                        scores.append((a, net * 1.5))

        return scores


# -----------------------------------------------------------------------
# Heuristic 2: Effect targeting
# -----------------------------------------------------------------------
@_register_heuristic
class TargetEffect(Heuristic):
    """Smart non-event targeting — placement, forced discard, demands.

    Categorises PICK_TARGET decisions by consequence:
      - Placement/gifts:  giving win-tag card → target weakest (waste the tag)
                          giving negative card → target strongest
      - Forced discard:   target highest threat-per-card (few strong cards)
      - Demands/takes:    target whoever has most valuable stuff
    """
    name = "target_effect"

    def score_resolution_choice(self, state, player, options, ctx):
        if ctx.intent != Intent.PICK_TARGET:
            return {}
        # Skip event targeting (handled by target_event)
        if "Brawl" in ctx.consequence:
            return {}

        consequence = ctx.consequence
        scores = []

        # --- Placement: card placed in opponent's domain ---
        if "placed" in consequence:
            tags = _get_card_tags(ctx.source)
            has_win_tag = any(t in _WIN_TAGS for t in tags)
            for o in options:
                if not hasattr(o, "count_tag") or o is player:
                    continue
                threat = _threat_score(o)
                if has_win_tag:
                    # Giving Trophy/Nature/Amenity → target weakest
                    score = -threat * 2.0
                else:
                    score = threat * 2.0
                scores.append((o, score))

        # --- Gift: opponent receives a specific card ---
        elif "receives" in consequence:
            # Card name is after "receives "
            card_name = consequence.split("receives ")[-1]
            tags = _get_card_tags(card_name)
            has_win_tag = any(t in _WIN_TAGS for t in tags)
            for o in options:
                if not hasattr(o, "count_tag") or o is player:
                    continue
                threat = _threat_score(o)
                if has_win_tag:
                    score = -threat * 2.0
                else:
                    score = threat * 2.0
                scores.append((o, score))

        # --- Forced discard: target highest quality (few but strong cards) ---
        elif "discard" in consequence.lower():
            for o in options:
                if not hasattr(o, "count_tag") or o is player:
                    continue
                threat = _threat_score(o)
                card_count = max(len(o.domain), 1)
                quality = threat / card_count
                score = quality * 3.0 + threat * 0.5
                scores.append((o, score))

        # --- Demand: they offer us a card ---
        elif "offer" in consequence:
            for o in options:
                if not hasattr(o, "count_tag") or o is player:
                    continue
                score = len(o.domain) * 0.5 + _threat_score(o) * 1.0
                scores.append((o, score))

        # --- Fallback: target strongest ---
        else:
            for o in options:
                if not hasattr(o, "count_tag") or o is player:
                    continue
                scores.append((o, _threat_score(o) * 1.0))

        return scores
