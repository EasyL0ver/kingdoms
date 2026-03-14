# Simulation — AI-Driven (v2)

**Players:** Alice, Bob, Charlie (3 players, 34 rounds = 100 turns)

---

## Initial State

Season: Forage, Nomad, Herbalism, Crags
Fields (7): Apprenticeship, Granary, Plough, Tavern, Mill, Militia, Militia
Piles: Claw 42, Tree 37, Wheat 10, Coin 5, Candle 1

---

## Round 1 (Turns 1–3)

**T1 — Alice:** Takes **Crags** from Season. *Foundation card that enables Highlander culture and provides Brawl defense later.* Crags has [Nature] and [Land] tags, giving Alice her first winning tag for the Tree victory condition.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Crags|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Crags → Alice's Domain

</details>

**T2 — Bob:** Takes **Nomad** from Season. *Need culture foundation early to build strategy around.* Nomad is Drafted — requires Pasture in Domain or discards itself. Bob has no Pasture, so Nomad goes to discard.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON_DISCARD|Nomad|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON_DISCARD Nomad → Bob's discard

</details>

**T3 — Charlie:** Takes **Forage** from Season. *Need to dig through Tree pile to find key cards.* Forage activates immediately — puts top 3 Tree cards (Nomad, Pasture, Withered Crop) into Charlie's discard. Charlie chooses to discard Forage to take Pasture to Domain instead.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Forage|Charlie
DRAW_DISCARD|tree|3|Charlie
MOVE|Charlie|Forage|DISCARD
MOVE_DISCARD|Charlie|Pasture
```

</details>

<details><summary>📋 Ops Trace (6 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Forage → Charlie's Domain
- ✅ DRAW_DISCARD tree → Nomad → Charlie's discard
- ✅ DRAW_DISCARD tree → Pasture → Charlie's discard
- ✅ DRAW_DISCARD tree → Withered Crop → Charlie's discard
- ✅ MOVE Forage Charlie's Domain → Charlie's discard
- ✅ MOVE_DISCARD Pasture Charlie's discard → Charlie's Domain

</details>

## Round 2 (Turns 4–6)

**T4 — Alice:** Takes **Herbalism** from Season. *Need knowledge cards to build economy and Herbalism can recover key cards later.* No immediate effects as Herbalism has no Drafted text.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Herbalism|Alice
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Herbalism → Alice's Domain
- 🔄 Season auto-refilled: [Solstice, Sky Dance, Forage, Sowing]

</details>

**T5 — Bob:** Takes **Solstice** from Season. *Building towards Harvest synergy since Fields are full of good cards.* Solstice goes to Domain — no Drafted effect, just a passive On Harvest card for future triggers.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Solstice|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Solstice → Bob's Domain

</details>

**T6 — Charlie:** Takes **Sowing** from Season. *Need Wheat access to build economy and Charlie has Pasture to meet the requirement.* Sowing moves to Domain, enabling Wheat zone activation with 2+ [Nature] cards (Charlie has 1 Pasture, needs 1 more).

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Sowing|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Sowing → Charlie's Domain

</details>

## Round 3 (Turns 7–9)

**T7 — Alice:** Takes **Sky Dance** from Season. *Need repeatable Rite trigger to build spiritual engine.* Sky Dance enables free Rite activation every turn going forward.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Sky Dance|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Sky Dance → Alice's Domain

</details>

**T8 — Bob:** Activates **Sky Dance** from Alice's Domain using his Solstice access. *Need to trigger Rite to get value from my Solstice card.* Sky Dance triggers Rite globally. Bob's Solstice responds: On Rite lets Bob choose Brawl, Rumour, or Rite for all players of his culture — but Bob has no culture card, so only his own Domain triggers. Bob chooses Rumour. No other players respond to the Rite event.

<details><summary>🎯 Raw OPS</summary>

```
None
```

</details>

<details><summary>📋 Ops Trace (0 applied, 1 violations)</summary>

- ❌ UNKNOWN OP: None — full line: None

</details>

> 🔄 Retry 1 — illegal ops detected:

> UNKNOWN OP: None — full line: None

> **Retry response:**
**T8 — Bob:** Activates **Solstice** from Domain. *Need to spread culture and help allies since I have minimal cards.* On Harvest effect triggers — chooses to place Nomad from discard into Charlie's Domain, forcing culture regardless of prerequisites. Charlie now has Nomad [Culture] despite lacking Pasture.

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ MOVE_DISCARD Nomad Bob's discard → Bob's Domain
- ✅ MOVE Nomad Bob's Domain → Charlie's Domain

</details>

**T9 — Charlie:** Activates **Sowing** to access the Wheat zone, taking **Apprenticeship** and **Granary** from Fields. *Building economy with two key Wheat cards while having the Nature requirements.* Draws **Warband** and **Land Grab** from Claw as tax for the two cards taken.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_FIELDS|Apprenticeship|Charlie
TAKE_FIELDS|Granary|Charlie
DRAW|claw|2|Charlie
```

</details>

<details><summary>📋 Ops Trace (4 applied, 0 violations)</summary>

