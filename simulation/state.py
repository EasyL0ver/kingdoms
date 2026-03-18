"""Game state model: Card, Player, GameState."""
from __future__ import annotations
import json
import random
import copy
from dataclasses import dataclass, field
from pathlib import Path

_next_card_id = 0

def _new_card_id() -> int:
    global _next_card_id
    _next_card_id += 1
    return _next_card_id


@dataclass
class Card:
    name: str
    tags: list[str]
    deck: str  # "claw", "tree", "wheat", "coin", "candle", "zone"
    # Zone card properties — only used by zone cards
    face_up: list[Card] = field(default_factory=list)
    pile: list[Card] = field(default_factory=list)
    pile_ptr: int = 0
    id: int = field(default_factory=_new_card_id)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


@dataclass
class Player:
    name: str
    domain: list[Card] = field(default_factory=list)
    discard: list[Card] = field(default_factory=list)
    domain_card: Card = field(default_factory=lambda: Card(name="Presence", tags=[], deck="zone"))

    def domain_names(self) -> list[str]:
        return [c.name for c in self.domain]

    def discard_names(self) -> list[str]:
        return [c.name for c in self.discard]

    def has_card(self, name: str) -> bool:
        return any(c.name == name for c in self.domain)

    def has_discard(self, name: str) -> bool:
        return any(c.name == name for c in self.discard)

    def count_tag(self, tag: str) -> int:
        return sum(1 for c in self.domain if c.has_tag(tag))

    def get_card(self, name: str) -> Card | None:
        for c in self.domain:
            if c.name == name:
                return c
        return None

    def get_discard_card(self, name: str) -> Card | None:
        for c in self.discard:
            if c.name == name:
                return c
        return None

    def cards_with_tag(self, tag: str) -> list[Card]:
        return [c for c in self.domain if c.has_tag(tag)]

    def remove_from_domain(self, card: Card) -> bool:
        if card in self.domain:
            self.domain.remove(card)
            return True
        return False

    def discard_from_domain(self, card: Card) -> bool:
        if self.remove_from_domain(card):
            self.discard.append(card)
            return True
        return False

    def add_to_domain(self, card: Card, state: GameState | None = None):
        """Add card to domain."""
        self.domain.append(card)

    def has_wheat_access(self) -> bool:
        if self.has_card("Animal Husbandry"):
            return True
        if self.has_card("Sowing") and self.count_tag("Nature") >= 2:
            return True
        if self.has_card("Withered Crop") and self.has_discard("Harvest"):
            return True
        if self.has_card("Plough"):
            return True
        if self.has_card("Orchard"):
            return True
        return False

    def has_coin_access(self) -> bool:
        if self.has_card("Animal Husbandry"):
            return True
        if self.has_card("Mill"):
            return True
        if self.has_card("Mine"):
            return True
        if self.has_card("Market"):
            return True
        # Apprenticeship needs a player with Craftsmanship to agree — handled at action level
        return False

    def has_candle_access(self) -> bool:
        return self.has_card("Clergy")

    def shares_culture(self, other: Player) -> bool:
        """True if both players have a Culture card with the same name."""
        my_cultures = {c.name for c in self.domain if c.has_tag("Culture")}
        their_cultures = {c.name for c in other.domain if c.has_tag("Culture")}
        return bool(my_cultures & their_cultures)


@dataclass
class Action:
    type: str
    card: Card | None = None
    owner: Player | None = None  # for Well activation
    label: str = ""

    def __str__(self):
        return self.label or self.type


