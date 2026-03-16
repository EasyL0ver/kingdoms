"""Strategy interface and RandomStrategy implementation."""
from __future__ import annotations
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from state import GameState, Player, Card, Action


class Intent(Enum):
    """What the decision means for the choosing player."""
    GAIN = "gain"                  # pick something to add to your domain
    SACRIFICE = "sacrifice"        # pick your own card to lose (cost you chose to pay)
    GIVE_AWAY = "give_away"        # forced to give a card to opponent
    PICK_TARGET = "pick_target"    # choose who to attack/affect
    PICK_OPTION = "pick_option"    # choose between ability modes
    ACCEPT_REJECT = "accept_reject"  # yes/no binary decision
    ORDER = "order"                # choose resolution sequence
    TURN_ACTION = "turn_action"    # main turn action selection


@dataclass
class DecisionContext:
    """Structured metadata for every strategy decision."""
    intent: Intent                     # what this decision means for the chooser
    source: str                        # card/zone that caused this decision
    opponent: Any = None               # Player on the other side (if applicable)
    consequence: str = ""              # what happens after (e.g. "triggers Brawl if refused")
    tags: list[str] = field(default_factory=list)  # extra flags ("forced", "event:Brawl", etc.)


class Strategy(ABC):
    """Abstract decision-maker for a player."""

    @abstractmethod
    def choose_action(self, state: GameState, player: Player, actions: list[Action],
                      ctx: DecisionContext) -> Action:
        """Pick one action from the list of valid actions for this turn."""

    @abstractmethod
    def choose_from(self, state: GameState, player: Player, options: list,
                    ctx: DecisionContext):
        """Pick one item from a list (card, player, string option, etc.)."""

    @abstractmethod
    def choose_n(self, state: GameState, player: Player, options: list,
                 min_n: int, max_n: int, ctx: DecisionContext) -> list:
        """Pick between min_n and max_n items from options."""

    @abstractmethod
    def choose_yes_no(self, state: GameState, player: Player,
                      ctx: DecisionContext) -> bool:
        """Yes/no decision."""

    @abstractmethod
    def choose_order(self, state: GameState, player: Player, items: list,
                     ctx: DecisionContext) -> list:
        """Choose the resolution order for a list of items (e.g. On Event cards)."""


class RandomStrategy(Strategy):
    """Makes uniformly random valid choices."""

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def choose_action(self, state: GameState, player: Player, actions: list[Action],
                      ctx: DecisionContext) -> Action:
        return self.rng.choice(actions)

    def choose_from(self, state: GameState, player: Player, options: list,
                    ctx: DecisionContext):
        return self.rng.choice(options)

    def choose_n(self, state: GameState, player: Player, options: list,
                 min_n: int, max_n: int, ctx: DecisionContext) -> list:
        n = self.rng.randint(min_n, min(max_n, len(options)))
        return self.rng.sample(options, n)

    def choose_yes_no(self, state: GameState, player: Player,
                      ctx: DecisionContext) -> bool:
        return self.rng.choice([True, False])

    def choose_order(self, state: GameState, player: Player, items: list,
                     ctx: DecisionContext) -> list:
        result = list(items)
        self.rng.shuffle(result)
        return result
