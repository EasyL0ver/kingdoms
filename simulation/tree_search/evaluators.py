"""Board position evaluators — score a game state from a player's perspective."""
from __future__ import annotations
from abc import ABC, abstractmethod
from state import GameState, Player


class Evaluator(ABC):
    """Scores a board position from a player's perspective."""
    name: str = ""

    @abstractmethod
    def score(self, state: GameState, player: Player) -> float:
        ...


_EVALUATOR_REGISTRY: dict[str, type[Evaluator]] = {}


def _register_evaluator(cls):
    _EVALUATOR_REGISTRY[cls.name] = cls
    return cls


def get_evaluator(name: str) -> Evaluator:
    if name not in _EVALUATOR_REGISTRY:
        available = ", ".join(sorted(_EVALUATOR_REGISTRY))
        raise ValueError(f"Unknown evaluator '{name}'. Available: {available}")
    return _EVALUATOR_REGISTRY[name]()


def list_evaluators() -> list[str]:
    return sorted(_EVALUATOR_REGISTRY.keys())


def evaluate(state: GameState, player: Player,
             evaluators: list[Evaluator] | None = None) -> float:
    """Score a position: own score minus best opponent's score (weighted)."""
    if not evaluators:
        evaluators = [get_evaluator(n) for n in _EVALUATOR_REGISTRY]
    my_score = sum(e.score(state, player) for e in evaluators)
    best_opp = max(
        (sum(e.score(state, p) for e in evaluators)
         for p in state.players if p is not player),
        default=0.0,
    )
    return my_score - 0.3 * best_opp


# ── Built-in evaluators ──────────────────────────────────────────────

@_register_evaluator
class TagValue(Evaluator):
    """Score cards by their tag value."""
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


class _PileProximity_DISABLED(Evaluator):
    """DISABLED — superseded by EndgameAwareness."""
    name = "pile_proximity_disabled"

    def score(self, state, player):
        s = 0.0
        pile_health = {}
        for deck in ("claw", "tree", "wheat"):
            remaining = state.pile_remaining(deck)
            if deck == "tree":
                remaining += len(state.season)
            elif deck == "wheat":
                remaining += len(state.fields)
            pile_health[deck] = remaining

        win_tags = {"claw": "Trophy", "tree": "Nature", "wheat": "Amenity"}
        closest = min(pile_health, key=pile_health.get)

        for deck, tag in win_tags.items():
            my_count = player.count_tag(tag)
            max_opp = max(
                (p.count_tag(tag) for p in state.players if p is not player),
                default=0,
            )
            lead = my_count - max_opp
            urgency = max(1, 30 - pile_health[deck]) / 30.0

            # Extra weight for the closest pile
            if deck == closest:
                s += my_count * 2.0
            s += lead * 3.0 * (1.0 + urgency)
        return s


@_register_evaluator
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


@_register_evaluator
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

        # Reward Revelation existing (known, claimable card)
        if state.revelation:
            # Everyone benefits from Rite claiming, but Clergy owner benefits more
            if has_clergy:
                s += 3.0  # known card + peek bonus from ordering
            else:
                s += 1.0  # still claimable via Rite

        # Clergy + Religion snowball: the more Religion you have, the deeper you peek
        if has_clergy and religion_count >= 2:
            s += religion_count * 1.5  # peek depth scales with faithful count

        return s


@_register_evaluator
class EndgameAwareness(Evaluator):
    """Discourage ending the game on an axis where we're tied or behind."""
    name = "endgame_awareness"

    def score(self, state, player):
        s = 0.0
        win_tags = {"claw": "Trophy", "tree": "Nature", "wheat": "Amenity", "coin": "Wealth", "candle": "Religion", "sword": "Chivalry"}
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


@_register_evaluator
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


