#!/usr/bin/env python3
"""Generate printable A4 card sheets from decks.json.

Cards are sized ~3mm smaller than Magic: The Gathering (60×85mm vs 63×88mm).
Output: cards.html — open in a browser and Print → Save as PDF.

Usage:  python print_cards.py
"""

import json
import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Card dimensions (mm)
# ---------------------------------------------------------------------------
CARD_W = 60   # MTG is 63
CARD_H = 85   # MTG is 88

COLS = 3
ROWS = 3
CARDS_PER_PAGE = COLS * ROWS

# ---------------------------------------------------------------------------
# Deck theming
# ---------------------------------------------------------------------------
DECK_COLORS = {
    "claw":   ("#8B1A1A", "#F5E0E0"),
    "tree":   ("#2E7D32", "#E8F5E9"),
    "wheat":  ("#8D6E00", "#FFF8E1"),
    "coin":   ("#7B5B00", "#FFF3D4"),
    "candle": ("#4A148C", "#F3E5F5"),
    "sword":  ("#37474F", "#ECEFF1"),
    "zone":   ("#37474F", "#F5F5F5"),
}

DECK_ICONS = {
    "claw": "🐾", "tree": "🌳", "wheat": "🌾",
    "coin": "🪙", "candle": "🕯️", "sword": "⚔️", "zone": "🏰",
}

