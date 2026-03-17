"""Strategic win-condition heuristics."""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import Heuristic, _register_heuristic, _card_tag_score
from heuristics.card_hints import get_card_heuristics, Draw, Order, Take, Peek, Trigger
from strategy import Intent

if TYPE_CHECKING:
    from state import GameState, Player
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
    """Return the zone where this player is strictly ahead of all opponents.

    Only returns a zone if advantage > 0 (player leads). Among multiple
    leading zones, picks the one with the biggest lead.
    Returns None if the player doesn't lead on any axis.
    """
    best, best_adv = None, 0  # threshold: must be strictly > 0
    for zone in _WIN_TAGS:
        adv = _zone_advantage(state, player, zone)
        if adv > best_adv:
            best_adv = adv
            best = zone
    return best


def _effect_zone(effect) -> str | None:
    """Extract the zone from an effect, if it has one."""
    if isinstance(effect, (Draw, Order, Take, Peek)):
        zone = effect.zone if isinstance(effect, (Draw, Order, Peek)) else effect.area
        return zone
    return None


def _card_all_zones(ch) -> set[str]:
    """Collect all zones a card interacts with across all hooks."""
    all_effects = (
        ch.on_order
        + ch.on_event_brawl + ch.on_event_feast + ch.on_event_rite
        + ch.on_event_harvest + ch.on_event_rumour
        + ch.on_dawn
    )
    zones = set()
    for effect in all_effects:
        z = _effect_zone(effect)
        if z:
            zones.add(z)
    return zones


def _card_helps_zone(card_name: str, zone: str) -> bool:
    """Check if a card interacts with the given zone via any hook."""
    ch = get_card_heuristics(card_name)
    if not ch:
        return False
    return zone in _card_all_zones(ch)


def _card_zone_score(card_name: str, best_zone: str, state, player) -> float:
    """Score a card based on how well it aligns with the player's winning zone.

    Positive if it helps the best zone. Negative if it also interacts with
    zones where opponents lead (accelerating an unfavorable win condition).
    """
    ch = get_card_heuristics(card_name)
    if not ch:
        return 0.0

    zones = _card_all_zones(ch)
    score = 0.0
    if best_zone in zones:
        score += 1.0

    # Penalize interaction with zones where we're NOT leading
    for zone in zones:
        if zone == best_zone:
            continue
        if zone in _WIN_TAGS:
            adv = _zone_advantage(state, player, zone)
            if adv < 0:
                score -= 1.5

    return score


@_register_heuristic
class PlayToWin(Heuristic):
    """Favor the zone where you're winning, push it to depletion.

    State-aware: evaluates each player's standing on all three scoring axes
    (Trophy/Nature/Amenity) and biases toward the zone where they lead.

    Uses CardHeuristics metadata (on_order, on_event_*, on_dawn)
    to identify which cards interact with the target zone.
    """
    name = "play_to_win"

    def score_resolve(self, state, player, options, ctx):
        best = _best_zone(state, player)
        if not best:
            return {}

        tag = _WIN_TAGS[best]
        depletion = _zone_depletion(state, best)

        if ctx.intent == Intent.GAIN:
            bonus = 1.5 + 2.0 * depletion
            scores = _card_tag_score(options, tag, bonus)
            owned_names = {c.name for c in player.domain}
            for o in options:
                if hasattr(o, "name"):
                    zscore = _card_zone_score(o.name, best, state, player)
                    if zscore > 0.0:
                        multiplier = 2.0 if o.name not in owned_names else 1.0
                        scores.append((o, zscore * multiplier * (1.0 + depletion)))
                    elif zscore < 0.0:
                        scores.append((o, zscore * (1.0 + depletion)))
            return scores

        if ctx.intent in (Intent.DISCARD, Intent.GIVE_AWAY):
            # Protect cards aligned with winning zone (negate gain scores)
            penalty = -(1.5 + 2.0 * depletion)
            scores = _card_tag_score(options, tag, penalty)
            for o in options:
                if hasattr(o, "name"):
                    zscore = _card_zone_score(o.name, best, state, player)
                    if zscore != 0.0:
                        scores.append((o, -zscore * (1.0 + depletion)))
            return scores

        if ctx.intent == Intent.OPTION:
            advantage = _zone_advantage(state, player, best)
            scores = []

            # Zone selection
            has_zone_options = any(
                isinstance(o, str) and o in _WIN_TAGS for o in options
            )
            if has_zone_options:
                for o in options:
                    if not isinstance(o, str) or o not in _WIN_TAGS:
                        continue
                    if o == best:
                        scores.append((o, 2.0 + 2.0 * depletion + 0.5 * max(advantage, 0)))
                    else:
                        other_adv = _zone_advantage(state, player, o)
                        if other_adv > 0:
                            scores.append((o, 0.5 + 0.5 * other_adv))
                        else:
                            scores.append((o, -1.0))
            else:
                for o in options:
                    if not isinstance(o, str):
                        continue
                    if o == "wheat" and best == "wheat":
                        scores.append((o, 2.0 + depletion))
                    elif o == "scry" and best == "tree":
                        scores.append((o, 1.5))
                    elif o == "rite":
                        scores.append((o, 0.5))

            # Ordering cards that help the winning zone (turn actions)
            for a in options:
                if not hasattr(a, "card") or not a.card:
                    continue
                name = getattr(a.card, "name", "")
                if not name:
                    continue
                zscore = _card_zone_score(name, best, state, player)
                if zscore != 0.0:
                    scores.append((a, zscore * (1.5 + depletion)))

            return scores

        return {}
