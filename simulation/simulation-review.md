# Simulation — AI-Driven (v2)

**Players:** Alice, Bob, Charlie (3 players, 14 rounds = 40 turns)

---

## Initial State

Season: Worship of Fertility, Nomad, Pathfinding, Sowing
Fields (7): Famine, Plough, Granary, Militia, Famine, Plough, Mill
Piles: Claw 42, Tree 37, Wheat 10, Coin 5, Candle 1

---

## Round 1 (Turns 1–3)

**T1 — Alice:** Takes **Pathfinding** from Season. *Early Pathfinding with its [Knowledge] tag creates a snowball engine — each Knowledge card drawn increases future draws, and it's the strongest scaling card in Tree.* Pathfinding enters Alice's Domain.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Pathfinding|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Pathfinding → Alice's Domain

</details>

**T2 — Bob:** Takes **Sowing** from Season. *Grabbing the Wheat gateway early — once I get 2 Nature cards, I'll have access to Fields without needing diplomacy.* Sowing has no Drafted text, enters Domain normally.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Sowing|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Sowing → Bob's Domain

</details>

**T3 — Charlie:** Takes **Worship of Fertility** from Season. *Starting empty, need to build a foundation — Worship of Fertility is [Nature][Spiritual] giving two valuable tags and Rite synergy for later.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Worship of Fertility|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Worship of Fertility → Charlie's Domain

</details>

## Round 2 (Turns 4–6)

**T4 — Alice:** Draws from Claw, getting **Raid**. *Pathfinding needs Knowledge cards to snowball — Claw offers faster card acquisition than the single Nomad in Season, and Raid can be planted in opponents later via Incite.* Raid has no Drafted effect, stays in Domain.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|1|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW claw → Raid → Alice's Domain

</details>

**T5 — Bob:** Activates Wheat zone via Sowing (has 0 [Nature] cards — wait, Sowing requires 2+ [Nature]). *Bob cannot activate Wheat — Sowing's prerequisite not met.* Instead, Bob draws from Claw. Draws **Ingenuity** [Craftsmanship][Discontent] — Drafted triggers: draw 1 from Coin. Bob draws **Mine** from Coin. Mine is Drafted: requires Crags or discard Mine. Bob has no Crags — Mine goes to discard.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|1|Bob
DRAW_DISCARD|coin|1|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW claw → Ingenuity → Bob's Domain
- ✅ DRAW_DISCARD coin → Mine → Bob's discard

</details>