# ---------------------------------------------------------------------------
# Card rules text — written from simulation code (source of truth)
# ---------------------------------------------------------------------------
CARD_TEXT = {
    # ── Zone cards ──────────────────────────────────────────────────────
    "Presence":
        "On Dawn — choose one:\n"
        "• Order on the Claw zone or Tree zone.\n"
        "• Order a card in your Domain.\n"
        "• Order a card from your discard.",

    "Claw Zone":
        "On Order — draw 2 cards from the Claw pile.",

    "Tree Zone":
        "4 cards face-up — the Season.\n"
        "On Order — take 1 card from the Season.\n"
        "Refill the Season to 4.",

    "Wheat Zone":
        "Face-up cards — the Fields.\n"
        "On Order — take 1–3 cards from the Fields.\n"
        "For each card taken, draw 1 from Claw.",

    "Coin Zone":
        "3 face-up cards — the Opportunities.\n"
        "Discarded cards go to the Wares.\n"
        "On Order — choose one:\n"
        "• Buy — take 1 card from the Wares.\n"
        "• Trade — give 1 Domain card to Wares,\n"
        "  take 1 Opportunity. Rumour.",

    "Candle Zone":
        "1 face-up card — the Revelation.\n"
        "On Order — claim the Revelation.\n"
        "Reveal the next card.",

    "Sword Zone":
        "2 face-up cards — the Tourney.\n"
        "On Order — Injustice (2+ [Mob] in any\n"
        "Domain): tyrant takes [Unit], you take rest.\n"
        "Peace (Joust): challenge an opponent.\n"
        "Accept = both pick 1. Refuse = Brawl in\n"
        "both Domains. Refill Tourney to 2.",

    # ── Claw deck ───────────────────────────────────────────────────────
    "Warband":
        "On Order — you may move 1 [Mob] to the\n"
        "Domain with the most cards. Brawl there.",

    "Raid":
        "On Brawl — give 1 card from your Domain\n"
        "to the active player.\n"
        "If Uprising, discard 1 instead.",

    "Scavenge":
        "On Brawl — the active player takes 1 card\n"
        "from your discard.",

    "Blood Offering":
        "On Order — discard 1 card from your Domain.\n"
        "Rite in your Domain.",

    "Poach":
        "On Order — Feast in your Domain. Draw 1\n"
        "from Claw.\n"
        "Hunt — blocked if another player has [Hunt].",

    "Worship of the Hunt":
        "On Rite — dump 5 Claw cards to the active\n"
        "player's discard.",

    "Worship of War":
        "On Rite — the active player Brawls in a\n"
        "Domain of their choice.",

    "Incite":
        "On Dawn — move up to 3 [Mob] cards from\n"
        "your Domain to other Domains.\n"
        "Discard Incite.",

    "Chiefdom":
        "On Dawn — move up to 2 [Mob] cards from\n"
        "your Domain or a culture ally's to any\n"
        "other Domain.",

    "Kinship":
        "On Harvest — Order on the Tree zone.",

    "Racketeering":
        "On Order — choose a player. They offer you\n"
        "1 card. Take it, or refuse and Brawl in\n"
        "their Domain.",

    "Tyranny":
        "On Order — draw from Claw equal to your\n"
        "[Discontent] count. Brawl in your Domain\n"
        "(spoils are discarded, not taken).",

    "Marauders":
        "On Feast — discard Marauders.\n"
        "Draw 1 from Claw.",

    "Share the Spoils":
        "On Feast — draw 1 from Claw.",

    "Martial Excellence":
        "On Order — Order on the Sword zone.\n"
        "Requires another [Trophy] in your Domain.",

    "Outriders":
        "On Order — draw 3 from Claw.\n"
        "Discard 1 of your choice.",

    "Land Grab":
        "On Order — take all [Land] cards from the\n"
        "Season to your Domain. Discard Land Grab.\n"
        "Requires [Land] in the Season.",

    "Rite of Passage":
        "On Brawl — draw 1 from Tree.",

    "Culling":
        "On Dawn — the player with the most cards\n"
        "discards 1–2 cards of their choice.\n"
        "Discard Culling.",

    "Ivory":
        "On Order — discard Ivory.\n"
        "Order on the Coin zone.",

    "Hunger":
        "On Harvest — dump 1 Claw card to your\n"
        "discard.\n"
        "On Feast — return 1 card from your discard\n"
        "to top of the Claw pile.",

    "Uprising":
        "On Dawn — Brawl in your Domain. No player\n"
        "benefits from the Brawl.\n"
        "Discard Uprising.",

    "Ransack":
        "On Order — discard 1 card from your Domain.\n"
        "Draw 2 from Claw. Take 1 from the Season.",

    "Spoils of War":
        "On Dawn — place Spoils of War in another\n"
        "player's Domain.\n"
        "On Brawl — moves to the active player. They\n"
        "draw from Claw and Tree equal to their\n"
        "[Trophy] count.",

    "Dusk Rite":
        "On Order — exile any number of cards from\n"
        "your discard. Rite in your Domain.\n"
        "Discard Dusk Rite.",

    "Blood Feud":
        "On Brawl — draw 2 from Claw. Move up to\n"
        "2 [Mob] to the active player. Discard\n"
        "Blood Feud, then Brawl the attacker back.",

    "Enforcers":
        "On Brawl — both you and the active player\n"
        "draw 2 from Claw.",

    # ── Tree deck ───────────────────────────────────────────────────────
    "Eldership":
        "On Brawl — if the active player shares your\n"
        "culture, you may cancel the Brawl.\n"
        "They draw 1 from Tree.",

    "Sky Dance":
        "On Order — Rite in your Domain.",

    "Harvest":
        "On Dawn — Harvest in every zone.\n"
        "Discard Harvest.",

    "Gathering":
        "On Dawn — choose Brawl or Rite. Fires in\n"
        "your Domain and all culture allies' Domains.\n"
        "Discard Gathering.",

    "Sacred Grove":
        "On Order — choose one:\n"
        "• Rite in your Domain.\n"
        "• Look at the top 3 Tree cards. Take any\n"
        "  [Spiritual] cards. Return the rest.",

    "Herbalism":
        "On Order — discard a [Knowledge] or [Nature]\n"
        "card. Take 1 card from your discard to\n"
        "your Domain.",

    "Worship of the Rain":
        "On Rite — swap 1 Season card with the top\n"
        "card of the Candle pile.",

    "Worship of Fertility":
        "On Rite — Harvest in the active player's\n"
        "Domain.",

    "Forage":
        "On Order — dump top 2 Tree and top 2 Claw\n"
        "cards to your discard.\n"
        "Feast in your Domain.",

    "Sowing":
        "On Order — Order on the Wheat zone.\n"
        "On Harvest — refill 1 Field.\n"
        "Requires 2+ [Nature] in your Domain.",

    "Withered Crop":
        "On Order — exile cards from your discard.\n"
        "Refill Fields by that count from the Wheat\n"
        "pile. Order on the Wheat zone.",

    "Remembrance":
        "On Order — return cards from your discard\n"
        "to your Domain equal to your [Knowledge]\n"
        "count.",

    "Pilgrimage":
        "On Order — claim the Revelation. Reveal\n"
        "the next card.\n"
        "On Rite — same effect.",

    # ── Wheat deck ──────────────────────────────────────────────────────
    "Plough":
        "On Order — Order on the Wheat zone. Return\n"
        "1 [Discontent] to the Claw pile.\n"
        "On Harvest — choose: Feast in your Domain,\n"
        "or Order on the Wheat zone.",

    "Granary":
        "On Order — Feast in your Domain.\n"
        "Discard Granary.",

    "Mill":
        "On Order — draw 1 from Coin.\n"
        "Discard Mill.",

    "Famine":
        "On Dawn — choose a player. They discard\n"
        "1 Wheat card from their Domain.\n"
        "Discard Famine.",

    "Animal Husbandry":
        "On Order — choose one:\n"
        "• Order on the Wheat zone.\n"
        "• Order on the Coin zone.\n"
        "• Feast in your Domain.",

    "Tavern":
        "On Feast — return 1 [Discontent] card from\n"
        "your Domain to the Claw pile.",

    "Feed the Commoners":
        "On Dawn — return up to 3 [Discontent] cards\n"
        "from your Domain to the Claw pile.\n"
        "Discard Feed the Commoners.",

    "Apprenticeship":
        "On Order — Order on the Coin zone.\n"
        "Requires an opponent with [Craftsmanship].",

    "Militia":
        "On Order — discard 1 [Mob] from your Domain.\n"
        "On Brawl — discard Militia to cancel\n"
        "the Brawl in your Domain.",

    "Well":
        "On Order (any player) — the orderer and the\n"
        "owner each Order on the Tree zone.\n"
        "Refill 1 Season card and 1 Field.",

    "Maypole":
        "No effect — pure [Amenity] tag.",

    "Village Gossip":
        "On Rumour — look at the top card of any\n"
        "pile. You may put it on the bottom.",

    "Orchard":
        "On Order — take 1 card from the Fields\n"
        "(no Claw tax).",

    "Stewardship":
        "On Dawn — choose one:\n"
        "• Order on the Wheat zone (if Fields exist).\n"
        "• Order on the Tree zone (if Season exists).",

    "Irrigation":
        "On Dawn — refill 1 Field from the Wheat\n"
        "pile.",

    "Worship of the Bread":
        "On Feast — refill 1 Field.\n"
        "On Rite — refill 1 Field.",

    # ── Coin deck ───────────────────────────────────────────────────────
    "Treasure":
        "No effect — pure tags.",

    "Market":
        "On Order — Order on the Coin zone.\n"
        "On Rumour — swap 1 Domain card with\n"
        "1 Wares card.",

    "Smuggler":
        "On Brawl — move 1 Domain card to Wares.\n"
        "On Rumour — move Smuggler to the active\n"
        "player's Domain.",

    "Sellsword":
        "On Brawl — discard Sellsword to the Wares\n"
        "to cancel the Brawl in your Domain.",

    "Swindle":
        "On Order — give all Wares to a chosen\n"
        "opponent. Brawl in their Domain.\n"
        "Discard Swindle.",

    "Prosperity":
        "On Dawn — draw 1 from Coin if Opportunities\n"
        "exist.",

    "Embassy":
        "On Dawn — if you have a culture ally and\n"
        "Wares exist: you and your ally each take\n"
        "1 card from the Wares.",

    "Efficiency":
        "On Order — Order up to 4 other cards in\n"
        "your Domain. Discard Efficiency.",

    "Spice Market":
        "On Order — draw Coin cards equal to your\n"
        "count of unique tags in your Domain.",

    "Commodities":
        "On Rumour — draw 1 card from a chosen pile.\n"
        "Add it to the Wares.",

    "Mine":
        "On Dawn — discard Mine if you have no Crags.\n"
        "On Order — draw 1 from Coin.",

    "Provisions":
        "On Feast — draw 1 from Coin.",

    "Worship of Gold":
        "On Rite — the active player takes 1 card\n"
        "from the Wares.",

    # ── Candle deck ─────────────────────────────────────────────────────
    "Worship of the Scripture":
        "On Rite — the active player peeks at Candle\n"
        "cards (scales with [Spiritual]). Keep 1,\n"
        "exile the rest.",

    "Worship of the Relic":
        "On Rite — peek at cards from a chosen pile\n"
        "(scales with [Spiritual]). May replace the\n"
        "Revelation. Return rest to top.",

    "Worship of the Martyr":
        "On Rite — the active player may discard\n"
        "cards. All other players must discard\n"
        "equal to [Spiritual] scaling.",

    "Clergy":
        "On Order — Order Candle zone. Peek at Candle\n"
        "cards (1 per player with [Religion]). Keep 1,\n"
        "may set 1 as Revelation, exile rest.",

    "Sabbath":
        "On Dawn — Rite in your Domain.",

    "Zealot":
        "On Brawl — cancel if you have [Religion];\n"
        "else discard 1 Domain card.\n"
        "On Rite — active player may move Zealot\n"
        "to another Domain.",

    "Alms":
        "On Feast — refill 1 Field. Return\n"
        "1 [Discontent] to the Claw pile.",

    "Evangelism":
        "On Order — each player in turn order claims\n"
        "1 Revelation. Refill between each.",

    "Purity":
        "On Order — optionally exile the Revelation\n"
        "and reveal the next. Rite in your Domain.",

    "Flagellation":
        "On Rite — Brawl in your Domain (no player\n"
        "benefits).",

    "Penance":
        "On Dawn — discard 2 cards from your Domain.\n"
        "You may sacrifice Penance for an extra\n"
        "effect.",

    "Benefaction":
        "On Order — draw 1 from Coin. Refill\n"
        "Opportunities to 3. Optionally trigger\n"
        "2 Rumours.",

    "Ornament":
        "On Order — move the Revelation to the Wares.\n"
        "Reveal the next card.",

    "Protect the Meek":
        "On Brawl — Order on the Sword zone.",

    # ── Sword deck ──────────────────────────────────────────────────────
    "Royal Hunt":
        "On Order — Feast twice. Draw 1 from Claw.\n"
        "Hunt — blocked if another player has [Hunt].",
}

