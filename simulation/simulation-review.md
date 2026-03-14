# Simulation — AI-Driven (v2)

**Players:** Alice, Bob, Charlie (3 players, 15 rounds = 45 turns)

---

## Initial State

Season: Harvest, Crags, Sowing, Crags
Fields (7): Granary, Mill, Tavern, Tavern, Militia, Plough, Famine
Piles: Claw 43, Tree 37, Wheat 10, Coin 5, Candle 1

---

## Round 1 (Turns 1–3)

**T1 — Alice:** Takes **Crags** from Season. *First-turn Land grab enables Highlander culture path and provides Brawl defense later.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Crags|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Crags → Alice's Domain

</details>

**T2 — Bob:** Takes **Crags** from Season. *Matching Alice's land grab — Crags enables Highlander culture and provides Brawl defense later.* No events triggered.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Crags|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Crags → Bob's Domain

</details>

**T3 — Charlie:** Takes **Sowing** from Season. *Sowing provides [Knowledge] tag and unlocks Wheat access once I get 2 [Nature] cards — need to build foundation.* Sowing enters Charlie's Domain.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Sowing|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Sowing → Charlie's Domain

</details>

## Round 2 (Turns 4–6)

**T4 — Alice:** Takes **Harvest** from Season. *Triggering Harvest refills Fields and thins the Tree deck toward [Nature] victory.* Harvest is Drafted — triggers Harvest globally, then discards itself. Fields refill from 7 to 7 (already full, no refill needed). No On Harvest responders in any Domain.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON_DISCARD|Harvest|Alice
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ TAKE_SEASON_DISCARD Harvest → Alice's discard
- 🔄 Season auto-refilled: [Solstice, Pasture, Pathfinding, Nomad]

</details>

**T5 — Bob:** Takes **Pasture** from Season. *Securing [Nature] land to enable Nomad culture and future Wheat access.* Pasture enters Bob's Domain alongside Crags, giving him 2 [Nature] cards.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Pasture|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Pasture → Bob's Domain

</details>

**T6 — Charlie:** Activates the Wheat zone via Sowing (has 0 [Nature] but Sowing is in Domain — wait, Sowing requires 2+ [Nature]). *Charlie cannot activate Wheat — Sowing requires 2+ [Nature] cards and Charlie has none.* Instead, takes **Pathfinding** from Season. *Building [Knowledge] for future card draw engine — Pathfinding scales with Knowledge count.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Pathfinding|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Pathfinding → Charlie's Domain

</details>

## Round 3 (Turns 7–9)

**T7 — Alice:** Draws from Claw, getting **Armament** and **Raid**. *With only one Crags, Alice needs to build toward [Trophy] tags to compete — Claw draws add Discontent and potential Trophy cards while Bob and Charlie race Tree/Nature.* Armament is [Knowledge], Raid is [Unit][Mob][Discontent]. Both stay in Domain.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|2|Alice
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW claw → Armament → Alice's Domain
- ✅ DRAW claw → Raid → Alice's Domain

</details>

**T8 — Bob:** Takes **Nomad** from Season. *Already has Pasture, so Nomad's Drafted requirement is met — secures [Culture] slot and builds toward [Nature] count for potential Tree victory.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Nomad|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Nomad → Bob's Domain

</details>

**T9 — Charlie:** Activates **Pathfinding** to draw 1 card from Tree (has 1 [Knowledge] card: Pathfinding itself). *Building Knowledge engine — each Knowledge card makes future Pathfinding draws stronger.* Draws **Solstice** to Domain.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|1|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW tree → Solstice → Charlie's Domain

</details>

## Round 4 (Turns 10–12)

**T10 — Alice:** Activates **Crags** to scout Claw pile. *Checking for threats before committing to Claw draws — Ingenuity on top is safe and gives free Coin access.* Alice looks at top 3 (Ingenuity, Marauders, Worship of the Hunt) and puts Marauders into her discard to remove the [Mob] threat from circulation while stashing it for potential Herbalism retrieval later.

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|claw|1|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD claw → Ingenuity → Alice's discard