**T6 — Charlie:** Takes **Sacred Grove** from Season (via Tree zone). *Sacred Grove is the cornerstone Spiritual card — it gives repeatable Rite triggers which synergize perfectly with Worship of Fertility already in Domain.* No Drafted effect. Season now has 0 cards and will auto-refill.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Sacred Grove|Charlie
```

</details>

<details><summary>📋 Ops Trace (0 applied, 1 violations)</summary>

- ❌ ILLEGAL: 'Sacred Grove' not in Season. Season has: [Nomad]

</details>

> 🔄 Retry 1 — illegal ops detected:

> ILLEGAL: 'Sacred Grove' not in Season. Season has: [Nomad]

> **Retry response:**
**T6 — Charlie:** Draws from **Claw** zone, receiving **Ingenuity** and **Scavenge**. *Building toward [Trophy] tags while Worship of Fertility waits for Rite triggers.* Ingenuity is Drafted — Charlie draws 1 from Coin, getting **Rumour**. Rumour is Drafted — triggers Rumour globally. No On Rumour cards in any Domain, so no further effects. Scavenge enters Charlie's Domain as a [Mob] card.

<details><summary>📋 Ops Trace (3 applied, 0 violations)</summary>

- ✅ DRAW claw → Ingenuity → Charlie's Domain
- ✅ DRAW claw → Scavenge → Charlie's Domain
- ✅ DRAW_DISCARD coin → Rumour → Charlie's discard

</details>

## Round 3 (Turns 7–9)

**T7 — Alice:** Activates **Pathfinding** to draw 1 card from Tree (1 [Knowledge] in Domain). *Building toward Tree depletion with my Nature strategy — Pathfinding scales with more Knowledge.* Draws **Sacred Grove** [Nature][Spiritual] — not Drafted, goes to Domain. Sacred Grove gives Alice her first [Nature] tag and a powerful Rite engine.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|1|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW tree → Sacred Grove → Alice's Domain

</details>

**T8 — Bob:** Activates the Wheat zone via Sowing (has 0 [Nature] — wait, checking Sowing: requires 2+ [Nature]). *Bob has no [Nature] cards, so Sowing doesn't grant access.* Instead, Bob takes **Nomad** from Season. Nomad is Drafted — requires a Pasture in Domain or discard itself. Bob has no Pasture, so Nomad is discarded. *Fishing for the next Season cards since Wheat access isn't available yet.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON_DISCARD|Nomad|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ TAKE_SEASON_DISCARD Nomad → Bob's discard
- 🔄 Season auto-refilled: [Forage, Harvest, Crags, Gathering]

</details>

**T9 — Charlie:** Takes **Harvest** from Season. *Worship of Fertility in Domain means triggering Harvest will chain into a Rite, building my Spiritual engine.* Harvest is Drafted — triggers Harvest globally, then discards itself. Fields refill from 7 to 7 (already full, no change). Charlie's Worship of Fertility responds: On Harvest triggers Rite in Charlie's Domain. No other On Rite cards respond — the Rite resolves with no further effect.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON_DISCARD|Harvest|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON_DISCARD Harvest → Charlie's discard

</details>

## Round 4 (Turns 10–12)

**T10 — Alice:** Activates **Sacred Grove**, choosing to trigger Rite in her Domain. *With Pathfinding already in play, adding more [Spiritual] cards will accelerate her Knowledge-based draw engine.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Alice's Domain (the Rite triggerer). Harvest fires — Fields refill from 7 to 7 (already full, no change). No On Harvest responders in Alice's Domain.

OPS:

---

### === STATE AFTER TURN 10 ===

**Alice** (3 cards): Pathfinding, Raid, Sacred Grove
**Bob** (2 cards): Sowing, Ingenuity
  Discard: Mine, Nomad
**Charlie** (3 cards): Worship of Fertility, Ingenuity, Scavenge
  Discard: Rumour, Harvest

Season: Forage, Crags, Gathering
Fields (7): Famine, Plough, Granary, Militia, Famine, Plough, Mill
Piles: Claw 38, Tree 32, Wheat 10, Coin 3

---

**T11 — Bob:** Activates Wheat zone via Sowing (has 0 [Nature] but wait — Sowing requires 2+ [Nature], which Bob doesn't have). *Bob cannot activate Wheat zone.* Instead, Bob takes **Crags** from Season to build toward Nature requirement and eventually Highlander. *Need [Nature] cards to unlock Sowing's Wheat access.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Crags|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Crags → Bob's Domain

</details>

**T12 — Charlie:** Activates **Sacred Grove** — wait, Charlie doesn't have Sacred Grove. Charlie activates **Worship of Fertility** — but this only has "On Rite" text, not "Activate". Charlie takes **Gathering** from Season. *Need a Rite trigger to activate my Worship of Fertility — Gathering can trigger Rite in my Domain and spread to cultural allies.* Gathering is Drafted — Charlie chooses to trigger Rite in their Domain. Charlie's Worship of Fertility responds: On Rite triggers Harvest in Charlie's Domain. Fields refill from 7 to 7 (already full, no change). Gathering moves to discard.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON_DISCARD|Gathering|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON_DISCARD Gathering → Charlie's discard

</details>

## Round 5 (Turns 13–15)

**T13 — Alice:** Activates **Sacred Grove**, choosing to trigger Rite in her Domain. *With Pathfinding already in hand, stacking Knowledge cards is the path to victory — need to find more Spiritual cards to build a Rite engine.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Alice's Domain (the Rite triggerer). Harvest fires — Fields refill from 7 to 7 (already full, no change). No On Harvest responders in Alice's Domain.

OPS:

**T14 — Bob:** Activates the Wheat zone via Sowing (has Crags [Nature] + Ingenuity [Craftsmanship] — wait, Ingenuity has [Craftsmanship] not [Nature]). *Bob only has 1 [Nature] card (Crags), so Sowing's requirement of 2+ [Nature] is NOT met.* Bob instead takes **Forage** from Season. *Building Tree infrastructure to dig for more Nature cards and enable Wheat access later.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Forage|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Forage → Bob's Domain
- 🔄 Season auto-refilled: [Pasture, Pathfinding, Regrowth, Highlander]

</details>

**T15 — Charlie:** Activates **Sacred Grove** from... wait, Charlie doesn't have Sacred Grove. Charlie activates **Worship of Fertility** — but that's "On Rite" only, not activatable. Charlie takes **Pasture** from Season instead. *Need [Nature] for Wheat access and to enable future Nomad — also racing Tree pile depletes where [Nature] wins.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Pasture|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Pasture → Charlie's Domain

</details>

## Round 6 (Turns 16–18)

**T16 — Alice:** Activates **Sacred Grove**, choosing to trigger Rite in her Domain. *With Pathfinding already generating value, building a Spiritual engine alongside it creates a powerful dual-threat.* Rite fires globally. Charlie's Worship of Fertility responds: On Rite triggers Harvest in Alice's Domain. Harvest fires — Fields refill from 7 to 7 (already full, no change). No On Harvest responders in any Domain, so Harvest does nothing further.

OPS:

**T17 — Bob:** Activates **Forage** — puts top 3 Tree cards (Solstice, Pasture, Pasture) into discard, then discards Forage to take **Pasture** to Domain. *With Crags already in place, adding Pasture gives 2 [Nature] for Sowing AND opens up Nomad recovery from discard later — strong foundation play.*

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|tree|3|Bob
MOVE|Bob|Forage|DISCARD
MOVE_DISCARD|Bob|Pasture
```