- ✅ TAKE_FIELDS Apprenticeship → Charlie's Domain
- ✅ TAKE_FIELDS Granary → Charlie's Domain
- ✅ DRAW claw → Warband → Charlie's Domain
- ✅ DRAW claw → Land Grab → Charlie's Domain

</details>

## Round 4 (Turns 10–12)

**T10 — Alice:** Activates **Sky Dance** to trigger Rite in her Domain. *Need to build spiritual engine early before others get established.* No On Rite cards respond yet, so the event fires but has no mechanical effects this turn.

OPS:

---

### === STATE AFTER TURN 10 ===

**Alice** (3 cards): Crags, Herbalism, Sky Dance
**Bob** (1 cards): Solstice
**Charlie** (7 cards): Pasture, Sowing, Nomad, Apprenticeship, Granary, Warband, Land Grab
  Discard: Nomad, Withered Crop, Forage

Season: Forage
Fields (5): Plough, Tavern, Mill, Militia, Militia
Piles: Claw 40, Tree 30, Wheat 10, Coin 5

---

**T11 — Bob:** Activates **Sky Dance** to trigger Rite globally. *Need to leverage Alice's spiritual engine and my Solstice for card advantage.* Alice's Sacred Grove responds: triggers another Rite in Alice's Domain. Alice's Sky Dance responds: triggers a third Rite. Bob's Solstice responds to all three Rites: On Harvest chooses to place Nomad from Charlie's discard into Charlie's Domain (Charlie already has Nomad, so existing one discarded first), then all Nomad-culture players (Charlie) draw from Tree.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Nomad|DISCARD
MOVE_DISCARD|Charlie|Nomad
DRAW|tree|1|Charlie
```

</details>

<details><summary>📋 Ops Trace (3 applied, 0 violations)</summary>

- ✅ MOVE Nomad Charlie's Domain → Charlie's discard
- ✅ MOVE_DISCARD Nomad Charlie's discard → Charlie's Domain
- ✅ DRAW tree → Sacred Grove → Charlie's Domain

</details>

**T12 — Charlie:** Activates **Warband** to trigger Brawl in Alice's Domain (largest with 3 cards). *Time to capitalize on my strong position and strip cards from the leader.* Alice has no Brawl defenders, so the Brawl resolves — Alice gives Charlie one card from her Domain. Charlie takes Herbalism as it's the most versatile utility card.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Alice|Herbalism|DOMAIN|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Herbalism Alice's Domain → Charlie's Domain

</details>

## Round 5 (Turns 13–15)

**T13 — Alice:** Activates **Sky Dance** to trigger Rite. *Need to build spiritual engine and Charlie has multiple Spiritual responders.* Rite fires globally. Charlie's Sacred Grove responds: chooses to trigger Rite again in Charlie's Domain. Charlie's Sacred Grove responds to its own second Rite: looks at top 3 Tree cards (Withered Crop, Oral Tradition, Highlander) and takes no Spiritual cards since none are present, puts them back in same order.

OPS:

**T14 — Bob:** Activates **Sky Dance** to trigger Rite in his Domain. *Need to build spiritual engine with Alice before Charlie's massive Domain becomes unstoppable.* Rite fires globally. Alice's Sacred Grove responds but she has no Spiritual cards to scry for, so she triggers Rite in her Domain instead. No other responses — both Rite triggers resolve with no further effects since no other On Rite cards are in play.

OPS:

**T15 — Charlie:** Activates **Warband** to trigger Brawl in Alice's Domain (tied with Bob at 2 cards, choosing Alice). *Alice has no Mob cards to benefit me, but this pressures the spiritual player.* Alice has no On Brawl responders, so no cards change hands.

OPS:

## Round 6 (Turns 16–18)

**T16 — Alice:** Activates **Sky Dance** to trigger Rite in her Domain. *Need to build spiritual engine and Charlie has multiple responders.* No cards in Alice's Domain respond to Rite, but Charlie's Sacred Grove responds: chooses to trigger another Rite in Charlie's Domain. Charlie's Sacred Grove responds to its own triggered Rite: chooses to look at top 3 Tree cards (Withered Crop, Oral Tradition, Highlander) and takes no Spiritual cards since none are present.

OPS:

**T17 — Bob:** Activates **Solstice**. *Perfect timing with Alice sharing my Highlander culture and Charlie needing cultural spread.* On Harvest triggers — Bob chooses to place Highlander from Charlie's discard into Alice's Domain, bypassing the Crags requirement. Alice now has both Sky Dance and culture access.

<details><summary>🎯 Raw OPS</summary>

```
MOVE_DISCARD|Charlie|Highlander|DOMAIN|Alice
```

</details>

<details><summary>📋 Ops Trace (0 applied, 1 violations)</summary>

- ❌ ILLEGAL: 'Highlander' not in Charlie's discard. Has: [Withered Crop, Forage, Nomad]

</details>

> 🔄 Retry 1 — illegal ops detected:

> ILLEGAL: 'Highlander' not in Charlie's discard. Has: [Withered Crop, Forage, Nomad]

> **Retry response:**
**T17 — Bob:** Activates **Solstice** to trigger Harvest in his Domain. *Need to refill the nearly empty Fields and capitalize on being the only one with an On Harvest card.* Harvest fires globally — Fields refill from 5 to 7. Bob's own Solstice responds: On Harvest lets Bob place Nomad from Charlie's discard into Alice's Domain, forcing her to share Nomad culture.

<details><summary>📋 Ops Trace (2 applied, 1 violations)</summary>

- ✅ REFILL_FIELDS +2: [Tavern, Plough]
- ✅ MOVE_DISCARD Nomad Charlie's discard → Charlie's Domain
- ❌ ILLEGAL: 'Nomad' not in Bob's Domain. Has: [Solstice]

</details>

> 🔄 Retry 2 — illegal ops detected:

> ILLEGAL: 'Nomad' not in Bob's Domain. Has: [Solstice]

> **Retry response:**
**T17 — Bob:** Activates **Solstice**. *Charlie has the strongest Domain with 9 cards, making him the biggest threat.* On Harvest triggers globally — Alice and Charlie also share Nomad culture. All three players draw from Tree. Fields refill from 5 to 7.

<details><summary>📋 Ops Trace (4 applied, 0 violations)</summary>

- ✅ DRAW tree → Withered Crop → Alice's Domain
- ✅ DRAW tree → Oral Tradition → Bob's Domain
- ✅ DRAW tree → Highlander → Charlie's Domain
- ✅ REFILL_FIELDS +2: [Tavern, Plough]

</details>

**T18 — Charlie:** Activates **Warband** to trigger Brawl in Alice's Domain (tied at 3 cards, but Alice has fewer defenses). *Alice has no Militia or Crags defense, making her the safest target.* Brawl triggers — Alice has no responders, so Charlie gets to take 1 card from Alice. Charlie takes Alice's **Sky Dance** for the [Spiritual] tag and repeatable Rite engine.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Alice|Sky Dance|DOMAIN|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Sky Dance Alice's Domain → Charlie's Domain

</details>

## Round 7 (Turns 19–21)

**T19 — Alice:** Activates **Withered Crop** to access Wheat zone, taking **Plough** from Fields and drawing **Duel** from Claw as tax. *Need to build economy and Plough enables Feast/Wheat flexibility on future Harvests.* Plough is Drafted — requires Pasture or self-discard, but Alice has no Pasture, so Plough discards itself.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_FIELDS|Plough|Alice
DRAW|claw|1|Alice
MOVE|Alice|Plough|DISCARD
```

