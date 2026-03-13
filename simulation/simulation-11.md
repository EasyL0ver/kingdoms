# Simulation 11 — Careful Event Play

**Same rules as Sim 10.** Focus on smarter player decisions: no empty Brawls, deliberate Rabble deployment, only trigger events with payoff.

**Players:** Alice, Bob, Charlie (3 players, 10 rounds = 30 turns)

---

## Deck Orders (shuffled)

**Claw (37):** Marauders, Poach, Scavenge, Land Grab, Marauders, Ingenuity, Poach, Chiefdom, Poach, Armament, Foray, Chiefdom, Outriders, Raid, Duel, Outriders, Share the Spoils, Share the Spoils, Land Grab, Scavenge, Racketeering, Land Grab, Poach, Raid, Scavenge, Blood Offering, Incite, Raid, Raid, Warband, Warband, Foray, Worship of War, Racketeering, Incite, Worship of the Hunt, Ingenuity

**Tree (41):** Withered Crop, Nomad, Gathering, Pathfinding, Withered Crop, Worship of the Rain, Gathering, Harvest, Nomad, Harvest, Pasture, Pasture, Forage, Sky Dance, Crags, Worship of Fertility, Sowing, Crags, Forage, Nomad, Oral Tradition, Regrowth, Crags, Solstice, Pathfinding, Withered Crop, Highlander, Sacred Grove, Pasture, Pasture, Highlander, Regrowth, Solstice, Highlander, Harvest, Crags, Harvest, Herbalism, Sowing, Eldership, Sowing

**Wheat (17):** Granary, Animal Husbandry, Tavern, Tavern, Feed the Commoners, Mill, Famine, Animal Husbandry, Militia, Militia, Famine, Mill, Plough, Plough, Plough, Granary, Apprenticeship

**Coin (5):** Rumour ×2, Mine, Rumour, Mine

---

## Initial State

Season 1: **Withered Crop**, **Nomad**, **Gathering**, **Pathfinding**
Fields (7): **Granary**, **Animal Husbandry**, **Tavern** ×2, **Feed the Commoners**, **Mill**, **Famine**

---

## Round 1 (Turns 1–3)

**T1 — Alice:** Takes **Pathfinding** [Knowledge] from Season. Tree draw engine.
→ Domain: Pathfinding

**T2 — Bob:** Takes **Gathering** from Season → Immediate. Bob has no culture, no cards that respond to events. Chooses Rite in his Domain (local). Nothing responds. Gathering to discard.
→ Discard: Gathering
→ 🟡 Gathering wasted early — no cards to respond.

**T3 — Charlie:** Takes **Withered Crop** from Season. Future Wheat gate (needs Harvest in discard).
→ Domain: Withered Crop
→ Season: Nomad (1 left)

---

## Round 2 (Turns 4–6)

**T4 — Alice:** Draws Claw (2): **Marauders** [Rabble], **Poach** [Rabble][Hunt].
→ Domain: Pathfinding, Marauders, Poach (3 cards)

**T5 — Bob:** Draws Claw (2): **Scavenge** [Rabble], **Land Grab** [Discontent].
Land Grab: Activate later — holds it for a good Season.
→ Domain: Scavenge, Land Grab (2 cards)

**T6 — Charlie:** Takes **Nomad** from Season (last) → no Pasture → bounces to discard.
→ Discard: Nomad
→ Season 1 empty → Season 2: **Withered Crop**, **Worship of the Rain**, **Gathering**, **Harvest**

---

## Round 3 (Turns 7–9)

**T7 — Alice:** Takes **Harvest** from Season 2 → Immediate → Harvest event!
Fields 7/7, no refill needed. Harvest to discard.
→ Discard: Harvest

**T8 — Bob:** Takes **Worship of the Rain** [Spiritual] from Season 2. On Rite — swap Season card.
→ Domain: Scavenge, Land Grab, Worship of the Rain (3 cards)

**T9 — Charlie:** Takes **Withered Crop** from Season 2. Now has 2 Withered Crop... 
Wait, he already has 1. Both need Harvest in discard. Still no Harvest → neither works yet.
Actually, takes **Gathering** instead. → Immediate. No culture, no responders. Chooses Rite locally → fizzles. To discard.
→ Discard: Nomad, Gathering
→ Season: Withered Crop (1 left)

---

## Round 4 (Turns 10–12)

