#!/usr/bin/env python3
"""Generate printable A4 card sheets and a Markdown card catalogue from decks.json.

Cards are sized ~3mm smaller than Magic: The Gathering (60×85mm vs 63×88mm).
Output:
  cards.html      — open in a browser and Print → Save as PDF.
  game-cards.md   — full card catalogue in Markdown.

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
# Zone card definitions (not in decks.json — text kept here)
# ---------------------------------------------------------------------------
ZONE_CARDS = [
    {"name": "Presence",   "tags": [],       "deck": "zone",   "count": 3,
     "setupText": "Start with this card.\n"
                  "It cannot be discarded or moved.",
     "orderText": "On Dawn — choose one:\n"
                  "• Order on the Claw zone or Tree zone.\n"
                  "• Order a card in your Domain.",
     "endgameText": ""},
    {"name": "Claw Zone",  "tags": ["Zone"], "deck": "claw",   "count": 1,
     "setupText": "",
     "orderText": "On Order — draw 2 cards from the Claw pile.",
     "endgameText": "Player with most [Trophy] wins."},
    {"name": "Tree Zone",  "tags": ["Zone"], "deck": "tree",   "count": 1,
     "setupText": "4 cards face-up — the Season.",
     "orderText": "On Order — take 1 card from the Season.\n"
                  "Refill the Season to 4.",
     "endgameText": "Player with most [Nature] wins."},
    {"name": "Wheat Zone", "tags": ["Zone"], "deck": "wheat",  "count": 1,
     "setupText": "5 face-up cards — the Village (conveyor).",
     "orderText": "On Order — take 1–5 from the bottom.\n"
                  "Reveal Claw cards equal to [Labour] tags\n"
                  "taken → to your Domain.\n"
                  "If [Discontent] in your Domain ≥ 3:\n"
                  "Revolt — Brawl in every Domain with Wheat.\n"
                  "Refills to 5 after drawing.",
     "endgameText": "Player with most [Amenity] wins."},
    {"name": "Coin Zone",  "tags": ["Zone"], "deck": "coin",   "count": 1,
     "setupText": "3 face-up cards — the Opportunities.\n"
                  "Discarded cards go to the Wares.",
     "orderText": "On Order — choose one:\n"
                  "• Buy — take 1 card from the Wares.\n"
                  "• Trade — give 1 Domain card to Wares,\n"
                  "  take 1 Opportunity. Rumour in every Domain.",
     "endgameText": "Player with most [Wealth] wins."},
    {"name": "Candle Zone","tags": ["Zone"], "deck": "candle", "count": 1,
     "setupText": "1 face-up card — the Revelation.",
     "orderText": "On Order — claim the Revelation.\n"
                  "Reveal the next card.",
     "endgameText": "Player with most [Religion] wins."},
    {"name": "Sword Zone", "tags": ["Zone"], "deck": "sword",  "count": 1,
     "setupText": "2 face-up cards — the Tourney.",
     "orderText": "On Order — Injustice (2+ [Mob] in any\n"
                  "Domain): tyrant takes [Unit], you take rest.\n"
                  "Peace (Joust): challenge an opponent.\n"
                  "Accept = both pick 1. Refuse = Brawl in\n"
                  "both Domains. Refill Tourney to 2.",
     "endgameText": "Player with most [Chivalry] wins."},
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
  white-space: nowrap;
}

.card-header .icon {
  font-size: 12pt;
  flex-shrink: 0;
}

.card-tags {
  padding: 1.5mm 3mm;
  font-size: 8pt;
  font-weight: 700;
  letter-spacing: 0.3pt;
  border-bottom: 0.3mm solid #999;
  min-height: 5mm;
  display: flex;
  align-items: center;
  gap: 1.5mm;
  flex-wrap: nowrap;
  overflow: hidden;
  box-sizing: content-box;
}

.tag {
  display: inline-block;
  padding: 0.3mm 1.5mm;
  border-radius: 1mm;
  font-size: 7.5pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2pt;
  color: #fff;
}

.tag-discontent  { background: #8B1A1A; }
.tag-mob         { background: #A93226; }
.tag-unit        { background: #4A4A4A; }
.tag-hunt        { background: #5D4037; }
.tag-trophy      { background: #B8860B; }
.tag-nature      { background: #2E7D32; }
.tag-spiritual   { background: #4A148C; }
.tag-religion    { background: #7B1FA2; }
.tag-knowledge   { background: #1565C0; }
.tag-labour      { background: #8D6E63; }
.tag-amenity     { background: #00838F; }
.tag-wealth      { background: #E65100; }
.tag-chivalry    { background: #37474F; }

.inline-tag {
  font-weight: 800;
}

.inline-tag-discontent  { color: #8B1A1A; }
.inline-tag-mob         { color: #A93226; }
.inline-tag-unit        { color: #4A4A4A; }
.inline-tag-hunt        { color: #5D4037; }
.inline-tag-trophy      { color: #B8860B; }
.inline-tag-nature      { color: #2E7D32; }
.inline-tag-spiritual   { color: #4A148C; }
.inline-tag-religion    { color: #7B1FA2; }
.inline-tag-knowledge   { color: #1565C0; }
.inline-tag-labour      { color: #8D6E63; }
.inline-tag-amenity     { color: #00838F; }
.inline-tag-wealth      { color: #E65100; }
.inline-tag-chivalry    { color: #37474F; }

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

.card-endgame {
  padding: 1.5mm 3mm;
  font-size: 8.5pt;
  font-weight: 800;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.3pt;
  color: #000;
  border-top: 0.5mm solid #000;
  background: #f0f0f0;
}

.card-reminder {
  padding: 1.5mm 3mm 1.5mm;
  font-size: 9pt;
  font-style: italic;
  line-height: 1.2;
  color: #555;
  border-top: 0.3mm solid #999;
  white-space: pre-wrap;
}

.card-section-label {
  padding: 1mm 3mm 0.5mm;
  font-size: 7pt;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.4pt;
  color: #555;
  border-top: 0.3mm solid #999;
}

.card-section-label:first-of-type {
  border-top: none;
}

.card-section-body {
  padding: 1mm 3mm 2mm;
  font-size: 11pt;
  line-height: 1.25;
  color: #000;
  white-space: pre-wrap;
}

.card-section-body b {
  font-weight: 800;
}
"""


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def render_card(card: dict) -> str:
    deck = card["deck"]
    name = card["name"]
    tags = card.get("tags", [])
    text = card.get("text", "")
    reminder = card.get("reminder", "")
    endgame = card.get("endgameText", "")
    icon = DECK_ICONS.get(deck, "")
    is_zone = "Zone" in name or name == "Presence"

    tags_row = ""
    if not is_zone:
        tags_inner = "".join(
            f'<span class="tag tag-{t.lower()}">{t}</span>' for t in sorted(tags))
        tags_row = f'<div class="card-tags">{tags_inner}</div>'

    if is_zone:
        setup = card.get("setupText", "")
        order = card.get("orderText", "")
        sections = ""
        if setup:
            sections += (f'<div class="card-section-label">Setup</div>'
                         f'<div class="card-section-body">{bold_keywords(setup)}</div>')
        if order:
            sections += (f'<div class="card-section-label">Order</div>'
                         f'<div class="card-section-body">{bold_keywords(order)}</div>')
        body_html = f'<div class="card-body" style="padding:0">{sections}</div>'
    elif text:
        body_html = f'<div class="card-body">{bold_keywords(text)}</div>'
    else:
        body_html = '<div class="card-body empty">— no effect —</div>'

    reminder_html = ""
    if reminder:
        reminder_html = f'<div class="card-reminder">{esc(reminder)}</div>'

    endgame_html = ""
    if endgame:
        endgame_html = f'<div class="card-endgame">{esc(endgame)}</div>'

    deck_label = name if "Zone" in name else deck.title()

    footer_html = ""
    if not is_zone:
        footer_html = f'<div class="card-footer">{icon} {esc(deck_label)}</div>'

    return (
        f'<div class="card deck-{deck}">'
        f'  <div class="card-header"><span class="icon">{icon}</span> {esc(name)}</div>'
        f'  {tags_row}'
        f'  {body_html}'
        f'  {reminder_html}'
        f'  {endgame_html}'
        f'  {footer_html}'
        f'</div>'
    )


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