@_register_evaluator
class CardSynergy(Evaluator):
    """Score cards based on whether their synergies are active in the current state."""
    name = "card_synergy"

    def score(self, state, player):
        s = 0.0
        domain_names = set(c.name for c in player.domain)
        has_mobs = player.count_tag("Mob") > 0
        has_knowledge = player.count_tag("Knowledge") > 0
        has_nature = player.count_tag("Nature")
        has_discontent = player.count_tag("Discontent")
        discard_size = len(player.discard)
        claw_remaining = state.pile_remaining("claw")
        tree_remaining = state.pile_remaining("tree")
        coin_remaining = state.pile_remaining("coin")
        candle_remaining = state.pile_remaining("candle")
        has_coin_cards = any(c.deck == "coin" or c.has_tag("Craftsmanship") for c in player.domain)
        has_fields = len(state.fields) > 0
        has_season = len(state.season) > 0

        for card in player.domain:
            match card.name:
                # ── Claw cards ──
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
                    mob_count = player.count_tag("Mob")
                    s += mob_count * 0.5
                case "Racketeering":
                    others = state.other_players(player)
                    if any(len(p.domain) > 0 for p in others):
                        s += 1.0

                # ── Tree cards ──
                case "Remembrance":
                    if has_knowledge and discard_size > 0:
                        knowledge_count = player.count_tag("Knowledge")
                        recoverable = min(knowledge_count, discard_size)
                        s += recoverable * 1.5
                case "Herbalism":
                    cost_cards = player.count_tag("Knowledge") + has_nature
                    if cost_cards > 1 and discard_size > 0:
                        s += 1.5
                case "Forage":
                    s += 1.5
                case "Sacred Grove":
                    s += 1.0 + player.count_tag("Spiritual") * 0.3
                case "Well":
                    if has_season:
                        s += 2.0

                # ── Wheat cards ──
                case "Sowing":
                    if has_nature >= 2 and has_fields:
                        s += 2.0
                case "Withered Crop":
                    has_harvest_discard = any(c.name == "Harvest" for c in player.discard)
                    if has_harvest_discard and has_fields:
                        s += 2.0
                case "Animal Husbandry":
                    s += 1.5
                case "Militia":
                    if has_mobs:
                        s += 1.0
                case "Granary":
                    if has_discontent > 0:
                        s += 1.5
                    else:
                        s += 0.5

                # ── Discard-orderable cards ──
                case "Dusk Rite":
                    if discard_size > 0 and (claw_remaining > 0 or tree_remaining > 0):
                        s += discard_size * 0.3

                # ── Wheat cards (continued) ──
                case "Stewardship":
                    s += 2.0

                # ── Coin cards ──
                case "Swindle":
                    if len(state.wares) >= 3:
                        s += 3.0 + len(state.wares) * 0.5
                case "Benefaction":
                    if coin_remaining > 0:
                        s += 2.5

                # ── Candle cards ──
                case "Clergy":
                    has_religion = player.count_tag("Religion")
                    s += 3.0 + has_religion * 0.5
                case "Sabbath":
                    spiritual = player.count_tag("Spiritual")
                    s += 2.0 + spiritual * 0.5
                case "Evangelism":
                    has_religion = player.count_tag("Religion")
                    max_opp_religion = max(
                        (p.count_tag("Religion") for p in state.other_players(player)),
                        default=0)
                    if has_religion > max_opp_religion:
                        s += 3.0 + (has_religion - max_opp_religion) * 1.0
                    else:
                        s += 1.0
                case "Purity":
                    if candle_remaining > 0:
                        s += 2.0
                case "Zealot":
                    has_religion = player.count_tag("Religion")
                    if has_religion > 1:
                        s += 2.5
                    else:
                        s += 1.0
                case "Ornament":
                    if len(state.revelation) > 0:
                        s += 2.0
                case "Alms":
                    if has_discontent > 0 or has_fields:
                        s += 1.5
                case "Penance":
                    has_religion = player.count_tag("Religion")
                    if candle_remaining <= 10 and has_religion >= 3:
                        s += 1.0
                    else:
                        s -= 1.0
                case "Flagellation":
                    has_religion = player.count_tag("Religion")
                    if has_religion > 1:
                        s += 0.5
                    else:
                        s -= 1.0
                case "Worship of the Scripture":
                    if player.has_card("Clergy"):
                        s += 2.5
                    else:
                        s += 1.0
                case "Worship of the Relic":
                    if player.has_card("Clergy"):
                        s += 2.5
                    else:
                        s += 1.0
                case "Worship of the Martyr":
                    if player.has_card("Clergy"):
                        s += 2.0
                    else:
                        s += 0.5
                # ── Sword cards ──
                case "Royal Hunt":
                    opponent_hunts = any(
                        p.cards_with_tag("Hunt") for p in state.players if p is not player)
                    if not opponent_hunts and claw_remaining > 3:
                        s += 4.0
                    elif not opponent_hunts:
                        s += 2.0
                    else:
                        s += 0.5
                # ── Claw gateway cards ──
                case "Ivory":
                    if len(state.opportunities) > 0:
                        s += 2.5
                    else:
                        s += 1.0
                case "Martial Excellence":
                    other_trophies = sum(1 for c in player.domain
                                       if c.has_tag("Trophy") and c.name != "Martial Excellence")
                    if other_trophies > 0 and len(state.tourney) > 0:
                        s += 3.0
                    elif other_trophies > 0:
                        s += 1.5
                # ── Candle gateway ──
                case "Protect the Meek":
                    if len(state.tourney) > 0:
                        s += 2.0
                    else:
                        s += 0.5

        return s