</details>

---

### === STATE AFTER TURN 10 ===

**Alice** (3 cards): Crags, Armament, Raid
  Discard: Harvest, Ingenuity
**Bob** (3 cards): Crags, Pasture, Nomad
**Charlie** (3 cards): Sowing, Pathfinding, Solstice

Season: Solstice
Fields (7): Granary, Mill, Tavern, Tavern, Militia, Plough, Famine
Piles: Claw 40, Tree 32, Wheat 10, Coin 5

---

**T11 — Bob:** Takes **Solstice** from Season. *Solstice triggers on Harvest and synergizes with Nomad culture — building toward a [Nature] victory while Tree pile thins.* Season now empty, auto-refills with 4 new cards from Tree pile.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Solstice|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Solstice → Bob's Domain
- 🔄 Season auto-refilled: [Gathering, Nomad, Harvest, Crags]

</details>

**T12 — Charlie:** Activates **Pathfinding** to draw 2 cards from Tree (has 2 [Knowledge]: Sowing, Pathfinding). *Building Knowledge engine while Tree pile is healthy — Pathfinding snowballs harder with more Knowledge cards.* Draws Oral Tradition and Forage. Oral Tradition has no Drafted text, stays in Domain. Forage has no Drafted text, stays in Domain. Charlie now has 3 [Knowledge] cards for next Pathfinding activation.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|2|Charlie
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW tree → Oral Tradition → Charlie's Domain
- ✅ DRAW tree → Forage → Charlie's Domain

</details>

## Round 5 (Turns 13–15)

**T13 — Alice:** Takes **Crags** from Season. *Second Crags gives Brawl defense and enables scouting the Claw pile — critical when holding Raid in own Domain.* Alice now has 2 Crags, which means any Brawl against her requires the attacker to discard a card to proceed.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Crags|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Crags → Alice's Domain

</details>

**T14 — Bob:** Takes **Harvest** from Season. *Triggering Harvest refills Fields and fires Solstice in my Domain — I can spread Nomad culture or draw Tree cards with allies.* Harvest is Drafted — triggers Harvest globally. Fields refill from 7 to 7 (already full, no change). Bob's Solstice responds: On Harvest, Bob chooses to have all players of his culture (Nomad) draw 1 from Tree. Only Bob has Nomad culture, so Bob draws Pasture from Tree.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON_DISCARD|Harvest|Bob
DRAW|tree|1|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ TAKE_SEASON_DISCARD Harvest → Bob's discard
- ✅ DRAW tree → Pasture → Bob's Domain

</details>

**T15 — Charlie:** Activates **Pathfinding** to draw 2 cards from Tree (has 2 [Knowledge]: Pathfinding, Oral Tradition). *Building Tree engine while accumulating [Nature] tags for endgame.* Draws Withered Crop and Sowing. Withered Crop has no Drafted effect and stays. Sowing has no Drafted effect and stays — but Charlie already has Sowing, so now has redundant access to Wheat.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|2|Charlie
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW tree → Withered Crop → Charlie's Domain
- ✅ DRAW tree → Sowing → Charlie's Domain

</details>

## Round 6 (Turns 16–18)

**T16 — Alice:** Activates **Crags** to scout Claw pile. *With 2 Crags already providing Brawl defense, using one to scout is low-cost — checking for threats like Uprising or finding useful cards to stash.* Alice looks at top 3 Claw cards (Marauders, Worship of the Hunt, Warband) and puts Marauders into her discard — a [Mob] card she doesn't want drawn against her, and potentially retrievable later if she gets Herbalism.

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|claw|1|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD claw → Marauders → Alice's discard

</details>