import re

EVENT_EMOJIS = {
    "On Dawn": "☀️",
    "On Order": "🎯",
    "On Brawl": "💥",
    "On Rite": "✨",
    "On Feast": "🍖",
    "On Rumour": "👂",
    "On Harvest": "🌱",
}

_EVENT_KEYWORD = re.compile(
    r'\b(On Dawn|On Order|On Brawl|On Rite|On Feast|On Harvest|On Rumour)\b'
)

_BOLD_KEYWORDS = re.compile(
    r'\b('
    r'Brawl|Rite|Feast|Harvest|Rumour|Order'
    r'|Hunt|Discard|Domain|Season|Fields|Wares|Opportunities|Revelation|Tourney'
    r'|Requires'
    r')\b'
)

_INLINE_TAG = re.compile(
    r'\[('
    r'Discontent|Mob|Unit|Hunt|Trophy|Nature|Spiritual|Religion'
    r'|Knowledge|Labour|Amenity|Wealth|Chivalry|Land'
    r')\]'
)

def bold_keywords(text: str) -> str:
    """Wrap game keywords in <b> tags, add event emojis, and color [Tag] refs."""
    safe = esc(text)
    safe = _EVENT_KEYWORD.sub(
        lambda m: f'<b>{EVENT_EMOJIS[m.group(1)]} {m.group(1)}</b>', safe)
    safe = _BOLD_KEYWORDS.sub(r'<b>\1</b>', safe)
    safe = _INLINE_TAG.sub(
        lambda m: f'<span class="inline-tag inline-tag-{m.group(1).lower()}">[{m.group(1)}]</span>',
        safe,
    )
    return safe


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
# Markdown generation
# ---------------------------------------------------------------------------

