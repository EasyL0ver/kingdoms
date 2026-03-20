# Card Text Templating Guide

> This guide covers two concerns:
> 1. **Card text authoring** — how to write text in `decks.json` (the source of truth)
> 2. **Render behaviour** — what `print_cards.py` does automatically (marked with 🖨️)
>
> When writing card text, only worry about authoring rules. Render features are handled by the script.

## Structure

```
On Event — effect text.
On Event (prereq) — effect text.
On Event (*italic prereq*) — effect text.
```

- **One ability per line** — use `\n` in JSON to separate abilities
- **Split conditional abilities** — if behavior differs by condition, write separate lines

## Prerequisites

Parenthetical after event name, no "Requires" keyword:
```
On Order (3+ [Labour]) — ...
On Brawl (active player has Kinship) — ...
On Dawn (Opportunities) — ...
```

Turn-based prereqs use italics:
```
On Harvest (*your turn*) — ...
On Harvest (*not your turn*) — ...
On Rite (*Worship of the Dawn in play*) — ...
```

## Singular Quantities

Use **"a"** not **"1"** for singular amounts:
- ✅ draw **a** card · discard **a** card · return **a** [Mob]
- ❌ draw **1** card · discard **1** card · return **1** [Mob]

Numeric amounts (2+) keep the number:
- ✅ draw **2** cards · discard **5** Claw cards

## Drawing

```
draw a card from the Claw deck
draw 2 cards from the Claw deck
draw cards from the Claw deck equal to ...
draw cards from the Claw and Tree decks equal to ...
```

## Discarding

Always specify location:
```
discard a card from your Domain
every player discards a card from their Domain
discard the top card of the Claw deck
```

Self-discard uses card name, placed at the end of the ability:
```
Discard Reaping.
Discard Blood Feud, then ...
```

If the card has a choice or complex effect, put the self-discard on its own line after:
```
On Rumour — choose one: • *Panic* — draw 2 cards from the Claw deck. • *Fortify* — return a [Discontent] to top of the Claw deck.
Discard Tidings.
```

## Returning

Always specify "top of":
```
return a card from your discard to top of the Claw deck
return a [Discontent] to top of the Claw deck
```

## Acquiring Cards

Use **"put into your Domain"** not "take":
```
put a card from the Season into your Domain
put all [Land] cards from the Season into your Domain
put any [Spiritual] cards into your Domain
```

## Firing Events

Event name + scope, no preposition:
```
Brawl your Domain          (not "Brawl in your Domain")
Rite every Domain           (not "Rite in every Domain")
Harvest your Domain
Rumour your Domain
Order the Coin zone         (not "Order on the Coin zone")
```

## Terminology

| ✅ Use | ❌ Don't use |
|--------|-------------|
| Domain (capitalized) | domain |
| discard | dump, sacrifice, slay |
| remove from the game | purge, swallow |
| active player | attacker, controller, Brawl starter |
| Kinship | culture ally, shares your culture |
| triggers | fires |
| deck | pile |

## Formatting Markers (authored in JSON)

| Marker | Renders as | Use for |
|--------|-----------|---------|
| `*text*` | *italic* | prereqs, mode names (Panic, Fortify) |
| `[Tag]` | colored bold 🖨️ | tag references in text |
| `\n` | line break | separating abilities |
| `• option` | bullet | choice lists (each on own line) |

## 🖨️ Bold Keywords (auto-bolded by renderer)

Events: Brawl, Rite, Feast, Harvest, Rumour, Order, Hunt
Locations: Season, Fields, Wares, Opportunities, Revelation, Tourney

**Not bolded:** Domain, Discard

> You don't need to mark these in JSON — `print_cards.py` detects and bolds them automatically.

## 🖨️ Event Emojis (added by renderer, HTML only)

☀️ Dawn · 🎯 Order · 💥 Brawl · ✨ Rite · 🍖 Feast · 👂 Rumour · 🌱 Harvest

> Emojis are prepended automatically when rendering. Do **not** put emojis in `decks.json`.

## 🖨️ Inline Tag Coloring (added by renderer)

`[Tag]` references in card text are automatically color-coded in HTML to match the tag bar colors.

> Just write `[Trophy]` in JSON — the renderer handles the styling.

## 🖨️ Tags Display

- Sorted alphabetically in tag bar
- Cards with no tags show grey italic "No Tag" badge
- Reminder text: use `"reminder"` property in JSON (renders italic, grey, small)

## Examples

**Simple:**
```
On Feast — draw a card from the Claw deck.
```

**With prereq:**
```
On Order (3+ [Labour]) — Order the Coin zone. Rumour your Domain.
```

**Split abilities:**
```
On Brawl (*your turn*) — discard a card from your Domain.
On Brawl (*not your turn*) — give a card from your Domain to the active player.
```

**Choice:**
```
On Order — choose one:
• Order the Wheat zone.
• Remove the Reaping card from your discard from the game, then Harvest your Domain.
```