**T17 — Bob:** Activates **Wheat zone** (via Sowing access with 2 Pastures). Takes **Militia** and **Tavern** from Fields, draws 2 Claw as tax. *Building defensive infrastructure against Alice's growing Mob threat while establishing Amenity presence for potential Wheat depletion race.* Draws Worship of the Hunt and Warband from Claw — neither is Drafted, both enter Domain.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_FIELDS|Militia|Bob
TAKE_FIELDS|Tavern|Bob
DRAW|claw|2|Bob
```

</details>

<details><summary>📋 Ops Trace (4 applied, 0 violations)</summary>

- ✅ TAKE_FIELDS Militia → Bob's Domain
- ✅ TAKE_FIELDS Tavern → Bob's Domain
- ✅ DRAW claw → Worship of the Hunt → Bob's Domain
- ✅ DRAW claw → Warband → Bob's Domain

</details>

**T18 — Charlie:** Activates **Pathfinding** to draw 2 cards from Tree (has 2 [Knowledge]: Pathfinding, Oral Tradition). *Building Knowledge engine to accelerate Tree depletion where I'm strong on [Nature] via Sowing access.* Draws Crags and Sky Dance. Crags is a Land with no Drafted effect — enters Domain. Sky Dance has no Drafted effect — enters Domain. Charlie now has 3 [Knowledge] for next Pathfinding activation.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|2|Charlie
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW tree → Crags → Charlie's Domain
- ✅ DRAW tree → Sky Dance → Charlie's Domain

</details>

## Round 7 (Turns 19–21)

**T19 — Alice:** Activates **Crags** to scout the Claw pile. *With 2 Crags in Domain, Alice has solid Brawl defense — time to check what's coming before committing to combat.* Alice looks at top 3 Claw cards (Raid, Raid, Chiefdom) and puts Raid into her discard to remove a dangerous Mob card from circulation.

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|claw|1|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD claw → Raid → Alice's discard

</details>

**T20 — Bob:** Activates **Warband** to trigger Brawl in Charlie's Domain (largest with 9 cards). *Charlie is snowballing with Pathfinding and needs to be stopped before he runs away with Tree.* Charlie has no Brawl defenses — no Militia, no Eldership, no double Crags. No [Mob] cards in Charlie's Domain to respond. Brawl baseline fires: Charlie must discard 1 card of his choice. Charlie discards Sowing (keeping Withered Crop for Wheat access, protecting Pathfinding and Sky Dance).

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Sowing|DISCARD
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Sowing Charlie's Domain → Charlie's discard

</details>

---

### === STATE AFTER TURN 20 ===

**Alice** (4 cards): Crags, Armament, Raid, Crags
  Discard: Harvest, Ingenuity, Marauders, Raid
**Bob** (9 cards): Crags, Pasture, Nomad, Solstice, Pasture, Militia, Tavern, Worship of the Hunt, Warband
  Discard: Harvest
**Charlie** (8 cards): Pathfinding, Solstice, Oral Tradition, Forage, Withered Crop, Sowing, Crags, Sky Dance
  Discard: Sowing

Season: Gathering, Nomad
Fields (5): Granary, Mill, Tavern, Plough, Famine
Piles: Claw 36, Tree 21, Wheat 10, Coin 5

---

**T21 — Charlie:** Activates **Pathfinding**. *With 3 [Knowledge] cards (Pathfinding, Oral Tradition, Sowing), this draws 3 from Tree — far better than a single Season pick.* Charlie draws Herbalism, Worship of Fertility, and Forage. Herbalism and Forage have Activate abilities (kept). Worship of Fertility is [Spiritual] with On Rite (kept). No Drafted effects on any of these cards.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|3|Charlie
```

</details>

<details><summary>📋 Ops Trace (3 applied, 0 violations)</summary>

- ✅ DRAW tree → Herbalism → Charlie's Domain
- ✅ DRAW tree → Worship of Fertility → Charlie's Domain
- ✅ DRAW tree → Forage → Charlie's Domain

</details>

## Round 8 (Turns 22–24)

**T22 — Alice:** Activates **Crags** to scout the Claw pile. *With 2 Crags providing Brawl defense and no Wheat access, scouting Claw to remove threats or stash useful cards is the best play.* Alice looks at the top 3 Claw cards (Raid, Chiefdom, Scavenge) and puts Chiefdom into her discard — a strong [Allegiance] card she can't use but could retrieve later with Herbalism if she ever gets access.

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|claw|1|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD claw → Raid → Alice's discard