# ---------------------------------------------------------------------------
# Zone card definitions (not in decks.json)
# ---------------------------------------------------------------------------
ZONE_CARDS = [
    {"name": "Presence",   "tags": [],       "deck": "zone",   "count": 3},
    {"name": "Claw Zone",  "tags": ["Zone"], "deck": "claw",   "count": 1},
    {"name": "Tree Zone",  "tags": ["Zone"], "deck": "tree",   "count": 1},
    {"name": "Wheat Zone", "tags": ["Zone"], "deck": "wheat",  "count": 1},
    {"name": "Coin Zone",  "tags": ["Zone"], "deck": "coin",   "count": 1},
    {"name": "Candle Zone","tags": ["Zone"], "deck": "candle", "count": 1},
    {"name": "Sword Zone", "tags": ["Zone"], "deck": "sword",  "count": 1},
]

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
CSS = r"""
@page {
  size: A4 portrait;
  margin: 0;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #eee;
}

.page {
  width: 210mm;
  height: 297mm;
  background: white;
  display: grid;
  grid-template-columns: repeat(3, 60mm);
  grid-template-rows: repeat(3, 85mm);
  justify-content: center;
  align-content: center;
  page-break-after: always;
  break-after: page;
}

@media print {
  body { background: white; }
  .page { box-shadow: none; }
}

@media screen {
  .page {
    margin: 10mm auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }
}

/* ── Card (laser-printer friendly: outlines only) ─────────── */

.card {
  width: 60mm;
  height: 85mm;
  border: 0.4mm solid #000;
  border-radius: 2.5mm;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  background: white;
}

.card-header {
  padding: 2.5mm 3mm 2mm;
  color: #000;
  font-weight: 800;
  font-size: 12pt;
  text-transform: uppercase;
  letter-spacing: 0.3pt;
  display: flex;
  align-items: center;
  gap: 1.5mm;
  min-height: 9mm;
  border-bottom: 0.5mm solid #000;
}

.card-header .icon {
  font-size: 12pt;
  flex-shrink: 0;
}

.card-tags {
  padding: 1.5mm 3mm 1.5mm;
  font-size: 8pt;
  font-weight: 700;
  letter-spacing: 0.3pt;
  border-bottom: 0.3mm solid #999;
  min-height: 5mm;
  display: flex;
  align-items: center;
  gap: 1.5mm;
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  padding: 0.3mm 1.5mm;
  border: 0.3mm solid #000;
  border-radius: 1mm;
  font-size: 7.5pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2pt;
  color: #000;
}

.card-body {
  padding: 2.5mm 3mm 2mm;
  flex: 1;
  font-size: 11pt;
  line-height: 1.25;
  color: #000;
  white-space: pre-wrap;
}

.card-body b {
  font-weight: 800;
}

.card-body.empty {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  font-style: italic;
  font-size: 11pt;
}

.card-footer {
  padding: 0.5mm 3mm 1.5mm;
  font-size: 7pt;
  text-align: right;
  text-transform: uppercase;
  letter-spacing: 0.3pt;
  font-weight: 700;
  color: #000;
  border-top: 0.3mm solid #999;
}
"""


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def render_card(card: dict) -> str:
    deck = card["deck"]
    name = card["name"]
    tags = card.get("tags", [])
    text = CARD_TEXT.get(name, "")
    icon = DECK_ICONS.get(deck, "")

    tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
    if not tags_html:
        tags_html = '<span style="visibility:hidden;font-size:5pt">&nbsp;</span>'

    if text:
        body_html = f'<div class="card-body">{bold_keywords(text)}</div>'
    else:
        body_html = '<div class="card-body empty">— no effect —</div>'

    deck_label = name if "Zone" in name else deck.title()

    return (
        f'<div class="card deck-{deck}">'
        f'  <div class="card-header"><span class="icon">{icon}</span> {esc(name)}</div>'
        f'  <div class="card-tags">{tags_html}</div>'
        f'  {body_html}'
        f'  <div class="card-footer">{icon} {esc(deck_label)}</div>'
        f'</div>'
    )


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


