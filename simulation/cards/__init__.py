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

    # Event-specific fields (set when called from on_event)
    event: str = ""        # "Brawl", "Rite", "Feast", "Harvest", "Rumour"
    triggerer: Player | None = None  # who triggered the event
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

    def responds_to(self, event: str, targeted: bool = False) -> bool:
        """Check if this context matches the given event and optional self-targeting."""
        if self.event != event:
            return False
        if targeted and self.target is not self.player:
            return False
        return True

    def discard_self(self):
        """Send this card to its owner's discard pile."""
        self.player.discard.append(self.card)


class CardBehavior:
    """Base class for card-specific logic.

    Class attributes define the card's identity:
        name: str       — card name (must match decks.json)
        tags: list[str] — tags like ["Discontent", "Mob"]
        deck: str       — which deck ("claw", "tree", "wheat", "coin", "candle")

    Four hooks define behavior:
        can_activate        — game rules: is activation legal right now?
        on_activate         — what happens when activated
        on_location_change  — fires on any card movement (pile→domain, domain→discard, etc.)
        on_event            — fires when an event broadcasts
    """
    name: str = ""
    tags: list[str] = []
    deck: str = ""

    def can_activate(self, ctx: CardContext) -> bool:
        """Can this card be activated right now?
        Checks both domain and discard (use ctx.location to distinguish).
        Return False by default — only activatable cards override this."""
        return False

    def on_activate(self, ctx: CardContext):
        """Resolve this card's activation as the player's turn action."""
        pass

    def on_location_change(self, ctx: CardContext, from_loc: str, to_loc: str):
        """Called when a card moves between zones.
        Locations: 'pile', 'domain', 'discard', 'season', 'fields', 'wares', 'removed'

        The card can place/discard itself. If it does nothing, the engine
        places it in the owner's domain by default.
        """
        pass

    def on_event(self, ctx: CardContext) -> bool:
        """Called when an event fires.
        Event type is in ctx.event. Triggerer in ctx.triggerer. Target in ctx.target.
        Return True if this card responded."""
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