</details>

**T23 — Bob:** Activates **Warband** to trigger Brawl in Charlie's Domain (11 cards, largest on board). *Charlie's Pathfinding engine is running away with the game — must strip cards before he depletes Tree.* Brawl fires in Charlie's Domain. No [Mob] cards present, no On Brawl responders — Brawl baseline applies: Charlie discards 1 card of choice. Charlie discards Forage (least essential duplicate).

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Forage|DISCARD
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Forage Charlie's Domain → Charlie's discard

</details>

**T24 — Charlie:** Activates **Sky Dance** to trigger Rite. *With Worship of Fertility responding, this chains into Harvest for Fields refill and potential Feast cascade.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Fields refill from 5 to 7 (draws Apprenticeship, Plough from Wheat pile). No On Harvest cards in Charlie's Domain, so Harvest resolves with just the refill. Bob's Worship of the Hunt also responds to the Rite — Charlie (the Rite triggerer) may activate all [Hunt] cards in their Domain, but Charlie has no [Hunt] cards, so this does nothing.

<details><summary>🎯 Raw OPS</summary>

```
REFILL_FIELDS|2
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ REFILL_FIELDS +2: [Apprenticeship, Plough]

</details>

## Round 9 (Turns 25–27)

**T25 — Alice:** Draws from Claw, getting **Chiefdom**. *With 2 Crags giving Brawl defense and multiple Raids in discard, taking an [Allegiance][Trophy] card that can plant Mob fits a Claw-depletion strategy.* Chiefdom enters Alice's Domain — she now has a repeatable way to move Mob cards. Her 2 Crags mean opponents must discard to Brawl her successfully.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|1|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW claw → Chiefdom → Alice's Domain

</details>

**T26 — Bob:** Activates **Warband** to trigger Brawl in Charlie's Domain (largest with 10 cards). *Charlie's runaway Pathfinding engine is the biggest threat — must strip cards before he dominates Tree.* Brawl fires in Charlie's Domain. No [Mob] cards present, so baseline Brawl applies: Charlie discards 1 card of choice. Charlie discards Withered Crop (least useful — already has Sowing for Wheat access).

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Withered Crop|DISCARD
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Withered Crop Charlie's Domain → Charlie's discard

</details>

**T27 — Charlie:** Activates **Sky Dance** to trigger Rite. *With Worship of Fertility responding, this chains into Harvest for Fields refill and potential On Harvest value.* Rite fires in Charlie's Domain. Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Fields refill from 7 to 7 (already full, no refill needed). Bob's Solstice and Charlie's Solstice both have On Harvest — Bob chooses to have all players of his culture (Nomad) draw 1 from Tree; only Bob has Nomad culture, so Bob draws Nomad. Charlie's Solstice: Charlie chooses all players of his culture to draw from Tree, but Charlie has no [Culture] card — effect fizzles.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|1|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW tree → Nomad → Bob's Domain

</details>

## Round 10 (Turns 28–30)

**T28 — Alice:** Activates **Chiefdom** to move Raid from her Domain to Charlie's Domain. *Charlie has no Brawl defense and holds the most valuable engine — planting Mob now sets up a devastating Warband strike next turn.* Alice chooses her own Raid and transfers it to Charlie's Domain.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Alice|Raid|DOMAIN|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Raid Alice's Domain → Charlie's Domain

</details>

**T29 — Bob:** Activates **Warband** to trigger Brawl in Charlie's Domain (largest at 10 cards). *Charlie's Pathfinding engine is the biggest threat — stripping cards now before he runs away with Tree.* Charlie has Raid [Mob] in Domain — it fights for Bob, giving Bob one of Charlie's cards. Charlie chooses to give up Forage (least valuable). No other On Brawl effects fire.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Forage|DOMAIN|Bob
MOVE|Charlie|Raid|DISCARD
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ MOVE Forage Charlie's Domain → Bob's Domain
- ✅ MOVE Raid Charlie's Domain → Charlie's discard

</details>

**T30 — Charlie:** Activates **Sky Dance** to trigger Rite. *With Worship of Fertility responding, this chains into Harvest for Fields refill and potential Feast triggers.* Rite fires in Charlie's Domain. Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Fields refill from 7 to 7 (already full, no refill needed). No On Harvest cards in any Domain respond.

OPS:

---

### === STATE AFTER TURN 30 ===

**Alice** (4 cards): Crags, Armament, Crags, Chiefdom
  Discard: Harvest, Ingenuity, Marauders, Raid, Raid
**Bob** (11 cards): Crags, Pasture, Nomad, Solstice, Pasture, Militia, Tavern, Worship of the Hunt, Warband, Nomad, Forage
  Discard: Harvest
**Charlie** (8 cards): Pathfinding, Solstice, Oral Tradition, Sowing, Crags, Sky Dance, Herbalism, Worship of Fertility
  Discard: Sowing, Forage, Withered Crop, Raid

Season: Gathering, Nomad
Fields (7): Granary, Mill, Tavern, Plough, Famine, Apprenticeship, Plough
Piles: Claw 34, Tree 17, Wheat 8, Coin 5

---

## Round 11 (Turns 31–33)

**T31 — Alice:** Activates **Chiefdom** to move **Raid** from her discard to Bob's Domain. *Planting Mob in Bob's Domain — he has the most cards and is a threat with 2 Pastures and Worship of the Hunt. Setting up for a future Brawl.*

<details><summary>🎯 Raw OPS</summary>

```
MOVE_DISCARD|Alice|Raid
MOVE|Alice|Raid|DOMAIN|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ MOVE_DISCARD Raid Alice's discard → Alice's Domain
- ✅ MOVE Raid Alice's Domain → Bob's Domain

