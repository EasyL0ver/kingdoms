# Simulation 12 — Automated Run

**Players:** Alice, Bob, Charlie (3 players, 10 rounds = 30 turns)

---

## Initial State

Season 1: **Sowing** [Knowledge], **Nomad** [Culture], **Harvest**, **Forage**
Fields (7): Granary, Famine, Tavern, Famine, Feed the Commoners, Mill, Plough
Piles: Claw 40, Tree 37, Wheat 10, Coin 5

---

## Round 1 (Turns 1–3)

**T1 — Alice:** Takes **Sowing** [Knowledge] from Season.
→ Domain: Sowing

**T2 — Bob:** Takes **Harvest** from Season.
  → Drafted: triggers **Harvest** globally!
  → Fields refilled to 7
→ Domain: *(empty)*
→ Discard: Harvest

**T3 — Charlie:** Draws Claw (2): **Raid** [Unit][Rabble][Discontent], **Worship of the Hunt** [Spiritual].
→ Domain: Raid, Worship of the Hunt

## Round 2 (Turns 4–6)

**T4 — Alice:** Draws Claw (2): **Armament** [Knowledge], **Racketeering** [Discontent].
→ Domain: Sowing, Armament, Racketeering

**T5 — Bob:** Draws Claw (2): **Warband** [Discontent], **Foray** [Discontent].
→ Domain: Warband, Foray
→ Discard: Harvest

**T6 — Charlie:** Takes **Forage** from Season.
→ Domain: Raid, Worship of the Hunt, Forage

## Round 3 (Turns 7–9)

**T7 — Alice:** Draws Claw (2): **Marauders** [Unit][Rabble][Discontent], **Land Grab** [Discontent].
→ Domain: Sowing, Armament, Racketeering, Marauders, Land Grab

**T8 — Bob:** Draws Claw (2): **Chiefdom** [Allegiance], **Uprising** [Discontent].
  → Drafted: **Uprising** — Brawl in own Domain, no benefits (spoils discarded)
→ Domain: Warband, Foray, Chiefdom, Uprising
→ Discard: Harvest

**T9 — Charlie:** Activates **Forage**.
  → Top 3: Solstice, Worship of the Rain, Pasture. Takes Pasture, discards Forage.
→ Domain: Raid, Worship of the Hunt, Pasture
→ Discard: Solstice, Worship of the Rain, Forage

## Round 4 (Turns 10–12)

**T10 — Alice:** Draws Claw (2): **Ingenuity** [Craftsmanship][Discontent], **Share the Spoils**.
  → Drafted: draws **Rumour** from Coin
  → Rumour triggers Rumour globally → to discard
→ Domain: Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils
→ Discard: Rumour

---

### === STATE AFTER TURN 10 ===

**Alice** (7 cards): Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils
  Discard: Rumour
**Bob** (4 cards): Warband, Foray, Chiefdom, Uprising
  Discard: Harvest
**Charlie** (3 cards): Raid, Worship of the Hunt, Pasture
  Discard: Solstice, Worship of the Rain, Forage

Season: Nomad
Fields (7): Granary, Famine, Tavern, Famine, Feed the Commoners, Mill, Plough
Piles remaining: Claw 28, Tree 34, Wheat 10, Coin 4

---

**T11 — Bob:** Draws Claw (2): **Incite**, **Scavenge** [Unit][Rabble][Discontent].
→ Domain: Warband, Foray, Chiefdom, Uprising, Scavenge
→ Discard: Harvest, Incite

**T12 — Charlie:** Draws Claw (2): **Duel**, **Warband** [Discontent].
→ Domain: Raid, Worship of the Hunt, Pasture, Duel, Warband
→ Discard: Solstice, Worship of the Rain, Forage

## Round 5 (Turns 13–15)

**T13 — Alice:** Draws Claw (2): **Uprising** [Discontent], **Land Grab** [Discontent].
  → Drafted: **Uprising** — Brawl in own Domain, no benefits (spoils discarded)
