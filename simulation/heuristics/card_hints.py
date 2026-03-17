"""Card heuristic metadata — strategy hints separate from game rules.

Each CardHeuristics mirrors the card behavior hooks, describing effects
per trigger using typed Effect classes:

  on_order:             effects when player orders this card
  on_event_<type>:      effects when a specific event fires
  on_dawn:              effects when this card moves from a pile

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
    scales_with: str = ""  # tag whose count amplifies this effect

@dataclass(frozen=True)
class Order:
    """Triggers a zone's order flow."""
    zone: str
    scales_with: str = ""

@dataclass(frozen=True)
class Take:
    """Takes from a face-up area (season, fields, wares)."""
    area: str
    scales_with: str = ""

@dataclass(frozen=True)
class Peek:
    """Peeks/scries the top of a zone pile."""
    zone: str
    scales_with: str = ""

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

@dataclass(frozen=True)
class Trigger:
    """Triggers an event in a specific scope.

    Scopes: "target" (opponent you pick), "self" (your domain),
    "cultural" (cultural allies' domains), "all" (everyone).
    """
    event: str
    scope: str
    scales_with: str = ""

# Union type for convenience
Effect = Draw | Order | Take | Peek | Give | Cancel | Discard | Trigger


# ---------------------------------------------------------------------------
# CardHeuristics
# ---------------------------------------------------------------------------
class CardHeuristics:
    """Strategy metadata for a single card."""
    name: str = ""
    on_order: list[Effect] = []
    on_event_brawl: list[Effect] = []
    on_event_feast: list[Effect] = []
    on_event_rite: list[Effect] = []
    on_event_harvest: list[Effect] = []
    on_event_rumour: list[Effect] = []
    on_dawn: list[Effect] = []


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
    on_order = [Order("claw"), Order("tree")]

# ---------------------------------------------------------------------------
# Claw deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Tyranny(CardHeuristics):
    name = "Tyranny"
    on_order = [Draw("claw", scales_with="Discontent"), Trigger("brawl", "self")]

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
    on_order = [Draw("claw")]

@_register_card_h
class _Ransack(CardHeuristics):
    name = "Ransack"
    on_order = [Draw("claw"), Take("season")]

@_register_card_h
class _SpoilsOfWar(CardHeuristics):
    name = "Spoils of War"
    on_event_brawl = [Draw("claw", scales_with="Trophy"),
                      Draw("tree", scales_with="Trophy"), Give()]

@_register_card_h
class _DuskRite(CardHeuristics):
    name = "Dusk Rite"
    on_order = [Draw("claw"), Draw("tree"), Trigger("rite", "all")]

@_register_card_h
class _LandGrab(CardHeuristics):
    name = "Land Grab"
    on_order = [Take("season")]

@_register_card_h
class _RiteOfPassage(CardHeuristics):
    name = "Rite of Passage"
    on_event_brawl = [Draw("tree")]

@_register_card_h
class _Ingenuity(CardHeuristics):
    name = "Ingenuity"
    on_dawn = [Draw("coin")]

@_register_card_h
class _Raid(CardHeuristics):
    name = "Raid"
    on_event_brawl = [Give()]

@_register_card_h
class _Scavenge(CardHeuristics):
    name = "Scavenge"
    on_event_brawl = [Give()]

@_register_card_h
class _Warband(CardHeuristics):
    name = "Warband"
    on_order = [Trigger("brawl", "target")]

@_register_card_h
class _BloodOffering(CardHeuristics):
    name = "Blood Offering"
    on_order = [Discard(), Trigger("rite", "all")]

@_register_card_h
class _Poach(CardHeuristics):
    name = "Poach"
    on_order = [Trigger("feast", "self", scales_with="Pasture")]

@_register_card_h
class _WorshipOfWar(CardHeuristics):
    name = "Worship of War"
    on_event_rite = [Trigger("brawl", "target")]

@_register_card_h
class _WorshipOfTheHunt(CardHeuristics):
    name = "Worship of the Hunt"
    on_event_rite = [Trigger("feast", "self")]

@_register_card_h
class _Chiefdom(CardHeuristics):
    name = "Chiefdom"
    on_order = [Give()]

@_register_card_h
class _Racketeering(CardHeuristics):
    name = "Racketeering"
    on_order = [Trigger("brawl", "target")]

@_register_card_h
class _Incite(CardHeuristics):
    name = "Incite"
    on_dawn = [Give()]

@_register_card_h
class _Culling(CardHeuristics):
    name = "Culling"
    on_dawn = [Discard()]

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
    on_order = [Draw("candle")]

@_register_card_h
class _Crags(CardHeuristics):
    name = "Crags"
    on_order = [Peek("claw")]

@_register_card_h
class _Forage(CardHeuristics):
    name = "Forage"
    on_order = [Draw("tree")]

@_register_card_h
class _SacredGrove(CardHeuristics):
    name = "Sacred Grove"
    on_order = [Peek("tree"), Trigger("rite", "all")]

@_register_card_h
class _SkyDance(CardHeuristics):
    name = "Sky Dance"
    on_order = [Trigger("rite", "all")]

@_register_card_h
class _Gathering(CardHeuristics):
    name = "Gathering"
    on_dawn = [Trigger("brawl", "self"), Trigger("brawl", "cultural"),
                         Trigger("rite", "all")]

@_register_card_h
class _Harvest(CardHeuristics):
    name = "Harvest"
    on_dawn = [Trigger("harvest", "all")]

@_register_card_h
class _WorshipOfFertility(CardHeuristics):
    name = "Worship of Fertility"
    on_event_rite = [Trigger("harvest", "all")]

@_register_card_h
class _Solstice(CardHeuristics):
    name = "Solstice"
    on_event_harvest = [Draw("tree")]

@_register_card_h
class _Sowing(CardHeuristics):
    name = "Sowing"
    on_order = [Order("wheat", scales_with="Nature")]

@_register_card_h
class _WitheredCrop(CardHeuristics):
    name = "Withered Crop"
    on_order = [Order("wheat")]

@_register_card_h
class _WorshipOfTheRain(CardHeuristics):
    name = "Worship of the Rain"
    on_event_rite = [Draw("tree")]

@_register_card_h
class _Remembrance(CardHeuristics):
    name = "Remembrance"
    on_order = [Take("discard", scales_with="Knowledge")]

# ---------------------------------------------------------------------------
# Wheat deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Mill(CardHeuristics):
    name = "Mill"
    on_order = [Draw("coin")]

@_register_card_h
class _Plough(CardHeuristics):
    name = "Plough"
    on_event_harvest = [Order("wheat"), Trigger("feast", "self")]

@_register_card_h
class _AnimalHusbandry(CardHeuristics):
    name = "Animal Husbandry"
    on_order = [Draw("coin"), Order("wheat"), Trigger("feast", "self")]

@_register_card_h
class _Granary(CardHeuristics):
    name = "Granary"
    on_order = [Discard(), Trigger("feast", "self")]

@_register_card_h
class _Apprenticeship(CardHeuristics):
    name = "Apprenticeship"
    on_order = [Order("coin")]

@_register_card_h
class _Well(CardHeuristics):
    name = "Well"
    on_order = [Order("tree"), Order("tree")]

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
    on_order = [Draw("coin")]

@_register_card_h
class _Rumour(CardHeuristics):
    name = "Rumour"
    on_dawn = [Trigger("rumour", "all")]

@_register_card_h
class _WorshipOfTheFlame(CardHeuristics):
    name = "Worship of the Flame"
    on_order = [Order("claw"), Order("tree")]
