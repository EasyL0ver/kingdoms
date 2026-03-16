"""Card heuristic metadata — strategy hints separate from game rules.

Each CardHeuristics defines strategy-relevant properties for a card:
which piles it helps deplete, which zones it gates, etc.

These are NOT game rules — they're advisory data for heuristic strategies.
"""
from __future__ import annotations


class CardHeuristics:
    """Strategy metadata for a single card."""
    name: str = ""
    draws: list[str] = []    # piles this card depletes: ["claw"], ["tree", "claw"], etc.
    gates: list[str] = []    # zones this card unlocks: ["wheat"], ["coin"]


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
# Claw deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Tyranny(CardHeuristics):
    name = "Tyranny"
    draws = ["claw"]

@_register_card_h
class _Marauders(CardHeuristics):
    name = "Marauders"
    draws = ["claw"]

@_register_card_h
class _ShareTheSpoils(CardHeuristics):
    name = "Share the Spoils"
    draws = ["claw"]

@_register_card_h
class _Outriders(CardHeuristics):
    name = "Outriders"
    draws = ["claw"]

@_register_card_h
class _Ransack(CardHeuristics):
    name = "Ransack"
    draws = ["claw", "tree"]  # draws claw + takes from season

@_register_card_h
class _SpoilsOfWar(CardHeuristics):
    name = "Spoils of War"
    draws = ["claw", "tree"]  # draws from both based on trophy count

@_register_card_h
class _DuskRite(CardHeuristics):
    name = "Dusk Rite"
    draws = ["claw", "tree"]  # draws from both after removing discard

@_register_card_h
class _LandGrab(CardHeuristics):
    name = "Land Grab"
    draws = ["tree"]  # takes Land cards from season

@_register_card_h
class _RiteOfPassage(CardHeuristics):
    name = "Rite of Passage"
    draws = ["tree"]

@_register_card_h
class _Ingenuity(CardHeuristics):
    name = "Ingenuity"
    draws = ["coin"]

# ---------------------------------------------------------------------------
# Tree deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Eldership(CardHeuristics):
    name = "Eldership"
    draws = ["tree"]

@_register_card_h
class _OralTradition(CardHeuristics):
    name = "Oral Tradition"
    draws = ["candle"]

@_register_card_h
class _WorshipOfTheRain(CardHeuristics):
    name = "Worship of the Rain"
    draws = ["tree"]

@_register_card_h
class _Forage(CardHeuristics):
    name = "Forage"
    draws = ["tree"]  # draws 3

@_register_card_h
class _SacredGrove(CardHeuristics):
    name = "Sacred Grove"
    draws = ["tree"]  # scries/skips through pile

@_register_card_h
class _Solstice(CardHeuristics):
    name = "Solstice"
    draws = ["tree"]

@_register_card_h
class _Sowing(CardHeuristics):
    name = "Sowing"
    gates = ["wheat"]

@_register_card_h
class _WitheredCrop(CardHeuristics):
    name = "Withered Crop"
    gates = ["wheat"]

# ---------------------------------------------------------------------------
# Wheat deck
# ---------------------------------------------------------------------------

@_register_card_h
class _Mill(CardHeuristics):
    name = "Mill"
    draws = ["coin"]

@_register_card_h
class _Plough(CardHeuristics):
    name = "Plough"
    gates = ["wheat"]

@_register_card_h
class _AnimalHusbandry(CardHeuristics):
    name = "Animal Husbandry"
    draws = ["coin"]
    gates = ["wheat"]

# ---------------------------------------------------------------------------
# Coin / Candle
# ---------------------------------------------------------------------------

@_register_card_h
class _Mine(CardHeuristics):
    name = "Mine"
    draws = ["coin"]