→ Domain: Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils, Uprising, Land Grab
→ Discard: Rumour

**T14 — Bob:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (9 cards)
→ Domain: Warband, Foray, Chiefdom, Uprising, Scavenge
→ Discard: Harvest, Incite

**T15 — Charlie:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (9 cards)
→ Domain: Raid, Worship of the Hunt, Pasture, Duel, Warband
→ Discard: Solstice, Worship of the Rain, Forage

## Round 6 (Turns 16–18)

**T16 — Alice:** Draws Claw (2): **Foray** [Discontent], **Marauders** [Unit][Rabble][Discontent].
→ Domain: Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils, Uprising, Land Grab, Foray, Marauders
→ Discard: Rumour

**T17 — Bob:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (11 cards)
    → Foray: Alice draws Pasture from Tree
→ Domain: Warband, Foray, Chiefdom, Uprising, Scavenge
→ Discard: Harvest, Incite

**T18 — Charlie:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (12 cards)
    → Foray: Alice draws Sky Dance from Tree
→ Domain: Raid, Worship of the Hunt, Pasture, Duel, Warband
→ Discard: Solstice, Worship of the Rain, Forage

## Round 7 (Turns 19–21)

**T19 — Alice:** Takes **Nomad** [Culture] from Season.
  → Season empty → New Season: Highlander, Pathfinding, Nomad, Solstice
→ Domain: Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils, Uprising, Land Grab, Foray, Marauders, Pasture, Sky Dance, Nomad
→ Discard: Rumour

**T20 — Bob:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (14 cards)
    → Foray: Alice draws Pasture from Tree
→ Domain: Warband, Foray, Chiefdom, Uprising, Scavenge
→ Discard: Harvest, Incite

---

### === STATE AFTER TURN 20 ===

**Alice** (15 cards): Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils, Uprising, Land Grab, Foray, Marauders, Pasture, Sky Dance, Nomad, Pasture
  Discard: Rumour
**Bob** (5 cards): Warband, Foray, Chiefdom, Uprising, Scavenge
  Discard: Harvest, Incite
**Charlie** (5 cards): Raid, Worship of the Hunt, Pasture, Duel, Warband
  Discard: Solstice, Worship of the Rain, Forage

Season: Highlander, Pathfinding, Nomad, Solstice
Fields (7): Granary, Famine, Tavern, Famine, Feed the Commoners, Mill, Plough
Piles remaining: Claw 20, Tree 27, Wheat 10, Coin 4

---

**T21 — Charlie:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (15 cards)
    → Foray: Alice draws Sacred Grove from Tree
→ Domain: Raid, Worship of the Hunt, Pasture, Duel, Warband
→ Discard: Solstice, Worship of the Rain, Forage

## Round 8 (Turns 22–24)

**T22 — Alice:** Draws Claw (2): **Poach** [Unit][Rabble][Hunt][Discontent], **Raid** [Unit][Rabble][Discontent].
→ Domain: Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils, Uprising, Land Grab, Foray, Marauders, Pasture, Sky Dance, Nomad, Pasture, Sacred Grove, Poach, Raid
→ Discard: Rumour

**T23 — Bob:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (18 cards)
    → Foray: Alice draws Oral Tradition from Tree
→ Domain: Warband, Foray, Chiefdom, Uprising, Scavenge
→ Discard: Harvest, Incite

**T24 — Charlie:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (19 cards)
    → Foray: Alice draws Crags from Tree
→ Domain: Raid, Worship of the Hunt, Pasture, Duel, Warband
→ Discard: Solstice, Worship of the Rain, Forage

## Round 9 (Turns 25–27)

**T25 — Alice:** Takes **Nomad** [Culture] from Season.
  → Replaces existing culture Nomad
→ Domain: Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils, Uprising, Land Grab, Foray, Marauders, Pasture, Sky Dance, Pasture, Sacred Grove, Poach, Raid, Oral Tradition, Crags, Nomad
→ Discard: Rumour, Nomad