</details>

**T32 — Bob:** Activates **Warband** to trigger Brawl in Charlie's Domain (8 cards, the largest). *Charlie's Pathfinding engine is the biggest threat — time to strip it before he runs away with the game.* Brawl fires in Charlie's Domain. Charlie has no On Brawl responders and no Mob cards, so the Brawl baseline applies: Charlie discards 1 card of his choice. Charlie discards Sowing (already has Herbalism for recovery, and his Nature count is weak anyway).

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Sowing|DISCARD
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Sowing Charlie's Domain → Charlie's discard

</details>

**T33 — Charlie:** Activates **Sky Dance** to trigger Rite. *With Worship of Fertility responding, this chains into Harvest which refills Fields and could trigger further effects.* Rite fires in Charlie's Domain. Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Harvest event fires — Fields refill from 7 to 7 (already full, no refill needed). Bob's Solstice responds to Harvest: Bob chooses to have all players of his culture (Nomad) draw 1 from Tree — but Charlie has no culture card, so only Bob draws. Bob draws Regrowth (Drafted) — all Pasture cards in discard return to owners' Domains. No Pastures in any discard. Regrowth moves to discard.

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|tree|1|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD tree → Regrowth → Bob's discard

</details>

## Round 12 (Turns 34–36)

**T34 — Alice:** Activates **Chiefdom** to move **Raid** from Bob's Domain to Charlie's Domain. *Positioning Mob in Charlie's undefended Domain for a future Brawl — Charlie has no Militia or Eldership, making them vulnerable.* Charlie now holds a [Mob] card that will backfire when Brawl is triggered against them.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Bob|Raid|DOMAIN|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Raid Bob's Domain → Charlie's Domain

</details>

**T35 — Bob:** Activates **Warband** to trigger Brawl in Charlie's Domain (most cards with 8). *Charlie's Pathfinding engine is the biggest threat — stripping cards now before he runs away with the game.* Charlie has Raid which responds On Brawl: Charlie must give 1 card to Bob. Charlie gives Oral Tradition (least useful without Coin access). No other On Brawl responders.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Oral Tradition|DOMAIN|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Oral Tradition Charlie's Domain → Bob's Domain

</details>

