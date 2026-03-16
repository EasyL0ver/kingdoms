"""Card heuristic metadata — strategy hints separate from game rules.

Each CardHeuristics mirrors the card behavior hooks, describing effects
per trigger using typed Effect classes:

  on_activate:          effects when player activates this card
  on_event_<type>:      effects when a specific event fires
  on_move_from_pile:    effects when this card moves from a pile

Effect classes are purely descriptive — they say WHAT happens, not whether
it's good or bad.  Heuristics interpret sentiment based on game state.
"""
from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Effect classes — describe what a card does
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Draw:
    """Draws blind from a zone pile."""
    zone: str

@dataclass(frozen=True)
class Activate:
    """Triggers a zone's activation flow."""
    zone: str

@dataclass(frozen=True)
class Take:
    """Takes from a face-up area (season, fields, wares)."""
    area: str

@dataclass(frozen=True)
class Peek:
    """Peeks/scries the top of a zone pile."""
    zone: str

@dataclass(frozen=True)
class Give:
    """Gives a card to another player."""
    pass

@dataclass(frozen=True)
class Cancel:
    """Cancels the current event."""
    pass

@dataclass(frozen=True)
class Discard:
    """Discards a card (own or from a pile)."""
    pass

# Union type for convenience
Effect = Draw | Activate | Take | Peek | Give | Cancel | Discard


# ---------------------------------------------------------------------------
# CardHeuristics
# ---------------------------------------------------------------------------
class CardHeuristics:
    """Strategy metadata for a single card."""
    name: str = ""
    on_activate: list[Effect] = []
    on_event_brawl: list[Effect] = []
    on_event_feast: list[Effect] = []
    on_event_rite: list[Effect] = []
    on_event_harvest: list[Effect] = []
    on_event_rumour: list[Effect] = []
    on_move_from_pile: list[Effect] = []


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
_CARD_HEURISTICS_MAP: dict[str, CardHeuristics] = {}


def _register_card_h(cls):
    """Decorator: auto-register a CardHeuristics subclass by its ``name``."""
    instance = cls()
    _CARD_HEURISTICS_MAP[cls.name] = instance
    return cls


def get_card_heuristics(card_name: str) -> CardHeuristics | None:
    """Look up heuristic metadata for a card. Returns None if not defined."""
    return _CARD_HEURISTICS_MAP.get(card_name)


# ---------------------------------------------------------------------------
# Starter / shared
# ---------------------------------------------------------------------------

@_register_card_h
class _Domain(CardHeuristics):
    name = "Domain"
    on_activate = [Activate("claw"), Activate("tree")]

# ---------------------------------------------------------------------------
# Claw deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Tyranny(CardHeuristics):
    name = "Tyranny"
    on_activate = [Draw("claw")]

@_register_card_h
class _Marauders(CardHeuristics):
    name = "Marauders"
    on_event_feast = [Draw("claw"), Discard()]

@_register_card_h
class _ShareTheSpoils(CardHeuristics):
    name = "Share the Spoils"
    on_event_feast = [Draw("claw")]

@_register_card_h
class _Outriders(CardHeuristics):
    name = "Outriders"
    on_activate = [Draw("claw")]

@_register_card_h
class _Ransack(CardHeuristics):
    name = "Ransack"
    on_activate = [Draw("claw"), Take("season")]

@_register_card_h
class _SpoilsOfWar(CardHeuristics):
    name = "Spoils of War"
    on_event_brawl = [Draw("claw"), Draw("tree"), Give()]

@_register_card_h
class _DuskRite(CardHeuristics):
    name = "Dusk Rite"
    on_activate = [Draw("claw"), Draw("tree")]

@_register_card_h
class _LandGrab(CardHeuristics):
    name = "Land Grab"
    on_activate = [Take("season")]

@_register_card_h
class _RiteOfPassage(CardHeuristics):
    name = "Rite of Passage"
    on_event_brawl = [Draw("tree")]

@_register_card_h
class _Ingenuity(CardHeuristics):
    name = "Ingenuity"
    on_move_from_pile = [Draw("coin")]

@_register_card_h
class _Raid(CardHeuristics):
    name = "Raid"
    on_event_brawl = [Give()]

@_register_card_h
class _Scavenge(CardHeuristics):
    name = "Scavenge"
    on_event_brawl = [Give()]

# ---------------------------------------------------------------------------
# Tree deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Eldership(CardHeuristics):
    name = "Eldership"
    on_event_brawl = [Cancel(), Draw("tree")]

@_register_card_h
class _OralTradition(CardHeuristics):
    name = "Oral Tradition"
    on_activate = [Draw("candle")]

@_register_card_h
class _Crags(CardHeuristics):
    name = "Crags"
    on_activate = [Peek("claw")]

@_register_card_h
class _Forage(CardHeuristics):
    name = "Forage"
    on_activate = [Draw("tree")]

@_register_card_h
class _SacredGrove(CardHeuristics):
    name = "Sacred Grove"
    on_activate = [Peek("tree")]

@_register_card_h
class _Solstice(CardHeuristics):
    name = "Solstice"
    on_event_harvest = [Draw("tree")]

@_register_card_h
class _Sowing(CardHeuristics):
    name = "Sowing"
    on_activate = [Activate("wheat")]

@_register_card_h
class _WitheredCrop(CardHeuristics):
    name = "Withered Crop"
    on_activate = [Activate("wheat")]

@_register_card_h
class _WorshipOfTheRain(CardHeuristics):
    name = "Worship of the Rain"
    on_event_rite = [Draw("tree")]

# ---------------------------------------------------------------------------
# Wheat deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Mill(CardHeuristics):
    name = "Mill"
    on_activate = [Draw("coin")]

@_register_card_h
class _Plough(CardHeuristics):
    name = "Plough"
    on_event_harvest = [Activate("wheat")]

@_register_card_h
class _AnimalHusbandry(CardHeuristics):
    name = "Animal Husbandry"
    on_activate = [Draw("coin"), Activate("wheat")]

@_register_card_h
class _Apprenticeship(CardHeuristics):
    name = "Apprenticeship"
    on_activate = [Activate("coin")]

@_register_card_h
class _Well(CardHeuristics):
    name = "Well"
    on_activate = [Activate("tree"), Activate("tree")]

@_register_card_h
class _VillageGossip(CardHeuristics):
    name = "Village Gossip"
    on_event_rumour = [Peek("claw"), Peek("tree"), Peek("wheat"),
                       Peek("coin"), Peek("candle")]

@_register_card_h
class _Militia(CardHeuristics):
    name = "Militia"
    on_event_brawl = [Cancel(), Discard()]

@_register_card_h
class _Tavern(CardHeuristics):
    name = "Tavern"
    on_event_feast = [Discard()]

# ---------------------------------------------------------------------------
# Coin / Candle
# ---------------------------------------------------------------------------

@_register_card_h
class _Mine(CardHeuristics):
    name = "Mine"
    on_activate = [Draw("coin")]

@_register_card_h
class _WorshipOfTheFlame(CardHeuristics):
    name = "Worship of the Flame"
    on_activate = [Activate("claw"), Activate("tree")]