**T26 — Bob:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (20 cards)
    → Foray: Alice draws Withered Crop from Tree
→ Domain: Warband, Foray, Chiefdom, Uprising, Scavenge
→ Discard: Harvest, Incite

**T27 — Charlie:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (21 cards)
  → Replaces existing culture Nomad
    → Foray: Alice draws Highlander from Tree
→ Domain: Raid, Worship of the Hunt, Pasture, Duel, Warband
→ Discard: Solstice, Worship of the Rain, Forage

## Round 10 (Turns 28–30)

**T28 — Alice:** Draws Claw (2): **Racketeering** [Discontent], **Ingenuity** [Craftsmanship][Discontent].
  → Drafted: draws **Mine** [Labour] from Coin
  → Drafted: discards a Crags to keep Mine
→ Domain: Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils, Uprising, Land Grab, Foray, Marauders, Pasture, Sky Dance, Pasture, Sacred Grove, Poach, Raid, Oral Tradition, Withered Crop, Highlander, Racketeering, Mine, Ingenuity
→ Discard: Rumour, Nomad, Nomad, Crags

**T29 — Bob:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (23 cards)
    → Foray: Alice draws Crags from Tree
→ Domain: Warband, Foray, Chiefdom, Uprising, Scavenge
→ Discard: Harvest, Incite

**T30 — Charlie:** Activates **Warband** [Discontent].
  → Triggers Brawl in Alice's Domain (24 cards)
    → Foray: Alice draws Harvest from Tree
→ Domain: Raid, Worship of the Hunt, Pasture, Duel, Warband
→ Discard: Solstice, Worship of the Rain, Forage

---

### === STATE AFTER TURN 30 ===

**Alice** (25 cards): Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils, Uprising, Land Grab, Foray, Marauders, Pasture, Sky Dance, Pasture, Sacred Grove, Poach, Raid, Oral Tradition, Withered Crop, Highlander, Racketeering, Mine, Ingenuity, Crags, Harvest
  Discard: Rumour, Nomad, Nomad, Crags
**Bob** (5 cards): Warband, Foray, Chiefdom, Uprising, Scavenge
  Discard: Harvest, Incite
**Charlie** (5 cards): Raid, Worship of the Hunt, Pasture, Duel, Warband
  Discard: Solstice, Worship of the Rain, Forage

Season: Highlander, Pathfinding, Solstice
Fields (7): Granary, Famine, Tavern, Famine, Feed the Commoners, Mill, Plough
Piles remaining: Claw 16, Tree 20, Wheat 10, Coin 3

---

---

## Epilogue

**Alice** — 25 cards in Domain
  Domain: Sowing, Armament, Racketeering, Marauders, Land Grab, Ingenuity, Share the Spoils, Uprising, Land Grab, Foray, Marauders, Pasture, Sky Dance, Pasture, Sacred Grove, Poach, Raid, Oral Tradition, Withered Crop, Highlander, Racketeering, Mine, Ingenuity, Crags, Harvest
  Tags: [Land]×3, [Culture]×1, [Spiritual]×2, [Craftsmanship]×2, [Knowledge]×3, [Rabble]×4, [Hunt]×1, [Unit]×4, [Labour]×1, [Discontent]×12, [Nature]×4

**Bob** — 5 cards in Domain
  Domain: Warband, Foray, Chiefdom, Uprising, Scavenge
  Tags: [Discontent]×4, [Unit]×1, [Rabble]×1, [Allegiance]×1

**Charlie** — 5 cards in Domain
  Domain: Raid, Worship of the Hunt, Pasture, Duel, Warband
  Tags: [Land]×1, [Spiritual]×1, [Rabble]×1, [Unit]×1, [Discontent]×2, [Nature]×1

### Pile Status
Claw: 16 remaining | Tree: 20 remaining | Wheat: 10 remaining | Coin: 3 remaining