</details>

<details><summary>📋 Ops Trace (3 applied, 0 violations)</summary>

- ✅ TAKE_FIELDS Plough → Alice's Domain
- ✅ DRAW claw → Duel → Alice's Domain
- ✅ MOVE Plough Alice's Domain → Alice's discard

</details>

**T20 — Bob:** Activates **Oral Tradition**, discarding Solstice to draw from Candle. *Need to access the powerful Worship of the Flame before the pile runs out.* Gets Worship of the Flame — the last Candle card. Charlie is dominating with 11 cards including multiple engines, so need to build spiritual power for late game.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Bob|Solstice|DISCARD
DRAW|candle|1|Bob
```

</details>

<details><summary>📋 Ops Trace (3 applied, 0 violations)</summary>

- ✅ MOVE Solstice Bob's Domain → Bob's discard
- ✅ DRAW candle → Worship of the Flame → Bob's Domain
- 🏁 GAME OVER — candle zone fully depleted!

</details>

---

### === STATE AFTER TURN 20 ===

**Alice** (3 cards): Crags, Withered Crop, Duel
  Discard: Plough
**Bob** (2 cards): Oral Tradition, Worship of the Flame
  Discard: Solstice
**Charlie** (11 cards): Pasture, Sowing, Apprenticeship, Granary, Warband, Land Grab, Nomad, Sacred Grove, Herbalism, Highlander, Sky Dance
  Discard: Withered Crop, Forage, Nomad

Season: Forage
Fields (6): Tavern, Mill, Militia, Militia, Tavern, Plough
Piles: Claw 39, Tree 26, Wheat 8, Coin 5

---

### GAME ENDS — candle zone fully depleted!

---

## Epilogue

**Alice** — 3 cards
  Domain: Crags, Withered Crop, Duel
  Tags: [Land]×1, [Nature]×1

**Bob** — 2 cards
  Domain: Oral Tradition, Worship of the Flame
  Tags: [Knowledge]×1, [Spiritual]×1

**Charlie** — 11 cards
  Domain: Pasture, Sowing, Apprenticeship, Granary, Warband, Land Grab, Nomad, Sacred Grove, Herbalism, Highlander, Sky Dance
  Tags: [Culture]×2, [Discontent]×2, [Knowledge]×2, [Labour]×2, [Land]×1, [Nature]×2, [Spiritual]×2

### Stats
API calls: 23 | Piles: Claw 39, Tree 26, Wheat 8, Coin 5, Candle 0