**T36 — Charlie:** Activates **Sky Dance** to trigger Rite. *With Worship of Fertility responding, this chains into Harvest which refills Fields and builds toward Wheat depletion where I'm competitive.* Rite fires in Charlie's Domain. Worship of Fertility responds: triggers Harvest in Charlie's Domain. Harvest event fires — Fields refill from 7 to 7 (already full, no change). Bob's Solstice has On Harvest but only triggers on actual Harvest events, not from Rite chains. Charlie's Solstice also has On Harvest — Charlie chooses to have all players of his culture draw 1 from Tree. Charlie has no Culture card, so only Charlie benefits: draws Sacred Grove.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|1|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW tree → Sacred Grove → Charlie's Domain

</details>

## Round 13 (Turns 37–39)

**T37 — Alice:** Activates **Chiefdom** to move **Raid** from Charlie's Domain to Bob's Domain. *Bob has the most cards and is leading [Nature] — planting Mob there sets up a devastating Brawl next turn.* Charlie loses a [Discontent] but Bob gains a liability.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Raid|DOMAIN|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Raid Charlie's Domain → Bob's Domain

</details>

**T38 — Bob:** Activates **Warband** to trigger Brawl in Charlie's Domain (7 cards, tied with Bob but Charlie is the bigger threat with Pathfinding engine). *Charlie's Pathfinding + Knowledge stack is snowballing — must strip cards before he runs away with Tree.* Brawl fires in Charlie's Domain. No [Mob] cards present, so baseline Brawl applies: Charlie discards 1 card of their choice. Charlie discards Herbalism (least essential to their Rite engine).

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Herbalism|DISCARD
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Herbalism Charlie's Domain → Charlie's discard

</details>

**T39 — Charlie:** Activates **Sky Dance** to trigger Rite. *With Worship of Fertility and Sacred Grove responding, this chains into Harvest for Fields refill and potential scoring acceleration.* Rite fires globally. Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Charlie's Sacred Grove could respond but Charlie chooses not to use it. Fields refill from 7 to 7 (already full, no change). Bob's Solstice responds to Harvest: Bob chooses to have all players of Nomad culture draw 1 from Tree. Bob draws Pasture. No other players share Nomad culture.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|1|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW tree → Pasture → Bob's Domain

</details>

## Round 14 (Turns 40–42)

**T40 — Alice:** Activates **Chiefdom** to move Bob's **Raid** from his Domain to Charlie's Domain. *Planting Mob in Charlie's Domain sets up a devastating Brawl — Charlie has zero Brawl defense and Alice can trigger Warband next turn via Claw draw.* The [Mob] card shifts allegiance, now primed to punish Charlie when Brawl fires.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Bob|Raid|DOMAIN|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Raid Bob's Domain → Charlie's Domain

</details>

---

### === STATE AFTER TURN 40 ===

**Alice** (4 cards): Crags, Armament, Crags, Chiefdom
  Discard: Harvest, Ingenuity, Marauders, Raid
**Bob** (13 cards): Crags, Pasture, Nomad, Solstice, Pasture, Militia, Tavern, Worship of the Hunt, Warband, Nomad, Forage, Oral Tradition, Pasture
  Discard: Harvest, Regrowth
**Charlie** (7 cards): Pathfinding, Solstice, Crags, Sky Dance, Worship of Fertility, Sacred Grove, Raid
  Discard: Sowing, Forage, Withered Crop, Raid, Sowing, Herbalism

Season: Gathering, Nomad
Fields (7): Granary, Mill, Tavern, Plough, Famine, Apprenticeship, Plough
Piles: Claw 34, Tree 14, Wheat 8, Coin 5

---

**T41 — Bob:** Activates **Warband** to trigger Brawl in Charlie's Domain (7 cards, tied with Bob but Charlie is the bigger threat with Pathfinding engine). *Charlie's spiritual-knowledge combo will run away with the game if unchecked.* Brawl fires in Charlie's Domain. Charlie's Raid responds: gives 1 card to Bob (the triggering player). Charlie chooses to give Raid itself (least valuable). No other On Brawl effects — Charlie discards 1 card of choice (Sky Dance, to protect Pathfinding).

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Raid|DOMAIN|Bob
MOVE|Charlie|Sky Dance|DISCARD
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ MOVE Raid Charlie's Domain → Bob's Domain
- ✅ MOVE Sky Dance Charlie's Domain → Charlie's discard

