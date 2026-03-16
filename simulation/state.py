"""Game state model: Card, Player, GameState."""
from __future__ import annotations
import json
import random
import copy
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Card:
    name: str
    tags: list[str]
    deck: str  # "claw", "tree", "wheat", "coin", "candle"

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


@dataclass
class Player:
    name: str
    domain: list[Card] = field(default_factory=list)
    discard: list[Card] = field(default_factory=list)

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
        """Add card to domain, respecting slot limits (Culture, Allegiance, Religion)."""
        for slot_tag in ("Culture", "Allegiance", "Religion"):
            if card.has_tag(slot_tag):
                existing = [c for c in self.domain if c.has_tag(slot_tag)]
                for e in existing:
                    self.discard_from_domain(e)
                    if state:
                        state.log(f"  → {self.name} discards {e.name} (replaced by {card.name})")
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
        return False

    def has_coin_access(self) -> bool:
        if self.has_card("Animal Husbandry"):
            return True
        if self.has_card("Mill"):
            return True
        if self.has_card("Mine"):
            return True
        if self.has_card("Ingenuity"):
            return True
        # Apprenticeship needs a player with Craftsmanship to agree — handled at action level
        return False

    def has_candle_access(self) -> bool:
        return self.has_card("Oral Tradition")

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
        self.piles: dict[str, list[Card]] = {}
        self.pile_ptrs: dict[str, int] = {}
        self.season: list[Card] = []
        self.fields: list[Card] = []
        self.wares: list[Card] = []
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

    def load_decks(self, decks_path: str | Path):
        data = json.loads(Path(decks_path).read_text(encoding="utf-8"))
        for deck_name, card_list in data.items():
            cards: list[Card] = []
            for entry in card_list:
                for _ in range(entry["count"]):
                    cards.append(Card(name=entry["name"], tags=list(entry["tags"]), deck=deck_name))
            self.rng.shuffle(cards)
            self.piles[deck_name] = cards
            self.pile_ptrs[deck_name] = 0

    def pile_remaining(self, deck: str) -> int:
        if deck not in self.piles:
            return 0
        return len(self.piles[deck]) - self.pile_ptrs.get(deck, 0)

    def draw_from_pile(self, deck: str) -> Card | None:
        if self.pile_remaining(deck) <= 0:
            return None
        idx = self.pile_ptrs[deck]
        card = self.piles[deck][idx]
        self.pile_ptrs[deck] = idx + 1
        return card

    def peek_pile(self, deck: str, n: int = 1) -> list[Card]:
        result = []
        ptr = self.pile_ptrs.get(deck, 0)
        for i in range(n):
            idx = ptr + i
            if idx < len(self.piles.get(deck, [])):
                result.append(self.piles[deck][idx])
        return result

    def put_on_bottom(self, deck: str, card: Card):
        """Put a card on the bottom of a pile (used by Village Gossip)."""
        if deck in self.piles:
            self.piles[deck].append(card)

    def setup_zones(self):
        """Set up Season (4 from Tree), Fields (5 from Wheat), Wares (3 from Coin)."""
        for _ in range(4):
            c = self.draw_from_pile("tree")
            if c:
                self.season.append(c)
        for _ in range(5):
            c = self.draw_from_pile("wheat")
            if c:
                self.fields.append(c)
        for _ in range(3):
            c = self.draw_from_pile("coin")
            if c:
                self.wares.append(c)

    def refill_season(self):
        if len(self.season) == 0:
            for _ in range(4):
                c = self.draw_from_pile("tree")
                if c:
                    self.season.append(c)
            if self.season:
                names = ", ".join(c.name for c in self.season)
                self.log(f"  🔄 Season refilled: {names}")

    def refill_fields(self, target: int = 5):
        while len(self.fields) < target:
            c = self.draw_from_pile("wheat")
            if not c:
                break
            self.fields.append(c)

    def refill_wares(self, target: int = 3):
        while len(self.wares) < target:
            c = self.draw_from_pile("coin")
            if not c:
                break
            self.wares.append(c)

    def check_game_end(self) -> str | None:
        """Check if any zone is fully depleted. Returns pile name or None.
        Tree/Wheat/Coin: pile AND face-up zone must both be empty.
        Claw/Candle: just the pile (no face-up zone)."""
        if self.pile_remaining("tree") == 0 and len(self.season) == 0:
            return "tree"
        if self.pile_remaining("wheat") == 0 and len(self.fields) == 0:
            return "wheat"
        if self.pile_remaining("coin") == 0 and len(self.wares) == 0:
            return "coin"
        for deck in ("claw", "candle"):
            if deck in self.piles and self.pile_remaining(deck) == 0:
                return deck
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