**T10 — Alice:** Activates **Poach** → Feast in her Domain!
→ **Marauders** fires On Feast: discard self, draw 1 Claw → draws **Marauders** (2nd copy!) [Rabble].
→ Domain: Pathfinding, Poach, Marauders (3 cards, swapped one Marauders for another)
→ Discard: Harvest, Marauders
→ 🟢 Poach→Feast→Marauders cycle! Hunters feed, riffraff cycles.

**T11 — Bob:** Takes **Withered Crop** from Season (last). Has no Harvest in discard → doesn't work yet.
→ Domain: Scavenge, Land Grab, WotR, Withered Crop (4 cards)
→ Season 2 empty → Season 3: **Nomad**, **Harvest**, **Pasture**, **Pasture**

**T12 — Charlie:** Takes **Harvest** from Season 3 → Immediate → Harvest! Fields 7/7 → no refill. To discard.
→ Discard: Nomad, Gathering, Harvest
→ 🟢 Withered Crop now live! Charlie has Wheat access (Turn 12).

---

## Round 5 (Turns 13–15)

**T13 — Alice:** Takes **Pasture** from Season 3. First [Nature][Land]!
→ Domain: Pathfinding, Poach, Marauders, Pasture (4 cards)
→ Hunt limit: global 1 + 1 Pasture = 2 [Hunt] can work in her Domain.

**T14 — Bob:** Activates **Land Grab**! Season 3 has: Nomad, Pasture. Nomad is [Culture] not [Land]. Only Pasture is [Land].
Takes **Pasture** from Season → his Domain! Land Grab to discard.
→ Domain: Scavenge, WotR, Withered Crop, Pasture (4 cards)
→ Discard: Gathering, Land Grab
→ Season: Nomad (1 left)
→ 🟢 Land Grab waited for the right moment (not T5 when drawn, but T14 when Season had Land). Activate timing works!

**T15 — Charlie:** Activates **Wheat zone!** Fields: Granary, AH, Tavern ×2, Feed the Commoners, Mill, Famine.
Strategic farmer. Takes **3 cards**: Tavern, Tavern, Mill.
Draws **3 Claw**: **Ingenuity** [Craftsmanship][Discontent], **Poach** [Hunt][Rabble], **Chiefdom** [Allegiance].
Ingenuity: Immediate → draw 1 Coin → **Rumour** → trigger Rumour → to discard.

→ Domain: Withered Crop, Tavern ×2, Mill, Poach, Chiefdom (6 cards)
→ Discard adds: Rumour, Ingenuity? No — Ingenuity stays in Domain (Immediate draws Coin, card stays). 
→ Domain: Withered Crop, Tavern ×2, Mill, Poach, Chiefdom, Ingenuity (7 cards)
→ Fields: Granary, AH, Feed the Commoners, Famine (4 remaining)
→ 🟢 Big Wheat play! 3 farm cards + 3 Claw draws. Got economy (Mill), Discontent cleanup (Tavern ×2), movement (Chiefdom), food (Poach), AND a Coin draw from Ingenuity.

---

## Round 6 (Turns 16–18)

**T16 — Alice:** Activates **Pathfinding** → 1 Knowledge = draw top 1 Tree: **Forage**.
→ Domain: Pathfinding, Poach, Marauders, Pasture, Forage (5 cards)

**T17 — Bob:** Has Harvest in discard? No — only Gathering and Land Grab. Withered Crop doesn't work.
Has 1 [Nature] (Pasture). No Sowing.
Takes **Nomad** from Season (last card) → has Pasture → Nomad STAYS! 🟢
→ Domain: Scavenge, WotR, Withered Crop, Pasture, Nomad (5 cards)
→ **Bob is Nomad!** First culture this sim (Turn 17).
→ Season 3 empty → Season 4: **Sky Dance**, **Crags**, **Worship of Fertility**, **Sowing**

**T18 — Charlie:** Activates **Poach** → Feast in her Domain!
→ **Tavern** fires On Feast: may discard 1 [Discontent] → discards **Ingenuity** [Discontent]. ✓
→ **Tavern #2** fires On Feast: may discard 1 [Discontent] → discards **Poach** [Discontent].
Wait — Poach is the card that triggered Feast. Can you discard the activating card? The Feast already triggered. Let's say yes — the effect is "discard from Domain" and Poach is in Domain.
→ Domain: Withered Crop, Tavern ×2, Mill, Chiefdom (5 cards)
→ Discard adds: Ingenuity, Poach
→ 🟢 Double Tavern cleaned 2 Discontent off a single Feast! Charlie's Domain is pristine.

