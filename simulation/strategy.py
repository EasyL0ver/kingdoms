"""Strategy interface and RandomStrategy implementation."""
from __future__ import annotations
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import GameState, Player


class Intent(Enum):
    """What the decision means for the choosing player."""
    GAIN = "gain"           # pick something to receive/add to domain
    DISCARD = "discard"     # voluntarily lose a card (cost you chose to pay)
    GIVE_AWAY = "give_away" # forced to give a card to opponent
    TARGET = "target"       # pick a player to affect
    OPTION = "option"       # pick between modes (includes yes/no as [True, False])


@dataclass
class DecisionContext:
    """Structured metadata for every strategy decision."""
    event: str              # current event: "Dawn", "Brawl", "Rite", "Feast", "Harvest", "Rumour"
    source: str             # card/zone name that caused this decision
    intent: Intent          # what kind of choice


class Strategy(ABC):
    """Abstract decision-maker for a player."""

    @abstractmethod
    def sequence(self, state: GameState, player: Player, items: list,
                 ctx: DecisionContext) -> list:
        """Choose resolution order for event responders or other ordered lists."""

    @abstractmethod
    def resolve(self, state: GameState, player: Player, options: list,
                ctx: DecisionContext):
        """Pick one item from options. For yes/no, options=[True, False]."""

    def resolve_n(self, state: GameState, player: Player, options: list,
                  min_n: int, max_n: int, ctx: DecisionContext) -> list:
        """Pick between min_n and max_n items. Default: pick one at a time from shrinking list."""
        n = min(max_n, len(options))
        if n <= min_n:
            return list(options[:n])
        picked = []
        remaining = list(options)
        for _ in range(n):
            if not remaining:
                break
            choice = self.resolve(state, player, remaining, ctx)
            picked.append(choice)
            remaining.remove(choice)
        return picked


class RandomStrategy(Strategy):
    """Makes uniformly random valid choices."""

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def sequence(self, state, player, items, ctx):
        result = list(items)
        self.rng.shuffle(result)
        return result

    def resolve(self, state, player, options, ctx):
        return self.rng.choice(options)

    def resolve_n(self, state, player, options, min_n, max_n, ctx):
        n = self.rng.randint(min_n, min(max_n, len(options)))
        return self.rng.sample(options, n)