</details>

**T42 — Charlie:** Activates **Sacred Grove**, choosing to trigger Rite in their Domain. *With Worship of Fertility responding, this chains into Harvest for Fields refill and potential tag acceleration.* Rite fires → Charlie's Worship of Fertility responds: triggers Harvest in Charlie's Domain. Harvest event fires → Fields refill from 7 to 7 (already full, no change). Bob's Solstice has On Harvest but Charlie triggered it, so Bob could choose to help cultural allies — but Bob is Nomad culture while Charlie has no culture card, so no cultural benefit applies.

OPS:

## Round 15 (Turns 43–45)

**T43 — Alice:** Activates **Chiefdom** to move **Raid** from Bob's Domain to Charlie's Domain. *Charlie has no Brawl defense and is leading the [Nature] race — planting Mob sets up a devastating strike next turn.* Chiefdom allows moving 1 [Mob] card from any Domain sharing Alice's culture (Highlander) to any other Domain. Bob has Nomad culture, so Alice moves from her own discard... wait, Chiefdom says "from your Domain or any Domain that shares your culture" — Alice has no Mob in her Domain, and Bob (Nomad) doesn't share Highlander culture. Alice cannot use Chiefdom effectively here.

Alice instead activates **Crags** to scout Claw. *Looking for Tyranny or useful [Trophy] cards to race Claw depletion — Alice has Chiefdom [Trophy] already.* Alice looks at top 3: Scavenge, Tyranny, Uprising. She puts Tyranny into her discard — removing it from play prevents anyone from snowballing, and she could potentially recover it with Herbalism if she acquires one.

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|claw|1|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD claw → Scavenge → Alice's discard

</details>

**T44 — Bob:** Activates **Warband** to trigger Brawl in Alice's Domain (the largest with 4 cards). *Alice is building [Trophy] tags and has Chiefdom — need to strip her before Claw depletes.* Alice has no Brawl defense (2 Crags but that requires attacker to discard, and Bob doesn't care). Alice has no On Brawl responders. Brawl baseline fires — Alice must discard 1 card of her choice. Alice discards Armament (least useful without Sword deck access).

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Alice|Armament|DISCARD
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Armament Alice's Domain → Alice's discard

</details>

**T45 — Charlie:** Activates **Sacred Grove**, choosing to trigger Rite. *With Worship of Fertility responding, this chains into Harvest → Fields refill, building toward [Nature] win.* Rite fires in Charlie's Domain. Worship of Fertility responds: triggers Harvest in Charlie's Domain. Fields refill from 7 to 7 (already full, no refill needed). Bob's Worship of the Hunt responds to Rite: Bob may activate all [Hunt] cards — Bob has no [Hunt] cards, so no effect.

OPS:

---

## Epilogue

**Alice** — 3 cards
  Domain: Crags, Crags, Chiefdom
  Tags: [Allegiance]×1, [Land]×2, [Nature]×2

**Bob** — 14 cards
  Domain: Crags, Pasture, Nomad, Solstice, Pasture, Militia, Tavern, Worship of the Hunt, Warband, Nomad, Forage, Oral Tradition, Pasture, Raid
  Tags: [Culture]×2, [Discontent]×2, [Knowledge]×1, [Land]×4, [Mob]×1, [Nature]×4, [Spiritual]×1, [Unit]×2

**Charlie** — 5 cards
  Domain: Pathfinding, Solstice, Crags, Worship of Fertility, Sacred Grove
  Tags: [Knowledge]×1, [Land]×1, [Nature]×3, [Spiritual]×2

### Stats
API calls: 45 | Piles: Claw 33, Tree 14, Wheat 8, Coin 5, Candle 1