---

## Round 7 (Turns 19–21)

**T19 — Alice:** Takes **Sowing** [Knowledge] from Season 4. Has 1 [Nature] (Pasture). Needs 2+. Not working yet. But Pathfinding now counts 2 Knowledge!
→ Domain: Pathfinding, Poach, Marauders, Pasture, Forage, Sowing (6 cards)

**T20 — Bob:** Takes **Sky Dance** [Spiritual] from Season 4. Rite trigger!
→ Domain: Scavenge, WotR, Withered Crop, Pasture, Nomad, Sky Dance (6 cards)
→ 🟢 Bob has Sky Dance! But no Worship cards to exploit Rite yet. WotR just swaps a Season card. He'd trigger Rite only when it benefits him.

**T21 — Charlie:** Activates **Mill** → discard Mill, draw 1 Coin → **Rumour** → trigger Rumour → to discard.
→ Domain: Withered Crop, Tavern ×2, Chiefdom (4 cards)
→ Discard adds: Mill, Rumour
→ Mill→Coin economy works again.

---

## Round 8 (Turns 22–24)

**T22 — Alice:** Activates **Forage** — top 3 Tree: Crags, Forage, Nomad. All to discard.
Has Pasture → takes **Nomad** [Culture]! Discards Forage.
Nomad: Immediate — has Pasture ✓. Stays!
→ Domain: Pathfinding, Poach, Marauders, Pasture, Sowing, Nomad (6 cards)
→ Discard: Harvest, Marauders, Forage, Crags, Forage(deck)
→ **Alice is Nomad!** (Turn 22). Same culture as Bob!
→ 🟢 Two Nomads! Gathering/Solstice/Chiefdom now have culture synergy potential.

**T23 — Bob:** Activates **Sky Dance** → Rite (global)!
→ Bob's **Worship of the Rain** fires: swap any Season card with top of Tree pile.
Season 4 has: Crags, Worship of Fertility (2 left). Bob swaps **Worship of Fertility** → put on bottom (or discard?). Card text: "discards any card from the Season and replaces it with the top card from the Tree pile."
Top of Tree pile: **Oral Tradition** [Knowledge].
→ Season 4: Crags, Oral Tradition (WoF gone, replaced)
→ Bob sculpted the Season! Removed a [Nature][Spiritual] and brought in [Knowledge].
→ 🟢 Sky Dance→Rite→WotR is a Season manipulation tool. Targeted and useful.

**T24 — Charlie:** Draws Claw (2): **Poach** [Hunt][Rabble], **Armament** [Knowledge].
Charlie has Chiefdom [Allegiance]. Could deploy Poach later.
→ Domain: Withered Crop, Tavern ×2, Chiefdom, Poach, Armament (6 cards)

---

## Round 9 (Turns 25–27)

**T25 — Alice:** Activates **Pathfinding** → 2 Knowledge (Pathfinding + Sowing) = draw top 2 from Tree pile.
Draws: **Regrowth**, **Crags**.
Regrowth: Immediate → returns all Pastures from discard → no Pastures in any discard → fizzles. To discard.
Crags: [Nature][Land]! Now Alice has 2 [Nature] (Pasture + Crags). **Sowing works! Wheat unlocked!** 🟢 (Turn 25)
→ Domain: Pathfinding, Poach, Marauders, Pasture, Sowing, Nomad, Crags (7 cards)
→ Discard adds: Regrowth
→ Alice has both lands! Crags + Pasture. She's Nomad but has Highlander terrain too.

**T26 — Bob:** Takes **Crags** from Season 4. Now has Pasture + Crags = 2 [Nature].
→ Domain: Scavenge, WotR, Withered Crop, Pasture, Nomad, Sky Dance, Crags (7 cards)
→ Bob has Withered Crop + Harvest in discard... wait, does Bob have Harvest in discard? No — Bob's discard is Gathering, Land Grab. No Harvest.
→ But Bob has 2 [Nature] and no Sowing. Still no Wheat gate!