DECK_FLAVOUR = {
    "claw":   "Violence, ambition, raw power, societal sentiment. The primal "
              "human element — anger, passion, desire, fear. The uncontrollable "
              "voice of the people that every civilisation must contend with.",
    "tree":   "Family, spirituality, harmony, roots, nature. Community bonds, "
              "ancestral wisdom, peaceful growth. The seasonal engine and "
              "communal heartbeat.",
    "wheat":  "Labour, agriculture, the common folk. The working class that "
              "sustains kingdoms — but every harvest comes with unrest.",
    "coin":   "Trade, commerce, social mobility. The merchant class and flow "
              "of wealth. The Wares evolve into a chaotic bazaar as players "
              "trade cards through it.",
    "candle": "Faith, religion, moral authority, divine right. Alternative "
              "path to power through spiritual influence.",
    "sword":  "Chivalry, martial prowess, feudal loyalty. The warrior "
              "aristocracy and feudal military order.",
}

DECK_NAMES = {
    "claw": "Claw", "tree": "Tree", "wheat": "Wheat",
    "coin": "Coin", "candle": "Candle", "sword": "Sword",
}


def _md_card_block(name: str, tags: list[str], text: str, icon: str,
                   reminder: str = "") -> str:
    """Return a fenced code block for a single card entry."""
    header = f"{icon}  {name.upper()}"
    tag_line = " ".join(f"[{t}]" for t in sorted(tags))
    lines = [header]
    if tag_line:
        lines.append(tag_line)
    if text:
        lines.append(text)
    inner = "\n".join(lines)
    block = f"```\n{inner}\n```"
    if reminder:
        block += f"\n\n> *{reminder}*"
    return block


def _md_zone_block(zc: dict, icon: str) -> str:
    """Return a fenced code block for a zone card with setup/order sections."""
    header = f"{icon}  {zc['name'].upper()}"
    setup = zc.get("setupText", "")
    order = zc.get("orderText", "")
    lines = [header]
    if setup:
        lines.append(f"SETUP: {setup}")
    if order:
        lines.append(order)
    inner = "\n".join(lines)
    return f"```\n{inner}\n```"


def generate_markdown(decks: dict) -> str:
    parts: list[str] = []

    parts.append("# Kingdoms — Card Catalogue\n")
    parts.append("All designed cards in one place, organised by deck.  \n"
                 "*Auto-generated by `print_cards.py` — do not edit by hand.*\n")

    # ── Zone cards ────────────────────────────────────────────────
    parts.append("---\n")
    parts.append("## Domain\n")
    presence = next(z for z in ZONE_CARDS if z["name"] == "Presence")
    parts.append(_md_zone_block(
        presence,
        DECK_ICONS.get(presence["deck"], ""),
    ))
    parts.append("")

    parts.append("---\n")
    parts.append("## Deck Zone Cards\n")
    parts.append("One per deck. Placed next to their draw pile at setup.\n")
    for zc in ZONE_CARDS:
        if zc["name"] == "Presence":
            continue
        parts.append(_md_zone_block(
            zc,
            DECK_ICONS.get(zc["deck"], ""),
        ))
        parts.append("")

    # ── Deck cards ────────────────────────────────────────────────
    for deck_key in ("claw", "tree", "wheat", "coin", "candle", "sword"):
        if deck_key not in decks:
            continue
        icon = DECK_ICONS.get(deck_key, "")
        label = DECK_NAMES[deck_key]
        flavour = DECK_FLAVOUR.get(deck_key, "")

        parts.append("---\n")
        parts.append(f"## {icon} {label} Deck Cards\n")
        if flavour:
            parts.append(f"> {flavour}\n")

        for card_def in decks[deck_key]:
            name = card_def["name"]
            tags = card_def["tags"]
            text = card_def.get("text", "")
            reminder = card_def.get("reminder", "")
            parts.append(_md_card_block(name, tags, text, icon, reminder))
            parts.append("")

    return "\n".join(parts)


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
                "setupText": zc.get("setupText", ""),
                "orderText": zc.get("orderText", ""),
                "endgameText": zc.get("endgameText", ""),
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
                    "text": card_def.get("text", ""),
                    "reminder": card_def.get("reminder", ""),
                })

    # 3. Report any cards without text
    missing = {c["name"] for c in cards
               if not c.get("text") and not c.get("orderText") and not c.get("reminder")}
    if missing:
        print(f"⚠  No text for: {', '.join(sorted(missing))}")

    # 4. Generate HTML
    html = generate_html(cards)
    out_html = Path(__file__).parent / "cards.html"
    out_html.write_text(html, encoding="utf-8")

    total_pages = math.ceil(len(cards) / CARDS_PER_PAGE)
    print(f"✅  Generated {out_html.name}: {len(cards)} cards on {total_pages} pages")
    print(f"    Open in browser → Print → Save as PDF (A4, no margins)")

    # 5. Generate Markdown catalogue
    md = generate_markdown(decks)
    out_md = Path(__file__).parent / "game-cards.md"
    out_md.write_text(md, encoding="utf-8")
    print(f"✅  Generated {out_md.name}")


if __name__ == "__main__":
    main()