import re

_BOLD_KEYWORDS = re.compile(
    r'\b('
    r'On Order|On Dawn|On Brawl|On Rite|On Feast|On Harvest|On Rumour'
    r'|Brawl|Rite|Feast|Harvest|Rumour|Order'
    r'|Hunt|Discard|Domain|Season|Fields|Wares|Opportunities|Revelation|Tourney'
    r'|Requires'
    r')\b'
)

def bold_keywords(text: str) -> str:
    """Wrap game keywords in <b> tags after HTML-escaping."""
    safe = esc(text)
    return _BOLD_KEYWORDS.sub(r'<b>\1</b>', safe)


def render_page(cards: list[dict]) -> str:
    inner = "\n".join(render_card(c) for c in cards)
    return f'<div class="page">\n{inner}\n</div>'


def generate_html(cards: list[dict]) -> str:
    pages = []
    for i in range(0, len(cards), CARDS_PER_PAGE):
        page_cards = cards[i : i + CARDS_PER_PAGE]
        pages.append(render_page(page_cards))

    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        "  <title>Kingdoms — Printable Cards</title>\n"
        f"  <style>{CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        + "\n".join(pages)
        + "\n</body>\n</html>\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    decks_path = Path(__file__).parent / "simulation" / "decks.json"
    decks = json.loads(decks_path.read_text(encoding="utf-8"))

    cards: list[dict] = []

    # 1. Zone cards first (fills exactly 1 page: 3 Presence + 6 zones = 9)
    for zc in ZONE_CARDS:
        for _ in range(zc["count"]):
            cards.append({
                "name": zc["name"],
                "tags": zc["tags"],
                "deck": zc["deck"],
            })

    # 2. Deck cards in order
    for deck_name in ("claw", "tree", "wheat", "coin", "candle", "sword"):
        if deck_name not in decks:
            continue
        for card_def in decks[deck_name]:
            for _ in range(card_def["count"]):
                cards.append({
                    "name": card_def["name"],
                    "tags": card_def["tags"],
                    "deck": deck_name,
                })

    # 3. Report any cards without text
    missing = set()
    for c in cards:
        if c["name"] not in CARD_TEXT:
            missing.add(c["name"])
    if missing:
        print(f"⚠  No text for: {', '.join(sorted(missing))}")

    # 4. Generate HTML
    html = generate_html(cards)
    out = Path(__file__).parent / "cards.html"
    out.write_text(html, encoding="utf-8")

    total_pages = math.ceil(len(cards) / CARDS_PER_PAGE)
    print(f"✅  Generated {out.name}: {len(cards)} cards on {total_pages} pages")
    print(f"    Open in browser → Print → Save as PDF (A4, no margins)")


if __name__ == "__main__":
    main()