**T27 — Charlie:** Activates **Chiefdom** → move 1 [Rabble] from his Domain to any other Domain. Charlie has no culture → can only move from own Domain.
Moves **Poach** to Alice's Domain! (Poach competes for Hunt limit — resource denial!)
→ Charlie: Withered Crop, Tavern ×2, Chiefdom, Armament (5 cards)
→ Alice: +Poach(Charlie's) = 8 cards
→ 🟢 Smart play! Charlie deployed Poach not for Brawl, but to eat Alice's hunting rights. Alice already has her own Poach → now 2 Hunt cards in her Domain. Global limit is 1 + her 1 Pasture = 2. She's at the limit. A third Poach would be locked.
→ Charlie doesn't WANT to Brawl — Poach has no On Brawl text. This is pure economic warfare.

---

## Round 10 (Turns 28–30)

**T28 — Alice:** Has 2 Poach in Domain (1 hers, 1 Charlie's). Both work (2 Hunt = her limit with 1 Pasture).
She wants to fight back. Activates **Wheat** (via Sowing, 2 Nature). 
Fields: Granary, AH, Feed the Commoners, Famine (4 remaining).
Takes **2 cards**: Animal Husbandry, Feed the Commoners.
AH: Immediate — discard Pasture or discard AH. She discards **Pasture**! 🔴 Loses Nomad anchor and Hunt limit drops.
Wait — losing Pasture means: Hunt limit drops to global 1 + 0 Pasture = 1. She has 2 Poach. Only 1 works now!
Feed the Commoners: Immediate — discard up to 3 [Discontent]. Discards **Marauders** + **Charlie's Poach** (both [Discontent]).
Draws **2 Claw** (Wheat tax): **Foray** [Discontent], **Chiefdom** [Allegiance].

→ Domain: Pathfinding, Poach, Sowing, Nomad, Crags, AH, Chiefdom, Foray (8 cards)
→ Discard adds: Pasture, Marauders, Poach(Charlie's), Feed the Commoners
→ 🟢 Feed the Commoners purged Charlie's Poach! Counter to economic warfare.
→ 🔴 But lost Pasture to AH cost. Nomad culture check? Nomad stays (it's already in Domain, prerequisite was on arrival only).
→ Regrowth in Alice's discard → future Pasture recovery possible!

**T29 — Bob:** Still no Wheat gate. Draws Claw (2): **Outriders**, **Raid** [Rabble].
Outriders: draw 3, discard 1. Uses it next turn (it's Activate).
→ Domain: Scavenge, WotR, Withered Crop, Pasture, Nomad, Sky Dance, Crags, Outriders, Raid (9 cards)
→ Bob has Raid + Scavenge. Both have On Brawl effects. If he gets them into someone's Domain and triggers Brawl...

**T30 — Charlie:** Activates **Wheat** (via Withered Crop, Harvest in discard ✓).
Fields: Granary, Famine (2 remaining).
Takes **1 card**: Granary [Labour].
Draws **1 Claw**: **Duel**.
→ Domain: Withered Crop, Tavern ×2, Chiefdom, Armament, Granary, Duel (7 cards)
→ Fields: Famine (1 remaining!)

---

## State After Round 10

**DOMAINS:**
- **Alice (8):** Pathfinding, Poach, Sowing, Nomad✦, Crags, Animal Husbandry, Chiefdom, Foray
- **Bob (9):** Scavenge, Worship of the Rain, Withered Crop, Pasture, Nomad✦, Sky Dance, Crags, Outriders, Raid
- **Charlie (7):** Withered Crop, Tavern ×2, Chiefdom, Armament, Granary, Duel

**DISCARDS:**
- **Alice (7):** Harvest, Marauders ×2, Forage ×2, Regrowth, Crags(from tree), Pasture, Poach, Feed the Commoners
- **Bob (2):** Gathering, Land Grab
- **Charlie (7):** Nomad, Gathering, Harvest, Ingenuity, Poach, Mill, Rumour ×2

**CULTURES:** Alice = Nomad ✦ | Bob = Nomad ✦ | Charlie = none

**Season 4:** Oral Tradition (1 remaining)
**Fields:** Famine (1 remaining!)
**Claw remaining:** 23 | **Tree remaining:** 17 | **Wheat remaining:** 7 | **Coin remaining:** 3

---

## What Happens Next (Projected)

**Bob is loaded.** 9 cards including Raid + Scavenge + Outriders + Sky Dance. Next moves:
- Activate Outriders (draw 3 Claw, discard 1) to find Incite or another mover
- Use Chiefdom... wait, Bob doesn't have Chiefdom. He needs Incite to deploy Raid/Scavenge.
- Or: Sky Dance → Rite → if he finds Worship of War, instant Brawl anywhere.

**Alice and Bob are same-culture Nomads.** If either gets Gathering, it fires events in BOTH Domains. Alice's Chiefdom can pull [Rabble] from Bob's Domain (same culture). Powerful alliance potential — or betrayal.

**Charlie is the farmer king.** Clean Domain (double Tavern purges Discontent), Wheat access, Granary for Feast. But no combat presence and no culture.

---

## Observations

### 🟢 Working Well

1. **NO EMPTY BRAWLS!** Zero Brawls this sim — because players correctly identified there was no payoff. Raid/Scavenge were drawn but never deployed. Smart play.

2. **Poach as economic warfare** — T27: Charlie deployed Poach to Alice's Domain to eat her Hunt limit. Not for Brawl — for resource denial. This is a totally new use case that emerged naturally. 🔥

3. **Feed the Commoners as defense** — T28: Alice purged enemy Poach + her own Marauders. Counter-espionage via farming card.

4. **Land Grab timing** — T14: Bob held Land Grab from T5 until T14 when Season had a Pasture. Patient, deliberate. Activate > Immediate.

5. **Double Tavern engine** — T18: Charlie's Feast cleaned 2 Discontent at once. Tavern stacking works.

6. **Culture formed organically** — Alice (T22 via Forage→Nomad) and Bob (T17 via Season pick). Both Nomad. Genuine same-culture faction.

7. **Sky Dance→WotR Season sculpting** — T23: Bob manipulated which cards are in the Season. Subtle but powerful Rite use without needing Brawl.

8. **Wheat 7-card display** — Two big plays (T15 Charlie 3 cards, T28 Alice 2 cards). Both were strategic, not degenerate. The Claw tax self-balances.

9. **Ingenuity→Coin chain** — Fired again (T15). Reliable Claw→Coin pivot.

### 🟡 Concerns

1. **Bob stuck without Wheat gate for 30 turns** — Has 2 Nature, Withered Crop, but no Harvest in discard. Has Sowing but got it late. Some players just don't get the right combination. Shuffle variance or too few gates?

2. **Fields depleted to 1 (Famine!)** — Only 1 Harvest fired (T12) and it fizzled (Fields were full). No refill happened. With 7-card display, Fields drain fast.

3. **No Brawl at all** — Good that players didn't waste actions on empty Brawls, but combat still hasn't happened with proper setup. The deploy-then-Brawl pipeline needs more turns.

4. **Crags peek still feels weak** — Nobody used it. Drawing 2 from Claw is just better than peeking.

5. **AH eating Pasture is brutal** — Alice lost her Pasture (T28), reducing Hunt limit and weakening Nomad position. Plough/AH land costs create real tension though.

### Key Stat Comparison

| Metric | Sim 10 | Sim 11 |
|---|---|---|
| Brawls | 2 (empty) | **0 (correct!)** 🟢 |
| Poach economic warfare | — | **T27** 🟢🆕 |
| First culture | Never | **T17** 🟢 |
| Same-culture faction | — | **Alice+Bob Nomad** 🟢 |
| Wheat plays | T18, T22 | **T15, T28, T30** 🟢 |
| Land Grab (activate) | — | **T14 (patient)** 🟢 |
| Season sculpting | — | **T23 (WotR)** 🟢 |
| Feed the Commoners | T22 | **T28 (purged enemy Poach!)** 🟢 |

---

## Design Insights

1. **Poach as [Hunt] denial is an emergent mechanic** — nobody designed this explicitly, it fell out of the global Hunt limit + Rabble deployment. This is the best kind of game design.

2. **Brawl needs setup = good** — Players correctly avoided empty Brawls. Combat is surgical, not random. This makes Raid/Scavenge deployment meaningful.

3. **Wheat 7-card display is the right power level** — big enough to be worth building toward, Claw tax prevents abuse, Feed the Commoners/Tavern clean up the mess.

4. **Culture matters** — Alice and Bob share Nomad culture. If either had Gathering, it would fire events in both Domains. Chiefdom lets them move Rabble between their Domains. Real alliance forming.

5. **Crags peek should probably just be removed** — it's never used. Let Crags be pure passive (Brawl defense + Nature + Land). Same as Pasture (blank + Nature + Land + Hunt limit).