class GameState:
    def __init__(self, player_names: list[str], seed: int | None = None):
        self.rng = random.Random(seed)
        self.players = [Player(name=n) for n in player_names]
        self.zone_cards: dict[str, Card] = {
            "claw": Card(name="Claw Zone", tags=["Zone"], deck="zone"),
            "tree": Card(name="Tree Zone", tags=["Zone"], deck="zone"),
            "wheat": Card(name="Wheat Zone", tags=["Zone"], deck="zone"),
            "coin": Card(name="Coin Zone", tags=["Zone"], deck="zone"),
            "candle": Card(name="Candle Zone", tags=["Zone"], deck="zone"),
            "sword": Card(name="Sword Zone", tags=["Zone"], deck="zone"),
        }
        self.wares_pile: list[Card] = []  # Junk dump — separate from Opportunities
        self.hunt_uses_this_round = 0
        self.round_num = 0
        self.turn_num = 0
        self.game_over = False
        self.depleted_pile: str | None = None
        self._log: list[str] = []

    def log(self, msg: str):
        self._log.append(msg)

    def get_log(self) -> str:
        return "\n".join(self._log)

    # Zone face-up areas — owned by zone cards, aliased here for convenience
    @property
    def season(self) -> list[Card]:
        return self.zone_cards["tree"].face_up

    @property
    def fields(self) -> list[Card]:
        return self.zone_cards["wheat"].face_up

    @property
    def opportunities(self) -> list[Card]:
        """Premium coin cards face-up (refilled to 3)."""
        return self.zone_cards["coin"].face_up

    @property
    def wares(self) -> list[Card]:
        """Junk pile — cards dumped by trades, Smuggler, etc. Free to grab."""
        return self.wares_pile

    @property
    def revelation(self) -> list[Card]:
        """The face-up Revelation card(s) for candle zone. Usually 0 or 1."""
        return self.zone_cards["candle"].face_up

    @property
    def tourney(self) -> list[Card]:
        """The 2 face-up sword cards in the Tourney."""
        return self.zone_cards["sword"].face_up

    def load_decks(self, decks_path: str | Path):
        data = json.loads(Path(decks_path).read_text(encoding="utf-8"))
        for deck_name, card_list in data.items():
            cards: list[Card] = []
            for entry in card_list:
                for _ in range(entry["count"]):
                    cards.append(Card(name=entry["name"], tags=list(entry["tags"]), deck=deck_name))
            self.rng.shuffle(cards)
            zone = self.zone_cards[deck_name]
            zone.pile = cards
            zone.pile_ptr = 0

    def pile_remaining(self, deck: str) -> int:
        zone = self.zone_cards.get(deck)
        if not zone:
            return 0
        return len(zone.pile) - zone.pile_ptr

    def draw_from_pile(self, deck: str) -> Card | None:
        if self.pile_remaining(deck) <= 0:
            return None
        zone = self.zone_cards[deck]
        card = zone.pile[zone.pile_ptr]
        zone.pile_ptr += 1
        return card

    def return_to_pile(self, deck: str, card: Card):
        """Put a card back on top of a pile (before pile_ptr)."""
        zone = self.zone_cards[deck]
        if zone.pile_ptr > 0:
            zone.pile_ptr -= 1
            zone.pile.insert(zone.pile_ptr, card)
        else:
            zone.pile.insert(0, card)

    def peek_pile(self, deck: str, n: int = 1) -> list[Card]:
        zone = self.zone_cards.get(deck)
        if not zone:
            return []
        result = []
        for i in range(n):
            idx = zone.pile_ptr + i
            if idx < len(zone.pile):
                result.append(zone.pile[idx])
        return result

    def put_on_bottom(self, deck: str, card: Card):
        """Put a card on the bottom of a pile (used by Village Gossip)."""
        zone = self.zone_cards.get(deck)
        if zone:
            zone.pile.append(card)

    def setup_zones(self):
        """Set up face-up areas: Season (4), Fields (5), Opportunities (3), Revelation (1), Tourney (2). Wares start empty."""
        from cards import get_behavior
        get_behavior("Tree Zone").refill(self)
        get_behavior("Wheat Zone").refill(self)
        get_behavior("Coin Zone").refill(self, 3)
        get_behavior("Candle Zone").refill(self)
        get_behavior("Sword Zone").refill(self)

    def refill_season(self, target: int = 4):
        from cards import get_behavior
        get_behavior("Tree Zone").refill(self, target)

    def refill_fields(self, target: int = 5):
        from cards import get_behavior
        get_behavior("Wheat Zone").refill(self, target)

    def refill_opportunities(self, target: int = 3):
        from cards import get_behavior
        get_behavior("Coin Zone").refill(self, target)

    def check_game_end(self) -> str | None:
        """Check if any zone is fully depleted. Returns pile name or None.
        Tree/Wheat/Coin: pile AND face-up zone must both be empty.
        Claw: just the pile (no face-up zone).
        Candle: pile AND Revelation must both be empty."""
        if self.pile_remaining("tree") == 0 and len(self.season) == 0:
            return "tree"
        if self.pile_remaining("wheat") == 0 and len(self.fields) == 0:
            return "wheat"
        if self.pile_remaining("coin") == 0 and len(self.opportunities) == 0:
            return "coin"
        if self.pile_remaining("candle") == 0 and len(self.revelation) == 0:
            return "candle"
        if "claw" in self.zone_cards and self.pile_remaining("claw") == 0:
            return "claw"
        if "sword" in self.zone_cards and self.pile_remaining("sword") == 0 and len(self.tourney) == 0:
            return "sword"
        return None

    def player_by_name(self, name: str) -> Player | None:
        for p in self.players:
            if p.name == name:
                return p
        return None

    def other_players(self, player: Player) -> list[Player]:
        return [p for p in self.players if p is not player]

    def play_order_from(self, player: Player) -> list[Player]:
        """Players in clockwise order starting from the given player."""
        idx = self.players.index(player)
        n = len(self.players)
        return [self.players[(idx + i) % n] for i in range(n)]
