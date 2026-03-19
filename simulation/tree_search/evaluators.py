"""Evaluators — score a board position from a player's perspective.

Each evaluator produces a partial score; they're summed together.
The tree search uses: my_score - 0.3 * best_opponent_score.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import GameState, Player


class Evaluator(ABC):
    """Scores a board position from a player's perspective."""
    name: str = ""

    @abstractmethod
    def score(self, state: GameState, player: Player) -> float: ...


_REGISTRY: dict[str, type[Evaluator]] = {}


def _register(cls):
    _REGISTRY[cls.name] = cls
    return cls


def get_evaluator(name: str) -> Evaluator:
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise ValueError(f"Unknown evaluator '{name}'. Available: {available}")
    return _REGISTRY[name]()


def list_evaluators() -> list[str]:
    return sorted(_REGISTRY.keys())


def evaluate(state: GameState, player: Player,
             evaluators: list[Evaluator] | None = None) -> float:
    """Score a position: own score minus best opponent's score (weighted)."""
    if not evaluators:
        evaluators = [get_evaluator(n) for n in _REGISTRY]
    my_score = sum(e.score(state, player) for e in evaluators)
    best_opp = max(
        (sum(e.score(state, p) for e in evaluators)
         for p in state.players if p is not player),
        default=0.0,
    )
    return my_score - 0.3 * best_opp


# ── Built-in evaluators ──────────────────────────────────────────────


@_register
class TagValue(Evaluator):
    """Score cards by their tag value — victory tags high, Discontent negative."""
    name = "tag_value"

    def score(self, state, player):
        s = 0.0
        s += player.count_tag("Trophy") * 3.0
        s += player.count_tag("Nature") * 3.0
        s += player.count_tag("Amenity") * 3.0
        s += player.count_tag("Wealth") * 3.0
        s += player.count_tag("Religion") * 3.0
        s += player.count_tag("Chivalry") * 3.0
        s += player.count_tag("Knowledge") * 1.5
        s += player.count_tag("Spiritual") * 1.0
        s += len(player.domain) * 0.5
        s -= player.count_tag("Discontent") * 3.0
        return s


@_register
class ZoneAccess(Evaluator):
    """Reward having access to wheat/coin/candle/sword zones."""
    name = "zone_access"

    def score(self, state, player):
        s = 0.0
        if player.has_wheat_access():
            s += 2.0
        if player.has_coin_access():
            s += 2.0
        if player.has_candle_access():
            s += 2.5
        if player.has_sword_access():
            s += 2.5
        return s


@_register
class CandleMomentum(Evaluator):
    """Reward candle commitment — Clergy + Religion tags + known Revelation."""
    name = "candle_momentum"

    def score(self, state, player):
        s = 0.0
        has_clergy = player.has_card("Clergy")
        religion_count = player.count_tag("Religion")
        candle_remaining = state.pile_remaining("candle") + len(state.revelation)

        if candle_remaining <= 0:
            return 0.0

        if state.revelation:
            if has_clergy:
                s += 3.0
            else:
                s += 1.0

        if has_clergy and religion_count >= 2:
            s += religion_count * 1.5

        return s


@_register
class EndgameAwareness(Evaluator):
    """Discourage ending the game on an axis where we're tied or behind."""
    name = "endgame_awareness"

    def score(self, state, player):
        s = 0.0
        win_tags = {
            "claw": "Trophy", "tree": "Nature", "wheat": "Amenity",
            "coin": "Wealth", "candle": "Religion", "sword": "Chivalry",
        }
        for deck, tag in win_tags.items():
            remaining = state.pile_remaining(deck)
            if deck == "tree":
                remaining += len(state.season)
            elif deck == "wheat":
                remaining += len(state.fields)
            elif deck == "coin":
                remaining += len(state.opportunities)
            elif deck == "candle":
                remaining += len(state.revelation)
            elif deck == "sword":
                remaining += len(state.tourney)

            if remaining > 15:
                continue

            my_count = player.count_tag(tag)
            max_opp = max(
                (p.count_tag(tag) for p in state.players if p is not player),
                default=0,
            )
            lead = my_count - max_opp
            danger = max(0, 15 - remaining) / 15.0

            if lead > 0:
                s += lead * danger * 4.0
            elif lead == 0:
                s -= danger * 6.0
            else:
                s -= danger * 10.0
        return s


