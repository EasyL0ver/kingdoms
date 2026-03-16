"""Card heuristic metadata — strategy hints separate from game rules.

Each CardHeuristics mirrors the card behavior hooks, describing zone
interactions per trigger:

  on_activate:          effects when player activates this card
  on_event_<type>:      effects when a specific event fires
  on_move_from_pile:    effects when this card moves from a pile

Effect strings use verb + zone format:
  "draw claw"      — draws blind from claw pile
  "activate tree"  — triggers the tree zone activation flow
  "take season"    — takes card(s) from season face-up area
  "peek claw"      — peeks/scries top of claw pile
  "draw coin"      — draws blind from coin pile
"""
from __future__ import annotations


class CardHeuristics:
    """Strategy metadata for a single card."""
    name: str = ""
    on_activate: list[str] = []
    on_event_brawl: list[str] = []
    on_event_feast: list[str] = []
    on_event_rite: list[str] = []
    on_event_harvest: list[str] = []
    on_event_rumour: list[str] = []
    on_move_from_pile: list[str] = []


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
    on_activate = ["activate claw", "activate tree"]

# ---------------------------------------------------------------------------
# Claw deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Tyranny(CardHeuristics):
    name = "Tyranny"
    on_activate = ["draw claw"]

@_register_card_h
class _Marauders(CardHeuristics):
    name = "Marauders"
    on_event_feast = ["draw claw"]

@_register_card_h
class _ShareTheSpoils(CardHeuristics):
    name = "Share the Spoils"
    on_event_feast = ["draw claw"]

@_register_card_h
class _Outriders(CardHeuristics):
    name = "Outriders"
    on_activate = ["draw claw"]

@_register_card_h
class _Ransack(CardHeuristics):
    name = "Ransack"
    on_activate = ["draw claw", "take season"]

@_register_card_h
class _SpoilsOfWar(CardHeuristics):
    name = "Spoils of War"
    on_event_brawl = ["draw claw", "draw tree"]

@_register_card_h
class _DuskRite(CardHeuristics):
    name = "Dusk Rite"
    on_activate = ["draw claw", "draw tree"]

@_register_card_h
class _LandGrab(CardHeuristics):
    name = "Land Grab"
    on_activate = ["take season"]

@_register_card_h
class _RiteOfPassage(CardHeuristics):
    name = "Rite of Passage"
    on_event_brawl = ["draw tree"]

@_register_card_h
class _Ingenuity(CardHeuristics):
    name = "Ingenuity"
    on_move_from_pile = ["draw coin"]

# ---------------------------------------------------------------------------
# Tree deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Eldership(CardHeuristics):
    name = "Eldership"
    on_event_brawl = ["draw tree"]

@_register_card_h
class _OralTradition(CardHeuristics):
    name = "Oral Tradition"
    on_activate = ["draw candle"]

@_register_card_h
class _Crags(CardHeuristics):
    name = "Crags"
    on_activate = ["peek claw"]

@_register_card_h
class _Forage(CardHeuristics):
    name = "Forage"
    on_activate = ["draw tree"]

@_register_card_h
class _SacredGrove(CardHeuristics):
    name = "Sacred Grove"
    on_activate = ["peek tree"]

@_register_card_h
class _Solstice(CardHeuristics):
    name = "Solstice"
    on_event_harvest = ["draw tree"]

@_register_card_h
class _Sowing(CardHeuristics):
    name = "Sowing"
    on_activate = ["activate wheat"]

@_register_card_h
class _WitheredCrop(CardHeuristics):
    name = "Withered Crop"
    on_activate = ["activate wheat"]

@_register_card_h
class _WorshipOfTheRain(CardHeuristics):
    name = "Worship of the Rain"
    on_event_rite = ["draw tree"]

# ---------------------------------------------------------------------------
# Wheat deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Mill(CardHeuristics):
    name = "Mill"
    on_activate = ["draw coin"]

@_register_card_h
class _Plough(CardHeuristics):
    name = "Plough"
    on_event_harvest = ["activate wheat"]

@_register_card_h
class _AnimalHusbandry(CardHeuristics):
    name = "Animal Husbandry"
    on_activate = ["draw coin", "activate wheat"]

@_register_card_h
class _Apprenticeship(CardHeuristics):
    name = "Apprenticeship"
    on_activate = ["activate coin"]

@_register_card_h
class _Well(CardHeuristics):
    name = "Well"
    on_activate = ["activate tree", "activate tree"]

@_register_card_h
class _VillageGossip(CardHeuristics):
    name = "Village Gossip"
    on_event_rumour = ["peek claw", "peek tree", "peek wheat", "peek coin", "peek candle"]

# ---------------------------------------------------------------------------
# Coin / Candle
# ---------------------------------------------------------------------------

@_register_card_h
class _Mine(CardHeuristics):
    name = "Mine"
    on_activate = ["draw coin"]

@_register_card_h
class _WorshipOfTheFlame(CardHeuristics):
    name = "Worship of the Flame"
    on_activate = ["activate claw", "activate tree"]
