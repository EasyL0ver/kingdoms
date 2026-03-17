"""Base card behavior and CardContext — the only interface cards need."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from state import GameState, Player, Card
    from engine import GameEngine


@dataclass
class CardContext:
    """Everything a card needs to make decisions and affect the game."""
    engine: GameEngine
    player: Player         # the card's owner (domain or discard)
    card: Card             # the card instance
    state: GameState       # full game state

    # Event-specific fields (set when dispatching per-event handlers)
    event: str = ""        # "Brawl", "Rite", "Feast", "Harvest", "Rumour"
    active_player: Player | None = None  # the active player (whose turn it is)
    target: Player | None = None     # target domain (for Brawl)
    uprising: bool = False           # Uprising special rules (no benefits)

    @property
    def location(self) -> str:
        """Where is this card? 'domain', 'discard', or 'unknown'."""
        if self.card in self.player.domain:
            return "domain"
        if self.card in self.player.discard:
            return "discard"
        return "unknown"

    def discard_self(self):
        """Send this card to its owner's discard pile."""
        self.player.discard.append(self.card)


class CardBehavior:
    """Base class for card-specific logic.

    Class attributes define the card's identity:
        name: str       — card name (must match decks.json)
        tags: list[str] — tags like ["Discontent", "Mob"]
        deck: str       — which deck ("claw", "tree", "wheat", "coin", "candle")

    Hooks define behavior:
        on_order        — what happens when Ordered (the player's turn action)
        on_dawn         — fires at the start of the owner's turn (Dawn phase)
        on_<event>      — per-event handlers (on_brawl, on_rite, etc.)
    """
    name: str = ""
    tags: list[str] = []
    deck: str = ""

    def on_order(self, ctx: CardContext):
        """Resolve this card's Order. Guard preconditions inside (early return)."""
        pass

    def on_dawn(self, ctx: CardContext):
        """Called at the start of the owner's turn (Dawn phase).
        Used for: one-shot effects (formerly Drafted), prerequisite checks,
        and delayed punishments."""
        pass

    def on_brawl(self, ctx: CardContext) -> bool:
        """Called when a Brawl event fires. Return True if this card responded."""
        return False

    def on_rite(self, ctx: CardContext) -> bool:
        """Called when a Rite event fires. Return True if this card responded."""
        return False

    def on_feast(self, ctx: CardContext) -> bool:
        """Called when a Feast event fires. Return True if this card responded."""
        return False

    def on_harvest(self, ctx: CardContext) -> bool:
        """Called when a Harvest event fires. Return True if this card responded."""
        return False

    def on_rumour(self, ctx: CardContext) -> bool:
        """Called when a Rumour event fires. Return True if this card responded."""
        return False


# Auto-discovery: all subclasses register themselves
_BEHAVIOR_MAP: dict[str, CardBehavior] = {}


def _register(cls: type[CardBehavior]):
    """Register a CardBehavior subclass by its name."""
    if cls.name:
        _BEHAVIOR_MAP[cls.name] = cls()
    return cls


def get_behavior(card_name: str) -> CardBehavior:
    """Get the behavior singleton for a card by name."""
    return _BEHAVIOR_MAP.get(card_name, _DEFAULT)


# Default behavior — no hooks
_DEFAULT = CardBehavior()