@_register
class OpponentBurden(Evaluator):
    """Reward opponent Discontent when we have brawl-triggering cards."""
    name = "opponent_burden"

    BRAWL_ENABLERS = {"Warband", "Racketeering"}

    def score(self, state, player):
        has_enabler = any(c.name in self.BRAWL_ENABLERS for c in player.domain)
        if not has_enabler:
            return 0.0
        opp_discontent = sum(
            opp.count_tag("Discontent") for opp in state.other_players(player)
        )
        return opp_discontent * 0.15


@_register
class CardSynergy(Evaluator):
    """Score cards based on whether their synergies are active."""
    name = "card_synergy"

    def score(self, state, player):
        s = 0.0
        has_mobs = player.count_tag("Mob") > 0
        has_nature = player.count_tag("Nature")
        has_discontent = player.count_tag("Discontent")
        discard_size = len(player.discard)
        claw_remaining = state.pile_remaining("claw")
        has_season = len(state.season) > 0
        has_fields = len(state.fields) > 0

        for card in player.domain:
            match card.name:
                # ── Claw ──
                case "Tyranny":
                    if has_discontent > 0 and claw_remaining > 0:
                        s += 2.0 + has_discontent * 1.0
                case "Chiefdom":
                    if has_mobs:
                        s += 2.5
                case "Outriders":
                    if claw_remaining >= 3:
                        s += 2.0
                    elif claw_remaining > 0:
                        s += 0.5
                case "Ransack":
                    if len(player.domain) > 1 and (claw_remaining > 0 or has_season):
                        s += 1.5
                case "Blood Offering":
                    spiritual = player.count_tag("Spiritual")
                    if len(player.domain) > 1:
                        s += 0.5 + spiritual * 0.5
                case "Warband":
                    s += player.count_tag("Mob") * 0.5
                case "Racketeering":
                    if any(len(p.domain) > 0 for p in state.other_players(player)):
                        s += 1.0

                # ── Tree ──
                case "Vigil":
                    allies_with_kinship = sum(1 for p in state.other_players(player)
                                              if p.has_card("Kinship"))
                    if allies_with_kinship > 0 and discard_size > 0:
                        s += min(allies_with_kinship, discard_size) * 1.5
                case "Floods":
                    other_floods = sum(1 for c in player.domain
                                       if c.name == "Floods") - 1
                    s += 1.5  # Season refill is always good
                    if other_floods > 0:
                        s += 1.0  # Brawl shield is great
                case "Regrowth":
                    nature_in_discard = sum(1 for c in player.discard if c.has_tag("Nature"))
                    s += nature_in_discard * 1.5
                case "Hospitality":
                    partners = sum(1 for p in state.other_players(player)
                                   if p.has_card("Kinship"))
                    if partners > 0:
                        s += 2.5
                case "Forage":
                    s += 1.5
                case "Worship of the Dawn":
                    if discard_size > 0:
                        dusk_exists = any(c.name == "Worship of the Dusk"
                                          for p in state.players for c in p.domain)
                        s += 2.0 if dusk_exists else 1.5
                case "Worship of the Hearth":
                    kinship_players = sum(1 for p in state.players
                                          if p.has_card("Kinship"))
                    s += kinship_players * 1.5
                case "Worship of the Dusk":
                    dawn_exists = any(c.name == "Worship of the Dawn"
                                      for p in state.players for c in p.domain)
                    s += 2.5 if dawn_exists else 1.5
                case "Sacred Grove":
                    s += 1.0 + player.count_tag("Spiritual") * 0.3
                case "Well":
                    if has_season:
                        s += 2.0

                # ── Wheat ──
                case "Sowing":
                    if has_nature >= 2 and has_fields:
                        s += 2.0
                case "Compost":
                    has_harvest_discard = any(c.name == "Harvest" for c in player.discard)
                    if has_harvest_discard and has_fields:
                        s += 2.5

        return s