</details>

<details><summary>📋 Ops Trace (5 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD tree → Solstice → Bob's discard
- ✅ DRAW_DISCARD tree → Pasture → Bob's discard
- ✅ DRAW_DISCARD tree → Pasture → Bob's discard
- ✅ MOVE Forage Bob's Domain → Bob's discard
- ✅ MOVE_DISCARD Pasture Bob's discard → Bob's Domain

</details>

**T18 — Charlie:** Activates **Sacred Grove** — wait, Charlie doesn't have Sacred Grove. Charlie activates **Worship of Fertility** — no, that's an "On Rite" card, not activatable. Charlie takes **Regrowth** from Season. *Recovers all discarded Pastures globally — Bob has one in discard, this strengthens Nature boards.* Regrowth is Drafted: Bob's Pasture returns from discard to Bob's Domain. Regrowth moves to Charlie's discard.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON_DISCARD|Regrowth|Charlie
MOVE_DISCARD|Bob|Pasture
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ TAKE_SEASON_DISCARD Regrowth → Charlie's discard
- ✅ MOVE_DISCARD Pasture Bob's discard → Bob's Domain

</details>

## Round 7 (Turns 19–21)

**T19 — Alice:** Activates **Sacred Grove**, choosing to trigger Rite in her Domain. *With Worship of Fertility in play on Charlie, this chains into Harvest for free value.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Alice's Domain (the Rite triggerer). Harvest fires — Fields refill from 7 to 7 (already full, no change). No other On Harvest cards respond.

OPS:

**T20 — Bob:** Activates the Wheat zone via Sowing (has 3 [Nature]: Crags, Pasture, Pasture). Takes **Plough** and **Granary** from Fields, drawing 2 from Claw as tax: **Worship of War** and **Share the Spoils**. *Building Wheat infrastructure while stockpiling Claw cards — Worship of War gives future Brawl capability, and the Wheat cards enable Feast chains.* Plough is Drafted — requires discarding a Pasture or discarding itself. Bob discards a Pasture to keep Plough.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_FIELDS|Plough|Bob
TAKE_FIELDS|Granary|Bob
DRAW|claw|2|Bob
MOVE|Bob|Pasture|DISCARD
```

</details>

<details><summary>📋 Ops Trace (5 applied, 0 violations)</summary>

- ✅ TAKE_FIELDS Plough → Bob's Domain
- ✅ TAKE_FIELDS Granary → Bob's Domain
- ✅ DRAW claw → Worship of War → Bob's Domain
- ✅ DRAW claw → Share the Spoils → Bob's Domain
- ✅ MOVE Pasture Bob's Domain → Bob's discard

</details>

---

### === STATE AFTER TURN 20 ===

**Alice** (3 cards): Pathfinding, Raid, Sacred Grove
**Bob** (8 cards): Sowing, Ingenuity, Crags, Pasture, Plough, Granary, Worship of War, Share the Spoils
  Discard: Mine, Nomad, Solstice, Forage, Pasture
**Charlie** (4 cards): Worship of Fertility, Ingenuity, Scavenge, Pasture
  Discard: Rumour, Harvest, Gathering, Regrowth

Season: Pathfinding, Highlander
Fields (5): Famine, Militia, Famine, Plough, Mill
Piles: Claw 36, Tree 25, Wheat 10, Coin 3

---

**T21 — Charlie:** Activates **Sacred Grove** in Alice's Domain? No — Charlie can only activate cards in their own Domain. Charlie activates the **Tree zone**, taking **Pathfinding** from Season. *With only 1 [Knowledge] card (Ingenuity), Pathfinding is weak now but scales if Charlie can stack more Knowledge. Tree depletion favors [Nature] and Charlie has Pasture + Worship of Fertility.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Pathfinding|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Pathfinding → Charlie's Domain

</details>

## Round 8 (Turns 22–24)

**T22 — Alice:** Activates **Sacred Grove**, choosing to trigger Rite in her Domain. *With Worship of Fertility and Worship of War on the board, a Rite chain can devastate Bob while building momentum.* Rite fires globally. Bob's Worship of War responds: Alice (triggering player) may trigger Brawl in any Domain — she targets Bob's Domain. Brawl in Bob's Domain fires. Bob has no Mob cards, so no cards are transferred. Charlie's Worship of Fertility responds to the original Rite: triggers Harvest in Charlie's Domain. Harvest fires — Fields refill from 5 to 7. Bob's Plough responds: On Harvest, Bob chooses to trigger Feast in his Domain. Feast fires. Bob's Share the Spoils responds: Bob may draw 1 from Claw — he draws Chiefdom.

<details><summary>🎯 Raw OPS</summary>

```
REFILL_FIELDS|2
DRAW|claw|1|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ REFILL_FIELDS +2: [Plough, Mill]
- ✅ DRAW claw → Chiefdom → Bob's Domain

</details>

**T23 — Bob:** Activates **Worship of War** via **Sacred Grove**'s Rite trigger. *With Chiefdom already in place to plant Mob and Worship of War ready, Bob builds his Brawl engine by triggering Rite.* Sacred Grove triggers Rite in Bob's Domain. Worship of War responds: Bob may trigger Brawl in any Domain — he targets Alice (3 cards, includes Raid). Charlie's Worship of Fertility responds to the Rite: triggers Harvest in Charlie's Domain. Fields refill from 7 to 7 (already full). Brawl resolves in Alice's Domain: Alice's Raid responds — Alice gives 1 card to Bob. Bob takes Pathfinding (the most valuable card). Alice now has only Raid and Sacred Grove.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Alice|Pathfinding|DOMAIN|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Pathfinding Alice's Domain → Bob's Domain

</details>

**T24 — Charlie:** Activates **Pathfinding** to draw 2 cards from Tree (has 2 [Knowledge]: Worship of Fertility, Pathfinding). *Building toward Tree depletion where I'm competitive on [Nature] tags.* Draws Forage and Nomad. Nomad is Drafted — Charlie has Pasture, so Nomad stays. But Charlie already has no [Culture], so Nomad enters Domain. Now Charlie has 3 [Nature] (Worship of Fertility, Pasture, Nomad) making them a serious threat if Tree depletes.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|2|Charlie
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW tree → Forage → Charlie's Domain
- ✅ DRAW tree → Nomad → Charlie's Domain

</details>

## Round 9 (Turns 25–27)

**T25 — Alice:** Activates **Sacred Grove**, choosing to trigger Rite in her Domain. *With Worship of Fertility in Charlie's Domain responding, this chains into Harvest for free card draw setup.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Alice's Domain (the Rite triggerer). Harvest fires — Fields refill from 7 to 7 (already full, no change). Bob's Plough responds to Harvest: Bob chooses to trigger Feast in his Domain. Bob's Share the Spoils responds to Feast: Bob draws 1 from Claw (Chiefdom). Chiefdom is not Drafted, enters Bob's Domain. Bob now has 2 [Allegiance] cards (Chiefdom ×2) — must discard one; discards the new Chiefdom.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|1|Bob
MOVE|Bob|Chiefdom|DISCARD
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW claw → Chiefdom → Bob's Domain
- ✅ MOVE Chiefdom Bob's Domain → Bob's discard

</details>

**T26 — Bob:** Activates **Pathfinding** to draw 2 cards from Tree (has 2 [Knowledge]: Sowing, Pathfinding). *With dominant position in [Nature] (Crags + Pasture + 2 Worship cards responding to Rite), accelerating Tree depletion to trigger the win condition.* Draws Harvest (Drafted — triggers Harvest globally, moves to discard). Fields refill from 7 to 7 (already full). Bob's Plough responds: On Harvest, Bob chooses to trigger Feast. Bob's Share the Spoils responds: draws 1 from Claw (Tyranny). Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain — Fields still full, no refill. Then draws Regrowth (Drafted — all Pasture cards in discards return to owners' Domains; Bob's Pasture returns, moves to discard).

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|tree|1|Bob
DRAW|claw|1|Bob
DRAW_DISCARD|tree|1|Bob
MOVE_DISCARD|Bob|Pasture
```

</details>

<details><summary>📋 Ops Trace (4 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD tree → Harvest → Bob's discard
- ✅ DRAW claw → Tyranny → Bob's Domain
- ✅ DRAW_DISCARD tree → Regrowth → Bob's discard
- ✅ MOVE_DISCARD Pasture Bob's discard → Bob's Domain

</details>

**T27 — Charlie:** Activates **Pathfinding** to draw 2 cards from Tree (has 2 [Knowledge]: Pathfinding, Ingenuity). *Bob's massive Domain with Tyranny and 12 cards is the threat — need to build up fast and potentially race Tree depletion since I'm tied for [Nature] lead.* Draws Crags and Sky Dance. Both stay in Domain.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|2|Charlie
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW tree → Crags → Charlie's Domain
- ✅ DRAW tree → Sky Dance → Charlie's Domain

</details>

## Round 10 (Turns 28–30)

**T28 — Alice:** Activates **Sacred Grove** choosing Rite. *With Worship of Fertility responding, this chains into Harvest for Fields refill.* Rite triggers globally. Charlie's Worship of Fertility responds: triggers Harvest in Alice's Domain. No On Harvest responders in Alice's Domain, but Fields refill from 7 to 7 (already full, so 0 new cards). Bob's Worship of War responds: Alice may trigger Brawl in any Domain — targets Bob's massive Domain. Brawl in Bob's Domain: Bob's Share the Spoils responds (On Feast, not On Brawl — no effect). No Mob cards in Bob's Domain to give cards to Alice. Brawl resolves with no transfers.

OPS:

**T29 — Bob:** Activates **Tyranny** to draw 4 cards from Claw (matching his 4 [Discontent] cards: Ingenuity, Plough, Tyranny, Chiefdom). *With 2 Trophies already and a massive Domain, accelerating Claw depletion while gaining more [Trophy] cards is the winning move.* Draws Armament, Poach, Outriders, and the next card (Worship of the Hunt). Armament and Poach carry [Discontent], further fueling future Tyranny activations.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|4|Bob
```

</details>

<details><summary>📋 Ops Trace (4 applied, 0 violations)</summary>

- ✅ DRAW claw → Armament → Bob's Domain
- ✅ DRAW claw → Poach → Bob's Domain
- ✅ DRAW claw → Outriders → Bob's Domain
- ✅ DRAW claw → Incite → Bob's Domain

</details>

**T30 — Charlie:** Activates **Sky Dance** to trigger Rite. *With Worship of Fertility responding, this chains into Harvest → Fields refill, building toward [Nature] victory.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Fields refill from 7 to 7 (already full, no change). No other On Harvest responders.

OPS:

---

### === STATE AFTER TURN 30 ===

**Alice** (2 cards): Raid, Sacred Grove
**Bob** (16 cards): Sowing, Ingenuity, Crags, Pasture, Plough, Granary, Worship of War, Share the Spoils, Pathfinding, Chiefdom, Tyranny, Pasture, Armament, Poach, Outriders, Incite
  Discard: Mine, Nomad, Solstice, Forage, Chiefdom, Harvest, Regrowth
**Charlie** (9 cards): Worship of Fertility, Ingenuity, Scavenge, Pasture, Pathfinding, Forage, Nomad, Crags, Sky Dance
  Discard: Rumour, Harvest, Gathering, Regrowth

Season: Highlander
Fields (7): Famine, Militia, Famine, Plough, Mill, Plough, Mill
Piles: Claw 29, Tree 19, Wheat 8, Coin 3

---

## Round 11 (Turns 31–33)

**T31 — Alice:** Activates **Sacred Grove**, choosing to trigger Rite in her Domain. *With Worship of Fertility in Charlie's Domain, this will trigger Harvest and refill Fields while I fish for better cards.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Alice's Domain. Harvest fires — Fields refill from 7 to 7 (already full, no change). Bob's Plough responds to Harvest: Bob chooses to trigger Feast in his Domain. Bob's Share the Spoils responds to Feast: Bob draws 1 from Claw (Scavenge). Bob's Poach responds to Feast: triggers Feast in Bob's Domain (hunt limit = 2 from his Pastures, 1 used). Poach discards, Bob draws 1 from Claw (Raid). Second Feast from Poach — Share the Spoils responds again: Bob draws 1 from Claw (Warband).

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Bob|Poach|DISCARD
DRAW|claw|3|Bob
```

</details>

<details><summary>📋 Ops Trace (4 applied, 0 violations)</summary>

- ✅ MOVE Poach Bob's Domain → Bob's discard
- ✅ DRAW claw → Scavenge → Bob's Domain
- ✅ DRAW claw → Raid → Bob's Domain
- ✅ DRAW claw → Warband → Bob's Domain

</details>

**T32 — Bob:** Activates **Chiefdom** to move **Scavenge** from his Domain to Alice's Domain. *Stacking Alice with Mob cards before unleashing Brawl — she already has Raid, adding Scavenge makes her Domain a juicy target for next turn's Warband.* No events triggered.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Bob|Scavenge|DOMAIN|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Scavenge Bob's Domain → Alice's Domain

</details>

**T33 — Charlie:** Activates **Sky Dance** to trigger Rite. *Bob's massive Domain with Worship of War is the existential threat — need to build Spiritual engine before he destroys everyone.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Fields refill from 7 to 7 (already full, no change). No On Harvest responders in Charlie's Domain, so Harvest does nothing further. Bob's Worship of War responds: Bob may trigger Brawl in any Domain — Bob targets Alice (smallest Domain, has 2 Mob cards). Brawl in Alice's Domain: Alice's Raid responds (gives 1 card to Bob), Alice's Scavenge responds (gives 1 card from discard to Bob — but Alice's discard is empty, so no effect).

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Alice|Raid|DOMAIN|Bob
MOVE|Alice|Scavenge|DOMAIN|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ MOVE Raid Alice's Domain → Bob's Domain
- ✅ MOVE Scavenge Alice's Domain → Bob's Domain

</details>

## Round 12 (Turns 34–36)

**T34 — Alice:** Activates **Sacred Grove**, choosing to trigger Rite in her Domain. *Desperate play — need to find Spiritual cards to have any chance, and Rite might chain into something useful.* Rite fires. Charlie's Worship of Fertility responds: triggers Harvest in Alice's Domain. Harvest fires — Fields refill from 7 to 7 (already full, no change). Charlie's Sky Dance could trigger another Rite but Alice has no On Harvest cards and no further benefit. Bob's Worship of War responds to the original Rite: Bob may trigger Brawl in any Domain — Bob targets Alice. Brawl fires in Alice's Domain. No [Mob] cards in Alice's Domain, so no On Brawl effects trigger. The Brawl does nothing to Alice.

OPS:

**T35 — Bob:** Activates **Warband** from Domain, triggering Brawl in Charlie's Domain (the largest with 9 cards). *Charlie has the most [Nature] and [Trophy] — destroying his position before Tree depletes is critical.* Charlie's Scavenge responds: gives Bob 1 card from Charlie's discard. Bob chooses Gathering (most versatile). Charlie has no Eldership or Militia to cancel.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Scavenge|DISCARD
MOVE_DISCARD|Charlie|Gathering
MOVE|Charlie|Gathering|DOMAIN|Bob
```

</details>

<details><summary>📋 Ops Trace (3 applied, 0 violations)</summary>

- ✅ MOVE Scavenge Charlie's Domain → Charlie's discard
- ✅ MOVE_DISCARD Gathering Charlie's discard → Charlie's Domain
- ✅ MOVE Gathering Charlie's Domain → Bob's Domain

</details>

**T36 — Charlie:** Activates **Sky Dance** to trigger Rite. *With Worship of Fertility responding, this chains into Harvest and refills Fields while building toward Nature victory.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Fields refill from 7 to 7 (already full, no change). No other Rite responders. Bob's Plough responds to Harvest: Bob chooses Feast in his Domain. Bob's Share the Spoils responds: Bob draws Marauders from Claw.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|1|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW claw → Marauders → Bob's Domain

</details>

## Round 13 (Turns 37–39)

**T37 — Alice:** Activates **Sacred Grove**, choosing to trigger Rite in her Domain. *Desperate play — only card left, fishing for any advantage against Bob's massive lead.* Rite fires globally. Bob's Worship of War responds: Bob may trigger Brawl in any Domain — he targets Alice. Brawl in Alice's Domain with no Mob cards means nothing happens. Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Fields refill from 7 to 7 (already full, no change). Charlie's Domain has no On Harvest cards.

OPS:

**T38 — Bob:** Activates **Warband** to trigger Brawl in Charlie's Domain (largest aside from his own at 8 cards). *Charlie's Pathfinding is the only threat left — strip it now.* Brawl fires in Charlie's Domain. Bob's Raid cards in his OWN Domain don't respond (they only respond when Brawl is in THEIR Domain). Charlie has no [Mob] cards and no Brawl defense. The Brawl resolves with no responders — no state change occurs. Bob wasted his turn.

OPS:

**T39 — Charlie:** Activates **Sky Dance** to trigger Rite. *Building toward [Nature] victory with Worship of Fertility compounding Harvest triggers.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Fields refill from 7 to 7 (already full, no change). No other On Harvest responders in Charlie's Domain. Bob's Plough responds to Harvest: Bob chooses to trigger Feast in his Domain. Bob's Share the Spoils responds: Bob draws 1 from Claw (Raid).

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|1|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW claw → Raid → Bob's Domain

</details>

## Round 14 (Turns 40–40)

**T40 — Alice:** Activates **Sacred Grove**, choosing to trigger Rite in her Domain. *Desperate play — need to find Spiritual cards or leverage Charlie's Worship responders somehow.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Alice's Domain — but Alice has no On Harvest cards, so nothing happens. Fields refill from 7 to 7 (already full, no change). No other Rite responders exist. Alice gains nothing tangible but the Harvest event fired.

OPS:

---

### === STATE AFTER TURN 40 ===

**Alice** (1 cards): Sacred Grove
**Bob** (22 cards): Sowing, Ingenuity, Crags, Pasture, Plough, Granary, Worship of War, Share the Spoils, Pathfinding, Chiefdom, Tyranny, Pasture, Armament, Outriders, Incite, Raid, Warband, Raid, Scavenge, Gathering, Marauders, Raid
  Discard: Mine, Nomad, Solstice, Forage, Chiefdom, Harvest, Regrowth, Poach
**Charlie** (8 cards): Worship of Fertility, Ingenuity, Pasture, Pathfinding, Forage, Nomad, Crags, Sky Dance
  Discard: Rumour, Harvest, Regrowth, Scavenge

Season: Highlander
Fields (7): Famine, Militia, Famine, Plough, Mill, Plough, Mill
Piles: Claw 24, Tree 19, Wheat 8, Coin 3

---

---

## Epilogue

**Alice** — 1 cards
  Domain: Sacred Grove
  Tags: [Nature]×1, [Spiritual]×1

**Bob** — 22 cards
  Domain: Sowing, Ingenuity, Crags, Pasture, Plough, Granary, Worship of War, Share the Spoils, Pathfinding, Chiefdom, Tyranny, Pasture, Armament, Outriders, Incite, Raid, Warband, Raid, Scavenge, Gathering, Marauders, Raid
  Tags: [Allegiance]×1, [Craftsmanship]×1, [Discontent]×8, [Knowledge]×3, [Labour]×2, [Land]×3, [Nature]×3, [Rabble]×5, [Spiritual]×1, [Trophy]×1, [Unit]×5

**Charlie** — 8 cards
  Domain: Worship of Fertility, Ingenuity, Pasture, Pathfinding, Forage, Nomad, Crags, Sky Dance
  Tags: [Craftsmanship]×1, [Culture]×1, [Discontent]×1, [Knowledge]×1, [Land]×2, [Nature]×3, [Spiritual]×2

### Stats
API calls: 41 | Piles: Claw 24, Tree 19, Wheat 8, Coin 3, Candle 1
