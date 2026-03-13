# Simulation — AI-Driven (v2)

**Players:** Alice, Bob, Charlie (3 players, 34 rounds = 100 turns)

---

## Initial State

Season: Pathfinding, Regrowth, Crags, Gathering
Fields (7): Feed the Commoners, Mill, Famine, Granary, Famine, Granary, Tavern
Piles: Claw 40, Tree 37, Wheat 10, Coin 5, Candle 1

---

## Round 1 (Turns 1–3)

**T1 — Alice:** Takes **Crags** from Season. *Early land grab is essential — Crags is a [Nature][Land] foundation card that enables Highlander culture later and provides Brawl defense at 2+ copies.* The card enters Alice's Domain with no Drafted effect.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Crags|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Crags → Alice's Domain

</details>

**T2 — Bob:** Takes **Pathfinding** from Season. *With an empty Domain, Pathfinding is the strongest card available — it's [Knowledge] which fuels itself, and even at 1 [Knowledge] it draws 1 Tree card per activation, scaling rapidly as Bob accumulates more Knowledge cards.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Pathfinding|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Pathfinding → Bob's Domain

</details>

**T3 — Charlie:** Takes **Regrowth** from Season. *With an empty Domain, Charlie needs to start building — Regrowth is Drafted, triggering all Pasture cards in discard to return to their owners' Domains, but no Pastures are in any discard pile, so the effect does nothing. Regrowth then moves to Charlie's discard. Gathering is the other option but its events would fire on an empty Domain with no culture allies — equally useless. Drawing from Claw risks Uprising as the top card which would Brawl an empty Domain pointlessly. Regrowth at least puts a card in discard for future Herbalism retrieval and clears the Season toward a refill with potentially better cards.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON_DISCARD|Regrowth|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON_DISCARD Regrowth → Charlie's discard

</details>

## Round 2 (Turns 4–6)

**T4 — Alice:** Takes **Gathering** from the Season. *With only one card in the Season, it's the only Tree option, and Gathering's flexible event trigger is valuable — choosing Rite here with no Spiritual responders anywhere would be pointless, and Rumour has no responders either, so Alice chooses Brawl targeting her own Domain. With only Crags and no Mob cards, the Brawl has no "On Brawl" responders anywhere, so it resolves harmlessly — a clean way to cycle Gathering to discard without cost.* Gathering is Drafted: Alice chooses to trigger Brawl in her Domain. No player has any On Brawl responders, so the Brawl resolves with no effect. Gathering moves to discard. The Season is now empty, so a new Season of 4 cards is revealed from the Tree pile.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON_DISCARD|Gathering|Alice
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ TAKE_SEASON_DISCARD Gathering → Alice's discard
- 🔄 Season auto-refilled: [Oral Tradition, Eldership, Crags, Nomad]

</details>

**T5 — Bob:** Activates **Pathfinding** to draw from the Tree pile. *Pathfinding draws cards equal to [Knowledge] count — Bob has 1 [Knowledge] card (Pathfinding itself), so he draws 1 from Tree.* Bob draws **Forage** — no Drafted keyword, so it enters his Domain normally. Forage gives Bob a repeatable dig tool to accelerate through the Tree pile, feeding his Knowledge-scaling engine.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|1|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ DRAW tree → Forage → Bob's Domain

</details>

**T6 — Charlie:** Takes **Crags** from Season. *With an empty Domain, Charlie needs foundation cards — Crags is a [Nature][Land] that enables Highlander later and provides Brawl defense when doubled, plus it's the strongest start available in this Season.* Crags enters Charlie's Domain.

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Crags|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Crags → Charlie's Domain

</details>

## Round 3 (Turns 7–9)

**T7 — Alice:** Takes **Crags** from the top of the Tree pile by activating the Tree zone — but the Season still has 3 cards, so she must take from the Season, not the pile. Instead, Alice takes **Eldership** from the Season. *With only one Crags and no Culture card yet, Eldership provides [Knowledge] and strong Brawl defense — a solid defensive pickup while waiting for a second land card to appear.* Eldership is [Allegiance] — Alice has no existing [Allegiance], so it stays.

Wait — let me reconsider. Alice has Crags already. The Season offers Oral Tradition, Eldership, and Nomad. Nomad requires a Pasture (which Alice doesn't have) so it would be discarded on Draft. Oral Tradition gives Candle access but needs Coin cards to fuel. Eldership gives Brawl defense and [Knowledge]. None of these are [Nature] cards that help toward a Tree-depletion win.

Actually, Alice should take from the Season (that's how Tree zone works — take 1 card from the Season). The best pick is **Eldership** — it gives Brawl protection (important with Bob having Pathfinding which could snowball) and [Knowledge] which pairs with future Pathfinding or Sowing. It also doesn't require prerequisites.

**T7 — Alice:** Takes **Eldership** from the Season. *With Crags already in Domain, Eldership adds [Knowledge] for future synergies and critical Brawl defense — Bob's Pathfinding is a growing threat that may provoke conflict soon.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Eldership|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Eldership → Alice's Domain

</details>

**T8 — Bob:** Activates **Pathfinding**. *With 2 [Knowledge] cards (Pathfinding + Forage), Bob draws 2 from the Tree pile, accelerating his engine.* Bob takes the top 2 cards from the Tree pile: **Crags** and **Highlander**. Crags enters his Domain normally. Highlander is Drafted — Bob checks for a Crags card in his Domain: he now has Crags, so Highlander stays. However, Bob has no [Culture] card yet, so Highlander enters his Domain without conflict.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|2|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW tree → Crags → Bob's Domain
- ✅ DRAW tree → Highlander → Bob's Domain

</details>

Looking at Charlie's situation: Domain has only Crags, discard has Regrowth. No culture card, no access beyond Claw and Tree. Bob is building a dangerous Pathfinding engine with 4 cards including Highlander culture. Alice has Eldership for Brawl defense.

Charlie needs to build up. The Season has Oral Tradition and Nomad. Nomad requires a Pasture (Charlie doesn't have one — would be discarded). Oral Tradition requires a Coin card to activate (Charlie has none) and unlocks Candle. Neither Season card helps Charlie right now.

Drawing from Claw gives 2 cards. Top 2 are Uprising and Chiefdom. Uprising is Drafted — triggers Brawl in Charlie's Domain. Charlie only has Crags (need 2+ Crags to cancel), so the Brawl fires but nobody benefits since Uprising says "No player benefits from On Brawl effects — cards that would be taken are discarded instead." Alice's Eldership wouldn't apply (it's Alice's Domain, not Charlie's). The Brawl in Charlie's Domain with only Crags — there are no On Brawl responders in Charlie's Domain, so the Brawl does nothing. Uprising discards itself. Then Chiefdom is a [Allegiance][Trophy] card that lets Charlie move Mob cards — decent for offensive play and gives a Trophy tag.

Alternatively, taking from Tree (Season) gives one card but neither helps now. Claw gives two cards and Chiefdom is solid. The Uprising Brawl in Charlie's Domain is harmless since no Mob/On Brawl cards are there.

**T9 — Charlie:** Draws 2 from Claw, getting **Uprising** and **Chiefdom**. *Claw draw is worth the risk — Chiefdom provides a Trophy tag and offensive capability, and Uprising's self-Brawl is harmless in a near-empty Domain.* Uprising is Drafted — triggers Brawl in Charlie's Domain with the special rule that no player benefits from On Brawl effects. Scanning Charlie's Domain (Crags) — Crags requires 2+ Crags to cancel, Charlie has only 1, so no cancel. No On Brawl responders in Charlie's Domain. Alice's Eldership only protects Alice's own Domain. The Brawl resolves with no effect. Uprising moves to discard. Chiefdom enters Charlie's Domain.

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|claw|1|Charlie
DRAW|claw|1|Charlie
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD claw → Uprising → Charlie's discard
- ✅ DRAW claw → Chiefdom → Charlie's Domain

</details>

## Round 4 (Turns 10–12)

Looking at Alice's position: she has Crags and Eldership, but no Culture card (Eldership's Brawl cancel requires sharing culture with the triggering player), no Wheat access, and only 1 [Nature] tag. The Season has Oral Tradition and Nomad — Nomad requires a Pasture (Alice has none), so it would be discarded. Oral Tradition is a gateway to Candle but needs Coin cards to fuel it.

Alice's best move is drawing from Claw. She needs to build her Domain and Claw offers 2 cards. The top 3 are Poach, Worship of War, Warband — Poach is a [Hunt] card that triggers Feast (useful), Worship of War is [Spiritual] that pairs with Rite on Brawl (decent with Eldership's knowledge theme but no Rite trigger yet), and Warband lets her attack. Two Claw draws give her Poach and Worship of War — both useful. Poach gives Feast capability and Worship of War is a strong aggressive tool if she gets a Rite trigger later.

**T10 — Alice:** Activates the Claw zone, drawing 2 cards: **Poach** and **Worship of War**. *With a thin Domain and no Wheat access yet, Alice needs to bulk up — Claw's two-card draw is the fastest path, and Poach gives her Feast access while Worship of War sets up future aggression.* Neither card is Drafted, so both enter her Domain directly. Poach gives Alice a [Hunt] activation for Feast triggers, and Worship of War will combo powerfully if she ever gets a Rite trigger (Sacred Grove, Sky Dance, or Gathering from discard via Herbalism). Alice eyes Bob's growing Domain nervously — Pathfinding with 2 [Knowledge] cards is about to snowball.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|2|Alice
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW claw → Poach → Alice's Domain
- ✅ DRAW claw → Worship of War → Alice's Domain

</details>

---

### === STATE AFTER TURN 10 ===

**Alice** (4 cards): Crags, Eldership, Poach, Worship of War
  Discard: Gathering
**Bob** (4 cards): Pathfinding, Forage, Crags, Highlander
**Charlie** (2 cards): Crags, Chiefdom
  Discard: Regrowth, Uprising

Season: Oral Tradition, Nomad
Fields (7): Feed the Commoners, Mill, Famine, Granary, Famine, Granary, Tavern
Piles: Claw 36, Tree 30, Wheat 10, Coin 5

---

**T11 — Bob:** Activates **Pathfinding**. *With Pathfinding and 2 [Knowledge] cards (Pathfinding itself and Forage), Bob draws 2 from the Tree pile, accelerating his Nature-tag collection toward a Tree-depletion victory.* Bob draws Withered Crop and Regrowth. Regrowth is Drafted — all Pasture cards in all discards return to their owners' Domains. No Pastures are in any discard, so nothing happens; Regrowth moves to Bob's discard. Withered Crop stays in Bob's Domain (not Drafted, no immediate trigger).

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|1|Bob
DRAW_DISCARD|tree|1|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW tree → Withered Crop → Bob's Domain
- ✅ DRAW_DISCARD tree → Regrowth → Bob's discard

</details>

**T12 — Charlie:** Activates the **Tree zone**, taking **Oral Tradition** from the Season. *Charlie has only two cards in Domain and needs to build infrastructure — Oral Tradition gives future Candle deck access via Coin sacrifice, and with Crags already in Domain it's a Knowledge card that adds utility. Nomad is useless without a Pasture, and Claw draws are too risky this early in Charlie's development. Oral Tradition also pairs well if Charlie can get Coin cards later.*

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON|Oral Tradition|Charlie
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ TAKE_SEASON Oral Tradition → Charlie's Domain

</details>

## Round 5 (Turns 13–15)

**T13 — Alice:** Activates **Poach**, triggering Feast in her Domain. *With Worship of War already in place and no Feast responders yet, this secures a Feast trigger to keep tempo while the Hunt limit allows it — Alice has 0 Pastures but the global hunt limit of 1 hasn't been used this round.* Feast fires in Alice's Domain. Scanning all Domains for On Feast cards — no cards respond (no Tavern, Share the Spoils, Marauders, or Plough in any Domain). The Feast resolves with no further effects. Poach itself has no discard clause, so it remains in Alice's Domain.

OPS:

**T14 — Bob:** Activates **Pathfinding**. *With 3 [Knowledge] cards in Domain (Pathfinding, Highlander, Withered Crop), Bob draws 3 from the Tree pile, pulling Solstice, Sowing, and Sacred Grove — a massive haul that accelerates his Nature engine.* Solstice, Sowing, and Sacred Grove all enter Bob's Domain. None are Drafted, so no immediate triggers. Bob now has Sowing with 2 [Nature] cards (Crags, Sacred Grove), unlocking Wheat access. Sacred Grove gives him a repeatable Rite trigger alongside his growing spiritual toolkit.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|3|Bob
```

</details>

<details><summary>📋 Ops Trace (3 applied, 0 violations)</summary>

- ✅ DRAW tree → Solstice → Bob's Domain
- ✅ DRAW tree → Sowing → Bob's Domain
- ✅ DRAW tree → Sacred Grove → Bob's Domain

</details>

**T15 — Charlie:** Activates **Oral Tradition** — discards a Coin card... but wait, Charlie has no Coin card in Domain to discard. Oral Tradition requires discarding a Coin card. Instead, Charlie activates the **Claw zone**, drawing 2 cards blind. *Bob's Pathfinding + 4 Knowledge cards is terrifying — Charlie needs aggressive tools to disrupt him before he runs away with the game.* Charlie draws **Warband** and **Duel**. Neither is Drafted. Warband is excellent — Charlie can use it next turn to Brawl Bob's massive Domain. Duel is dead weight without Warlords in play.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|2|Charlie
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW claw → Warband → Charlie's Domain
- ✅ DRAW claw → Duel → Charlie's Domain

</details>

## Round 6 (Turns 16–18)

Looking at Alice's position: she has Crags, Eldership, Poach, and Worship of War. She has only 1 [Nature] tag (Crags), so she can't win a Tree depletion race. She has 0 [Trophy] and 0 [Amenity] tags — she's behind on every axis. Her Worship of War lets her Brawl any Domain on Rite, and she has Poach for Feast. But she has no Rite trigger (no Sky Dance, no Sacred Grove, no Blood Offering).

Her best move is to grab Pasture from the top of the Tree pile via the Season. But the Season only has Nomad, and she has no Pasture so Nomad would be discarded. She could draw from Claw (Armament, Outriders, Scavenge) — Outriders would be excellent (draw 3 from Claw, discard 1, repeatable). Drawing from Claw gets 2 cards. Top 2 are Armament and Outriders.

Armament needs Coin cards and Sword deck (not in game) — dead card. Outriders is fantastic for Alice — repeatable Claw draw engine that's strictly better than the Claw zone. This accelerates her toward finding Incite, Raid, Share the Spoils, or other key pieces. Alice should activate the Claw zone to draw 2.

**T16 — Alice:** Activates the **Claw zone**, drawing **Armament** and **Outriders**. *With no Rite trigger and no gateway cards, Alice needs to build her engine fast — Outriders gives her a repeatable Claw draw that's strictly better than the zone itself.* Armament is a dead card (no Sword deck in play, no Coin cards) but Outriders is a powerful pickup. No Drafted effects on either card; no events triggered.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|2|Alice
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW claw → Armament → Alice's Domain
- ✅ DRAW claw → Outriders → Alice's Domain

</details>

**T17 — Bob:** Activates **Pathfinding**, drawing cards from the Tree pile equal to his [Knowledge] count. Bob has Pathfinding [Knowledge], Sowing [Knowledge], and Withered Crop... wait, Withered Crop has no tags — just Pathfinding [Knowledge] and Sowing [Knowledge], so 2 [Knowledge] cards = draw 2 from Tree. He draws **Pasture** and **Sowing**. Pasture has no Drafted effect and enters his Domain — excellent, another [Nature] card. Sowing is a duplicate; Bob already has one, but it's still a [Knowledge] card that fuels future Pathfinding draws and provides redundant Wheat access. Both enter his Domain. *Bob's Knowledge engine is snowballing — 4 [Knowledge] cards now means Pathfinding draws 4 next time, and 4 [Nature] cards (Crags, Pasture, Sacred Grove, Sowing) position him strongly for a Tree-depletion victory.*

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|2|Bob
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW tree → Pasture → Bob's Domain
- ✅ DRAW tree → Sowing → Bob's Domain

</details>

Looking at Charlie's position: He has Warband and Chiefdom with no Mob cards currently in his Domain to plant. He has Crags (1 [Nature]), Chiefdom ([Trophy], [Allegiance]), Oral Tradition, Warband, and Duel. Charlie needs to think about win conditions.

Bob is the biggest threat — 10 cards in Domain including Pathfinding, 2x Sowing, Sacred Grove, Pasture, Crags (2 [Nature] tags from Pasture + Crags, plus Sacred Grove has [Nature] = 3 [Nature]). If Tree depletes, Bob likely wins. Bob also has Highlander [Culture] enabling cultural defense via Eldership-like effects.

Alice has Worship of War and Poach — aggressive but only 1 [Nature] (Crags). She has Eldership [Allegiance] — no culture card though, so the Brawl-cancel condition (sharing culture with triggering player) may not apply.

Charlie should use Warband to trigger Brawl in Bob's Domain (most cards = 10). Bob has no Militia, no Eldership. Alice has Eldership but needs to share culture with Charlie to cancel — Alice has no [Culture] card, so Eldership won't trigger. Bob's Domain has no Brawl defenses (Crags x1 only, needs 2+ to cancel). Bob must give Charlie a card via... wait — Brawl itself doesn't force giving cards. Brawl fires the event, and On Brawl cards respond. Let me check: Bob has no On Brawl cards. Alice has Eldership (On Brawl) — but Charlie has no [Culture] so they don't share culture. Charlie's Crags — needs 2+ to cancel, he only has 1.

Actually, Brawl in Bob's Domain: scan for On Brawl cards globally. Nobody has relevant On Brawl responders for Bob's Domain. So Brawl does nothing mechanically. That's a wasted turn.

Better plan: Activate Chiefdom to move a [Mob] card. But Charlie has no [Mob] cards in his Domain. Chiefdom says "from your Domain or any Domain that shares your culture" — Charlie has no [Culture] card, so no shared culture Domains. Dead action.

Charlie should activate Outriders? No, that's Alice's card. Charlie's options: activate Claw zone (draw 2), activate Tree zone (take Nomad from Season), activate Oral Tradition (discard Coin card — he has none), activate Warband (Brawl biggest Domain — but no responders), Duel (no Warlords in play), Crags (scout Claw top 3).

Drawing from Claw gets Scavenge + Chiefdom. Scavenge is [Mob] — useful for planting later. Second Chiefdom would be discarded (already has [Allegiance]). But Chiefdom has [Trophy] tag — relevant if Claw depletes. Actually he already has Chiefdom occupying [Allegiance], so the second would force a discard of the existing one... or he keeps the new one. Either way, getting Scavenge as a [Mob] to plant via Chiefdom next turn is valuable setup.

**T18 — Charlie:** Activates Claw zone, drawing 2 cards: **

## Round 7 (Turns 19–21)

Looking at the board state, I need to assess Alice's position:

- Alice has no [Nature] tags (Crags has [Nature] — wait, yes Crags is [Nature][Land]). So Alice has 1 [Nature] from Crags.
- Bob is dominating with Pasture, Crags, Sacred Grove (3 [Nature]) plus Pathfinding + 3 [Knowledge] cards (Pathfinding, Sowing, Sowing) — he's a runaway threat if Tree depletes.
- Charlie has Chiefdom [Trophy] — only 1 [Trophy]. Alice has 0 [Trophy], 0 [Amenity].
- Alice has Worship of War [Spiritual] and could trigger Rite via another card, but she has no Rite trigger (no Sky Dance, no Sacred Grove, no Blood Offering... wait, she has no direct Rite trigger). Blood Offering isn't in her domain.
- Alice has **Outriders** (draw 3 from Claw, discard 1) — strictly better than Claw zone.
- Alice has **Poach** [Hunt] — can trigger Feast. She has 0 Pastures, so Hunt limit contribution is 0. Global limit is 1 [Hunt] activation per round. Has it been used this round? Turn 19 is the first turn of this round presumably, so Poach is available. But Feast with no On Feast responders in Alice's domain does nothing useful.

Best move: **Activate Outriders** to draw 3 from Claw, keep 2. The top 3 are Scavenge, Chiefdom, Worship of the Hunt. Chiefdom gives [Trophy] tag and lets Alice move Mob cards — useful for offense. Worship of the Hunt [Spiritual] adds another Rite responder. Scavenge is a [Mob] she doesn't want. Discard Scavenge, keep Chiefdom and Worship of the Hunt.

Chiefdom is [Allegiance] — Alice already has Eldership [Allegiance]. She must discard Eldership to keep Chiefdom. Chiefdom gives [Trophy] (win condition if Claw depletes) and offensive Mob-moving power. Eldership is defensive but Alice doesn't share culture with anyone (she has no [Culture] card), so Eldership's Brawl cancel never works. Easy swap.

**T19 — Alice:** Activates **Outriders**, drawing 3 from Claw: **Scavenge**, **Chiefdom**, **Worship of the Hunt**. She discards Scavenge as the weakest card — a [Mob] she doesn't want polluting her Domain. She keeps Chiefdom [Allegiance][Trophy] for its trophy tag and Mob-moving ability, and Worship of the Hunt [Spiritual] to pair with Worship of War for future Rite chains. Chiefdom conflicts with Eldership for the [Allegiance] slot, so Eldership is discarded — it was useless anyway since Alice has no [Culture] card and shares culture with nobody. *Building toward a Claw-depletion trophy strategy with Spiritual infrastructure for explosive Rite turns.*

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|3|Alice
MOVE|Alice|Scavenge|DISCARD
MOVE|Alice|Eldership|DISCARD
```

</details>

<details><summary>📋 Ops Trace (5 applied, 0 violations)</summary>

- ✅ DRAW claw → Scavenge → Alice's Domain
- ✅ DRAW claw → Chiefdom → Alice's Domain
- ✅ DRAW claw → Worship of the Hunt → Alice's Domain
- ✅ MOVE Scavenge Alice's Domain → Alice's discard
- ✅ MOVE Eldership Alice's Domain → Alice's discard

</details>

**T20 — Bob:** Activates **Pathfinding**. *With 4 [Knowledge] cards in Domain (Pathfinding, Sowing, Sowing, Withered Crop), Bob draws 4 from the top of the Tree pile, pulling Harvest, Harvest, Nomad, and the next card.* The first card drawn is **Harvest** — Drafted: triggers Harvest globally, then moves to discard. Fields currently have 7 cards, so no refill needed (7 minus 7 = 0). No On Harvest responders exist in any Domain, so Harvest does nothing. Second card is **Harvest** — Drafted again: triggers Harvest globally. Fields still at 7, no refill. No On Harvest responders. Moves to discard. Third card is **Nomad** — Drafted: Bob does not have a Pasture card… wait, Bob DOES have Pasture. Nomad stays in Domain. But Bob already has Highlander [Culture], and Domain holds max 1 [Culture]. Bob must discard the existing Highlander to keep Nomad, or discard Nomad. Highlander requires Crags (which Bob has), and Nomad requires Pasture (which Bob has). Bob keeps Highlander and discards Nomad — Highlander is already established and Crags-synergistic. Fourth card is the next in pile (position 4): Bob takes it to Domain. Checking tree pile — after the top 3 (Harvest, Harvest, Nomad), the 4th card needs to be identified. Since only top 3 are listed, I'll draw the 4th blind. Bob draws 1 more from Tree. *Pathfinding with 4 Knowledge is an enormous tempo swing — Bob cements his lead with massive Tree draws, accelerating Tree depletion toward his [Nature] victory condition (Pasture, Crags, Sacred Grove = 3 Nature tags).*

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|tree|1|Bob
DRAW_DISCARD|tree|1|Bob
DRAW|tree|1|Bob
MOVE|Bob|Nomad|DISCARD
DRAW|tree|1|Bob
```

</details>

<details><summary>📋 Ops Trace (5 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD tree → Harvest → Bob's discard
- ✅ DRAW_DISCARD tree → Harvest → Bob's discard
- ✅ DRAW tree → Nomad → Bob's Domain
- ✅ MOVE Nomad Bob's Domain → Bob's discard
- ✅ DRAW tree → Withered Crop → Bob's Domain

</details>

---

### === STATE AFTER TURN 20 ===

**Alice** (7 cards): Crags, Poach, Worship of War, Armament, Outriders, Chiefdom, Worship of the Hunt
  Discard: Gathering, Scavenge, Eldership
**Bob** (11 cards): Pathfinding, Forage, Crags, Highlander, Withered Crop, Solstice, Sowing, Sacred Grove, Pasture, Sowing, Withered Crop
  Discard: Regrowth, Harvest, Harvest, Nomad
**Charlie** (5 cards): Crags, Chiefdom, Oral Tradition, Warband, Duel
  Discard: Regrowth, Uprising

Season: Nomad
Fields (7): Feed the Commoners, Mill, Famine, Granary, Famine, Granary, Tavern
Piles: Claw 29, Tree 19, Wheat 10, Coin 5

---

Looking at Charlie's position: He has Chiefdom [Allegiance][Trophy], Warband, and Worship of War — a strong aggressive toolkit. But he needs to think about win conditions. Charlie has 1 [Trophy] (Chiefdom). Alice also has 1 [Trophy] (Chiefdom). If Claw depletes, it's a tie — not great. Tree depletion favors Bob massively (Crags, Pasture, Sacred Grove = 3 [Nature] vs Charlie's 1 Crags). Charlie should either race Claw and build more [Trophy], or attack Bob to strip [Nature] cards.

Charlie has Warband: "Activate — trigger Brawl in the Domain with the most cards." Bob has 11 cards — by far the most. Bob has 2x Crags — the On Brawl defense requires 2+ Crags AND the attacker to discard a card. Charlie can afford to discard something (Duel is dead weight). Bob has no Militia. This is the perfect time to Brawl Bob and slow down the Tree-depletion leader.

Brawl fires in Bob's Domain. Bob has 2 Crags → "On Brawl — if you have 2+ Crags, cancel the Brawl in your Domain unless the triggering player discards a card." Charlie discards Duel (dead card) to force through the Brawl. No other On Brawl responders in Bob's Domain. The Brawl resolves with no Mob cards in Bob's Domain, so no cards are forcibly given. However — Alice's Domain: Worship of War has no On Brawl text. Alice has no On Brawl cards. Charlie has no On Brawl cards either. 

Wait — Brawl in Bob's Domain with no [Mob] cards there means... nothing happens beyond the Crags check. Charlie pays Duel to push through, but Bob has no Raid/Scavenge/Marauders. The Brawl is empty. 

Better plan: Use **Chiefdom** to move a [Mob] card first... but Charlie has no Mob cards in his Domain. Poach is Alice's, not his.

Best alternative: Activate **Outriders**? No, that's Alice's. Activate **Oral Tradition** to draw from Candle — but Charlie has no Coin cards to discard as cost.

Charlie should activate **Chiefdom**: "Activate — move 1 [Mob] card from your Domain or any Domain that shares your culture to any other Domain." Charlie is Highlander-less but has Chiefdom. No culture sharing applies. He has no Mob cards himself. This does nothing.

Best move: Draw from Claw via Domain access — top card is Raid. Plant it in Bob's Domain later via Chiefdom (if culture matches) or Incite.

**T21 — Charlie:** Activates the **Claw zone**, drawing 2 cards: **Raid** and **Foray**. *Building up Mob ammunition to plant in Bob's massive Domain before triggering Warband — Bob is the biggest threat with 11 cards and a Nature-heavy build racing Tree depletion.* Raid and Foray are not Drafted, so both enter Charlie's Domain. Foray provides On Brawl insurance (draw 1 from Tree), and Raid is a [

## Round 8 (Turns 22–24)

**T22 — Alice:** Activates **Outriders** — draw 3 from Claw, discard 1. *Alice needs Mob cards to plant in opponents' Domains via Chiefdom, and Outriders is strictly better than the Claw zone.* She draws **Raid**, **Foray**, and **Racketeering**. Alice keeps Raid (plantable Mob) and Racketeering (powerful extortion tool), discarding Foray as the least useful — she'd rather attack than passively compensate from Brawls. Raid and Racketeering enter her Domain. No Drafted effects on any of these three cards. No events triggered.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|3|Alice
MOVE|Alice|Foray|DISCARD
```

</details>

<details><summary>📋 Ops Trace (4 applied, 0 violations)</summary>

- ✅ DRAW claw → Raid → Alice's Domain
- ✅ DRAW claw → Foray → Alice's Domain
- ✅ DRAW claw → Racketeering → Alice's Domain
- ✅ MOVE Foray Alice's Domain → Alice's discard

</details>

**T23 — Bob:** Activates **Pathfinding** to draw from the Tree pile. *With 4 [Knowledge] cards in Domain (Pathfinding, Sowing, Sowing, Withered Crop — wait, Withered Crop has no [Knowledge] tag, but Sowing ×2 + Pathfinding = 3 [Knowledge]), Bob draws 3 cards.* Top 3 of Tree: Gathering, Sky Dance, Highlander. **Gathering** is Drafted — Bob chooses to trigger Rite in his Domain (he has Sacred Grove [Spiritual] to respond). Sacred Grove responds to On Rite: the player who triggered the Rite (Bob) may activate all — actually, Sacred Grove has no "On Rite" text; it has "Activate — choose one: Trigger Rite / scry." No Spiritual "On Rite" cards exist in Bob's Domain. Rite resolves with no responders — no state change. Gathering moves to discard. **Sky Dance** enters Bob's Domain (not Drafted — stays). **Highlander** is Drafted — Bob already has a Highlander and a Crags, so Highlander can stay, but Bob already has Highlander [Culture] in Domain. Domain holds max 1 [Culture]. Bob must discard the existing Highlander to keep the new one, or discard the new one. Bob discards the new Highlander (keeping his existing one is equivalent). *Pathfinding with 3 [Knowledge] is a massive tempo engine — grabbing Sky Dance gives Bob a repeatable Rite trigger to pair with future Worship cards, and accelerating Tree depletion favors his [Nature] lead (Pasture, Crags, Sacred Grove = 3 [Nature] tags vs Alice's 0 and Charlie's 0).*

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|tree|1|Bob
DRAW|tree|1|Bob
DRAW_DISCARD|tree|1|Bob
```

</details>

<details><summary>📋 Ops Trace (3 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD tree → Gathering → Bob's discard
- ✅ DRAW tree → Sky Dance → Bob's Domain
- ✅ DRAW_DISCARD tree → Highlander → Bob's discard

</details>

Looking at the board state:

- **Charlie's position:** Has Warband, Chiefdom, and Oral Tradition but few scoring tags. Only 1 [Nature] (Crags), 0 [Trophy] (Chiefdom is [Allegiance][Trophy] — wait, yes Chiefdom IS [Trophy]). So Charlie has 1 [Trophy]. Alice has Chiefdom [Trophy] too. Bob is dominating [Nature] with Crags + Pasture + Sacred Grove (if [Nature]) + Worship of Fertility... wait, Bob has Crags, Pasture, Sacred Grove — that's 3 [Nature]. Bob wins Tree depletion easily.
- **Key threat:** Bob has 12 cards, Pathfinding + tons of Knowledge (Pathfinding, Sowing x2, Withered Crop x2, Sacred Grove... Pathfinding draws equal to [Knowledge] count). Bob is running away with the game.
- **Charlie's best play:** Alice has Raid in her own Domain and is the biggest Domain (9 cards). Charlie should activate **Warband** — trigger Brawl in the Domain with the most cards. That's Bob (12 cards). Alice's Raid is in Alice's Domain, not Bob's. But Bob has no Mob cards, so Brawl in Bob's domain... no On Brawl responders means Charlie gets nothing from it. Wait — Warband triggers Brawl, and [Mob] cards with "On Brawl" respond. Bob has no Mob cards.

Actually, Charlie should use **Chiefdom** to move Alice's Raid into Bob's Domain first — but Chiefdom says "from your Domain or any Domain that shares your culture." Charlie is Highlander? No, Charlie has no Culture card. Alice has no Culture card either. So Chiefdom can only move Mob from Charlie's own Domain. Charlie has no Mob cards.

Best play: Activate **Outriders**? Charlie doesn't have Outriders. Charlie should draw from Claw — top is Incite. Incite is Drafted: move up to 3 [Mob] cards from your Domain to any other Domain(s). Charlie has no Mob cards, so Incite does nothing useful but stays in Domain. Actually Incite has no "stays" text — it just says Drafted, doesn't say discard. So it stays. But it's dead with no Mob.

Better: Activate **Warband** targeting Bob (most cards, 12). Even with no Mob responders, Brawl still fires — but nothing happens. That's wasteful.

Best realistic play: Activate **Oral Tradition** — discard a Coin card to draw from Candle. Charlie has no Coin cards. Can't do that.

Charlie should draw from Claw to build up. Top card is Incite (Drafted — no Mob to move, stays in Domain as a future setup piece).

**T24 — Charlie:** Draws from the Claw zone, pulling **Incite** and **Racketeering**. *Building toward an offensive — Incite is a setup piece for future Mob planting, and Racketeering gives immediate extortion power.* Incite is Drafted: Charlie may move up to 3 [Mob] cards from their Domain to other Domains, but Charlie has no [Mob] cards currently — Incite resolves with no effect and stays in Domain.

## Round 9 (Turns 25–27)

Looking at the board state:

**Alice's position:** She has Chiefdom [Allegiance][Trophy], Worship of War [Spiritual], Worship of the Hunt [Spiritual], Raid [Mob] in her own Domain (bad — hurts her on Brawl), plus Racketeering, Outriders, Poach, Armament, Crags. No [Nature] tags, no [Amenity] tags. Her only win axis is [Trophy] via Claw depletion — she has 1 [Trophy] from Chiefdom. That's weak.

**Bob is the clear threat:** 12 cards in Domain, massive engine with Pathfinding + 2x Sowing + Sacred Grove + Sky Dance. He has Pasture, Crags, multiple [Nature] tags — he wins if Tree depletes. He also has Wheat access and can accelerate any pile.

**Key decision:** Alice needs to attack Bob. She has Chiefdom to move her own Raid into Bob's Domain, then she can use Worship of War (via a Rite trigger... but she has no Rite trigger card). Actually, she has no Sky Dance or Sacred Grove — she can't trigger Rite herself. She could use Racketeering to extort Bob or Charlie. She could use Outriders (draw 3 Claw, discard 1) to build up. 

**Best move:** Use Chiefdom to move Raid from Alice's Domain into Bob's Domain. This removes a liability from Alice (Raid hurts her on Brawl) and plants a [Mob] in Bob's Domain for a future Brawl. This sets up a devastating Racketeering or Warband play next turn against Bob.

**T25 — Alice:** Activates **Chiefdom** to move **Raid** from her Domain into Bob's Domain. *Planting Mob in Bob's massive Domain sets up a devastating Brawl or Racketeering play next turn — Raid in Bob's Domain means any Brawl there forces Bob to give Alice a card.* No events triggered.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Alice|Raid|DOMAIN|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Raid Alice's Domain → Bob's Domain

</details>

Looking at Bob's position: He has 13 cards in Domain including Pathfinding with 4 [Knowledge] cards (Pathfinding, Sowing, Sowing, Withered Crop... wait, let me count: Pathfinding [Knowledge], Sowing [Knowledge], Sowing [Knowledge], Withered Crop - no tag, Solstice - no tag, Sacred Grove [Spiritual], Sky Dance [Spiritual], Forage - no tag, Crags [Nature], Pasture [Nature], Highlander [Culture], Raid [Mob], Withered Crop - no tag). Knowledge cards: Pathfinding, Sowing, Sowing = 3 [Knowledge]. Pathfinding draws equal to [Knowledge] count = 3 cards from Tree.

Bob has 3 [Nature] tags (Crags, Pasture, Sacred Grove has [Nature]). Tree pile has 16 remaining. If Tree depletes, most [Nature] wins. Bob has strong Nature count. Drawing 3 from Tree accelerates Tree depletion AND builds his Domain. Top 3 Tree cards: Harvest, Herbalism, Pathfinding.

Harvest is Drafted → triggers Harvest → discard. Herbalism is [Knowledge] — would boost Pathfinding further. Pathfinding is [Knowledge] too. This is a massive snowball turn.

Harvest (Drafted): triggers Harvest event → Fields refill. Bob has Solstice (On Harvest) — choose to have all players of his culture draw 1 from Tree or place Culture card. Bob is Highlander culture. Alice/Charlie don't share it. So just Bob draws 1 from Tree. That's a 4th card from Tree this turn effectively.

**T26 — Bob:** Activates **Pathfinding**, drawing 3 cards from the Tree pile (3 [Knowledge] cards: Pathfinding, Sowing, Sowing). *With 3 Knowledge, Pathfinding pulls 3 Tree cards — snowballing toward Tree depletion while Bob leads in [Nature].* First card is **Harvest** (Drafted) — triggers Harvest globally, then discards. Fields refill from 7 to 7 (already full, no refill needed). Bob's **Solstice** responds On Harvest: Bob chooses all Highlander-culture players draw 1 from Tree — only Bob qualifies, drawing **Herbalism** (the next Tree card). Second card drawn is the original second: **Herbalism** [Knowledge]. Third card: **Pathfinding** [Knowledge] — but Bob already has Pathfinding, no restriction on duplicates, it stays. Bob's Domain grows enormously. Raid still sits awkwardly in his Domain.

<details><summary>🎯 Raw OPS</summary>

```
DRAW_DISCARD|tree|1|Bob
DRAW|tree|2|Bob
DRAW|tree|1|Bob
```

</details>

<details><summary>📋 Ops Trace (4 applied, 0 violations)</summary>

- ✅ DRAW_DISCARD tree → Harvest → Bob's discard
- ✅ DRAW tree → Herbalism → Bob's Domain
- ✅ DRAW tree → Pathfinding → Bob's Domain
- ✅ DRAW tree → Crags → Bob's Domain

</details>

Looking at the board state carefully:

**Charlie's position:** Has Chiefdom [Allegiance][Trophy], Crags, Warband, Oral Tradition, Duel. Only 1 [Trophy] tag (Chiefdom). Charlie has no [Nature] beyond Crags (1), and no [Amenity]. Charlie is behind on every win axis.

**Bob's position:** Bob has massive Domain (16 cards!) with Crags×3, Pasture = 4 [Nature] tags. Bob also has Pathfinding×2, Sowing×2 — he's been snowballing hard. If Tree depletes, Bob wins with 4 [Nature]. Bob also has Raid planted in his Domain.

**Alice's position:** Alice has Worship of War, Worship of the Hunt, Chiefdom, Poach, Outriders, Racketeering — aggressive build. 1 [Trophy] (Chiefdom). No [Nature], no [Amenity].

**Key insight:** Bob is the runaway leader with 4 [Nature] and would win a Tree depletion. Charlie needs to attack Bob. Charlie has Warband which triggers Brawl in the Domain with the most cards — that's Bob (16 cards). Bob has Raid in his Domain, which means On Brawl, Bob gives Charlie 1 card. Bob has 3 Crags — the Crags defense needs 2+ Crags AND the triggering player must discard a card. Charlie should be willing to pay that cost.

But wait — does Bob share Charlie's culture? Charlie has Chiefdom [Allegiance] but no [Culture] card. Bob has Highlander [Culture]. Since Charlie has no culture, the Eldership cultural check is irrelevant (Bob has no Eldership anyway).

Bob has 3 Crags → On Brawl defense: Charlie must discard a card or Brawl is cancelled. Charlie should discard Duel (dead card — no Warlords in play) to force the Brawl through. Then Raid triggers: Bob gives Charlie 1 card.

**T27 — Charlie:** Activates **Warband** to trigger Brawl in Bob's Domain (the largest with 16 cards). *Bob is the runaway leader with 4 [Nature] tags — must strip his Domain before Tree depletes.* Bob has 2+ Crags, so the Brawl is cancelled unless Charlie discards a card — Charlie discards **Duel** (dead card, no Warlords in play). Brawl proceeds. Bob's **Raid** responds: On Brawl, Bob must give 1 card to Charlie. Bob gives **Raid** itself (the worst card for Bob to keep, since it helps attackers). Charlie receives Raid. Charlie's Warband remains in Domain.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Duel|DISCARD
MOVE|Bob|Raid|DOMAIN|Charlie
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ MOVE Duel Charlie's Domain → Charlie's discard
- ✅ MOVE Raid Bob's Domain → Charlie's Domain

</details>

## Round 10 (Turns 28–30)

Looking at the board state:

- **Tree depletion** → most [Nature] wins. Bob has Crags×3 + Pasture = 4 [Nature]. Alice has Crags = 1. Bob wins Tree easily.
- **Claw depletion** → most [Trophy] wins. Alice has Chiefdom = 1 [Trophy]. Nobody else has any. Alice wins Claw.
- **Wheat depletion** → most [Amenity] wins. Nobody has any [Amenity] yet.

Alice's best path is racing Claw depletion (26 remaining — hard but she's the only one with [Trophy]) or stripping Bob's [Nature] via Brawl. Bob is the biggest threat with 4 [Nature] and 15 cards in Domain. Alice has Worship of War + Chiefdom to plant Mob then Brawl.

**Priority:** Use Chiefdom to move a Mob card into Bob's Domain to set up a devastating Brawl. Charlie has **Raid** in Domain — Alice can move that Raid into Bob's Domain via Chiefdom (Chiefdom says move 1 [Mob] from your Domain *or any Domain that shares your culture*). But Alice has no [Culture] card, so she can only move from her own Domain. Alice has **Poach** which is [Mob] — she can move Poach into Bob's Domain.

Actually, **Outriders** is strictly better tempo — draw 3 from Claw, discard 1. That accelerates Claw depletion AND builds Alice's hand. Top 3 Claw: Incite, Racketeering, Raid. Incite is Drafted — move up to 3 [Mob] from her Domain to Bob's. That's the dream: draw Outriders → get Incite → plant Poach into Bob's Domain, setting up Worship of War Brawl next turn.

**T28 — Alice:** Activates **Outriders** — draws 3 from Claw: **Incite**, **Racketeering**, **Raid**. *Outriders accelerates Claw depletion toward her [Trophy] win condition while fishing for Mob-planting tools.* Incite is Drafted — Alice moves **Poach** [Mob] and **Raid** (just drawn, also [Mob]) into Bob's Domain, weaponizing them for a future Brawl. She already has Racketeering, so she discards the duplicate Racketeering drawn this turn. Alice keeps Incite nowhere — it self-resolves and goes to discard.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|claw|3|Alice
MOVE|Alice|Poach|DOMAIN|Bob
MOVE|Alice|Raid|DOMAIN|Bob
MOVE|Alice|Incite|DISCARD
MOVE|Alice|Racketeering|DISCARD
```

</details>

<details><summary>📋 Ops Trace (7 applied, 0 violations)</summary>

- ✅ DRAW claw → Incite → Alice's Domain
- ✅ DRAW claw → Racketeering → Alice's Domain
- ✅ DRAW claw → Raid → Alice's Domain
- ✅ MOVE Poach Alice's Domain → Bob's Domain
- ✅ MOVE Raid Alice's Domain → Bob's Domain
- ✅ MOVE Incite Alice's Domain → Alice's discard
- ✅ MOVE Racketeering Alice's Domain → Alice's discard

</details>

Looking at the board state:

**Bob's position:** Massive Domain with 17 cards. He has 2 Pathfinding + 5 [Knowledge] cards (Pathfinding x2, Sowing x2, Herbalism) — activating Pathfinding draws 5 Tree cards. Tree pile has 12 remaining. Drawing 5 would bring it to 7. Bob has heavy [Nature]: Pasture, Crags x2 = 3 [Nature] tags, plus Sacred Grove = 4 [Nature]. If Tree depletes, Bob likely wins on [Nature].

But wait — Bob should be careful not to deplete Tree too fast if he can grow his [Nature] count more first. Actually, Bob already has 4 [Nature] (Pasture, Crags, Crags, Sacred Grove). Alice has 1 [Nature] (Crags). Charlie has 1 [Nature] (Crags). Bob is dominant on the Tree win axis.

Activating Pathfinding to draw 5 Tree cards accelerates Tree depletion massively (12→7 in pile, plus Season currently has 1 card). Top 3 are Pasture, Pasture, Pasture — that's even more [Nature] for Bob. This is the winning play: flood his Domain with [Nature] and race Tree to depletion.

Bob has 5 [Knowledge] cards: Pathfinding, Pathfinding, Sowing, Sowing, Herbalism. So Pathfinding draws 5.

Top 5 of Tree pile: Pasture, Pasture, Pasture, then cards 4-5 unknown. He takes all 5 to Domain.

**T29 — Bob:** Activates **Pathfinding** to draw the top 5 cards from the Tree pile, pulling **Pasture**, **Pasture**, **Pasture**, and 2 more cards deep into his Domain. *With 5 [Knowledge] cards and a dominant [Nature] lead, racing Tree depletion is the clear path to victory — three more Pastures cement an unassailable lead.* Tree pile drops from 12 to 7. Bob's [Nature] count surges to 7.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|5|Bob
```

</details>

<details><summary>📋 Ops Trace (5 applied, 0 violations)</summary>

- ✅ DRAW tree → Pasture → Bob's Domain
- ✅ DRAW tree → Pasture → Bob's Domain
- ✅ DRAW tree → Pasture → Bob's Domain
- ✅ DRAW tree → Nomad → Bob's Domain
- ✅ DRAW tree → Harvest → Bob's Domain

</details>

Looking at the board state:

- **Bob** has a massive Domain (22 cards!) with tons of [Nature] tags (Pasture×4, Crags, Sacred Grove, Pasture... at least 7+ [Nature]). If Tree depletes, Bob wins easily.
- Tree pile has only 7 remaining + 1 in Season = 8 total. Bob could race this.
- Charlie has Warband + Raid in Domain, and Chiefdom to move Mob. Charlie needs to attack Bob to strip [Nature] cards, or pivot strategy.

Charlie's best play: **Activate Chiefdom** to move Raid from Charlie's Domain into Bob's Domain. Bob already has 1 Raid — adding another makes a future Warband Brawl devastating. Charlie shares Highlander culture with Bob (both have Crags), but Chiefdom says "your Domain or any Domain that shares your culture" — Charlie has Chiefdom [Allegiance] and Crags, but no [Culture] card. Charlie's culture is undefined (no Culture card). Bob has both Highlander and Nomad... but Domain holds max 1 [Culture]. Wait — Bob has both Highlander AND Nomad in Domain. That violates the 1 [Culture] rule. Regardless, Charlie has NO culture card, so Charlie doesn't share culture with anyone.

Chiefdom: "move 1 [Mob] card from your Domain **or any Domain that shares your culture** to any other Domain." Charlie can move from own Domain regardless. Move Raid from Charlie's Domain to Bob's Domain — this plants a second Mob in Bob's massive Domain. Next turn, Charlie can activate Warband to trigger Brawl in Bob's Domain (most cards), and both Raids will force Bob to give Charlie 2 cards.

This is the optimal aggressive setup play.

**T30 — Charlie:** Activates **Chiefdom** to move **Raid** from his own Domain into Bob's Domain. *Bob's 22-card Domain is the biggest threat — planting a second Raid sets up a devastating Warband Brawl next turn that would strip two cards from Bob.* No events triggered; Raid simply relocates to Bob's Domain alongside the Raid already there.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Raid|DOMAIN|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Raid Charlie's Domain → Bob's Domain

</details>

---

### === STATE AFTER TURN 30 ===

**Alice** (7 cards): Crags, Worship of War, Armament, Outriders, Chiefdom, Worship of the Hunt, Racketeering
  Discard: Gathering, Scavenge, Eldership, Foray, Incite, Racketeering
**Bob** (23 cards): Pathfinding, Forage, Crags, Highlander, Withered Crop, Solstice, Sowing, Sacred Grove, Pasture, Sowing, Withered Crop, Sky Dance, Herbalism, Pathfinding, Crags, Poach, Raid, Pasture, Pasture, Pasture, Nomad, Harvest, Raid
  Discard: Regrowth, Harvest, Harvest, Nomad, Gathering, Highlander, Harvest
**Charlie** (4 cards): Crags, Chiefdom, Oral Tradition, Warband
  Discard: Regrowth, Uprising, Duel

Season: Nomad
Fields (7): Feed the Commoners, Mill, Famine, Granary, Famine, Granary, Tavern
Piles: Claw 23, Tree 7, Wheat 10, Coin 5

---

## Round 11 (Turns 31–33)

Looking at the board state:

- **Bob** has a massive Domain (23 cards!) with tons of [Nature] tags (Pasture ×4, Crags ×2, Sacred Grove, Worship of Fertility... wait, no Worship of Fertility, but Pasture ×4, Crags ×2 = 6 [Nature] minimum). If Tree depletes, Bob wins easily.
- **Tree pile has only 7 cards** + 1 Season card = 8 total Tree cards left. This is dangerously close to depletion, and Bob has Pathfinding ×2 which can drain it fast.
- Alice has 0 [Nature] tags (Crags has [Nature] — actually Crags IS [Nature][Land]). So Alice has 1 [Nature] from Crags. Bob has ~6+ [Nature]. Alice cannot win a Tree depletion.
- Alice has Chiefdom [Trophy] — only 1 [Trophy]. Claw pile has 23 cards, far from depletion.
- Alice needs to **attack Bob** to strip his Domain before Tree depletes, or slow Tree depletion.

Alice has **Racketeering** — target Bob. Bob must offer a card. If Alice refuses, Brawl fires in Bob's Domain where Bob has Raid ×2 (each gives Alice a card on Brawl). This is extremely powerful: refuse the offer → Brawl → Raid ×2 triggers → Bob gives Alice 2 cards. Bob also has Poach [Mob] which doesn't trigger on Brawl. But Bob has no Brawl defense (Eldership is in Alice's discard, Militia isn't present, Bob's Crags ×2... wait: "On Brawl — if you have 2+ Crags, cancel the Brawl in your Domain unless the triggering player discards a card." Bob HAS 2+ Crags (Crags, Crags). So Alice must discard a card to push through the Brawl.

Best play: Activate **Racketeering** targeting Bob. Bob (playing to minimize damage) offers his weakest card — likely Raid (getting rid of his own vulnerability). Alice should **refuse** the offer to trigger Brawl instead, since Bob has 2 Raids + Scavenge-like cards. But Bob's 2+ Crags means Alice must discard a card. Alice discards **Armament** (dead card, no Sword deck/Coin cards). Then Brawl fires: Raid ×2 each force Bob to give Alice 1 card. Bob gives his two worst cards. Bob chooses to give Raid and Raid (removing his own vulnerabilities).

**T31 — Alice:** Activates **Racketeering**, targeting Bob. *Bob's massive Domain threatens a Tree-depletion victory; need to strip his cards aggressively.* Bob offers **Harvest** (his least useful card with Drafted text that self-discards). Alice refuses — triggering Brawl in Bob's Domain. Bob has 2+ Crags, so Alice must discard a card to proceed; she discards **Armament** (dead weight). Brawl resolves: Bob's two **Raid** cards respond — Bob must give Alice 2 cards. Bob gives Raid and Raid (removing his own liabilities, minimizing Alice's gain).

OPS:

Looking at the board state carefully:

**Bob's position:** Massive Domain with 23 cards. He has 4 Pastures, 3 Crags = 7 [Nature] tags (Pasture×4 + Crags×3). He also has Sacred Grove, Worship of Fertility... wait, no Worship of Fertility. He has Poach, 2 Raids, 2 Pathfindings, 2 Sowings, 2 Withered Crops, Sky Dance, Herbalism, Solstice, Forage, Highlander, Nomad, Harvest.

**Win condition analysis:** Tree pile has 7 remaining + 1 in Season = 8 total Tree cards left. If Tree depletes, most [Nature] wins. Bob has 7 [Nature] (4 Pasture + 3 Crags). Alice has 1 Crags = 1 [Nature]. Charlie has 1 Crags = 1 [Nature]. Bob is massively ahead on [Nature].

**Bob should race Tree depletion.** He has 2 Pathfinding cards and tons of [Knowledge] (Pathfinding×2, Sowing×2, Herbalism, Solstice = 6 [Knowledge]). Activating Pathfinding draws 6 Tree cards, leaving only 1 in the pile (7-6=1) plus the Season would need refilling. This would nearly end the game.

But wait — Bob has 2 Pathfindings. He can only activate ONE card per turn. Activating one Pathfinding draws cards equal to [Knowledge] count. Let me count [Knowledge]: Pathfinding, Pathfinding, Sowing, Sowing, Herbalism, Solstice = 6 [Knowledge]. So he draws 6 from Tree pile (which has 7). That leaves 1 in the pile. Season has Nomad (1 card). After drawing 6, the pile has 1 left, Season still has Nomad. Very close to ending.

Many of these drawn Tree cards will add more [Nature] to Bob's domain too. Let's check the top cards: Sowing, Withered Crop, Forage, then 4 more unknown. He draws 6.

**T32 — Bob:** Activates **Pathfinding** to draw 6 cards from the Tree pile. *With 6 [Knowledge] cards, this nearly depletes Tree — and Bob holds a commanding 7+ [Nature] lead to win that axis.* Bob draws: Sowing, Withered Crop, Forage, and 3 more from the pile. Sowing and Withered Crop have no Drafted effects. Forage has no Drafted effect. The remaining 3 cards are drawn normally. After this, only 1 card remains in the Tree pile. Season has 1 card (Nomad). The game is one turn from ending.

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|6|Bob
```

</details>

<details><summary>📋 Ops Trace (6 applied, 0 violations)</summary>

- ✅ DRAW tree → Sowing → Bob's Domain
- ✅ DRAW tree → Withered Crop → Bob's Domain
- ✅ DRAW tree → Forage → Bob's Domain
- ✅ DRAW tree → Solstice → Bob's Domain
- ✅ DRAW tree → Worship of the Rain → Bob's Domain
- ✅ DRAW tree → Worship of Fertility → Bob's Domain

</details>

**T33 — Charlie:** Activates **Warband** — triggers Brawl in Bob's Domain (the Domain with the most cards at 29). *Bob's massive Domain is the biggest threat; time to strip him before Tree depletes.* Bob has 2 **Raid** cards responding to the Brawl: each forces Bob to give 1 card to Charlie (the triggering player). Bob also has 3+ **Crags**, so his On Brawl defense triggers — Charlie must discard a card to proceed. Charlie discards **Warband** (already used). Bob gives Charlie 2 cards from his Domain — Bob chooses to give **Raid** and **Raid** (his worst cards). Charlie receives both Raids into his Domain.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Warband|DISCARD
MOVE|Bob|Raid|DOMAIN|Charlie
MOVE|Bob|Raid|DOMAIN|Charlie
```

</details>

<details><summary>📋 Ops Trace (3 applied, 0 violations)</summary>

- ✅ MOVE Warband Charlie's Domain → Charlie's discard
- ✅ MOVE Raid Bob's Domain → Charlie's Domain
- ✅ MOVE Raid Bob's Domain → Charlie's Domain

</details>

## Round 12 (Turns 34–36)

**T34 — Alice:** Activates **Racketeering**, targeting Bob. *Bob's Domain is enormous with 27 cards — he's the runaway leader on [Nature] and would win if Tree depletes (only 1 card left in the Tree pile). Racketeering is Alice's best tool to strip a key card.* Bob, forced to offer a card, offers **Withered Crop** (his least valuable card — he has three copies and multiple other Wheat access cards). Alice refuses the offer and triggers **Brawl in Bob's Domain** instead, hoping to extract more value. Brawl fires in Bob's Domain — scanning for On Brawl responders: Bob has no [Mob] cards and no Brawl defense cards (no Militia, no Eldership — Eldership is in Alice's discard). Bob's Crags On Brawl: Bob has 3 Crags, so the Brawl is cancelled unless Alice discards a card. Alice discards **Armament** (dead card — no Sword deck in game) to force the Brawl through. However, with no [Mob] cards in Bob's Domain, the Brawl resolves with no On Brawl effects giving cards to Alice. The Brawl does nothing further. Alice's Foray is in her discard so no draw. Net result: Alice loses Armament but the Brawl had no Mob responders in Bob's Domain — a painful miss, but Racketeering itself stays in Alice's Domain for future use.

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Alice|Armament|DISCARD
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Armament Alice's Domain → Alice's discard

</details>

**T35 — Bob:** Activates **Pathfinding**. *With 6 [Knowledge] cards in Domain (Pathfinding ×2, Sowing ×3, Herbalism... wait — let me count: Pathfinding, Pathfinding, Sowing, Sowing, Sowing, Withered Crop, Withered Crop, Withered Crop, Herbalism = 9 [Knowledge] cards, but only 1 card remains in the Tree pile.* Bob activates Pathfinding, which draws top cards from the Tree pile equal to his number of [Knowledge] cards. He has 9 [Knowledge] cards (Pathfinding ×2, Sowing ×3, Withered Crop ×3, Herbalism), but only 1 card remains in the Tree pile — so he draws just 1: **Highlander**. Highlander is Drafted — Bob must have a Crags card in his Domain to keep it (he has 2 Crags), so it stays. Bob already has Nomad as his [Culture] card, so gaining Highlander [Culture] means he must discard one. Bob discards Nomad to keep Highlander (Highlander is [Culture]). The Tree pile is now empty, but the Season still has 1 card (Nomad), so the Tree deck is not yet fully depleted — the game continues. *Bob draws the last Tree pile card to edge closer to ending on Tree depletion, where his massive 7 [Nature] cards (Pasture ×4, Crags ×2, Worship of Fertility) would win.*

<details><summary>🎯 Raw OPS</summary>

```
DRAW|tree|1|Bob
MOVE|Bob|Nomad|DISCARD
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ DRAW tree → Highlander → Bob's Domain
- ✅ MOVE Nomad Bob's Domain → Bob's discard

</details>

**T36 — Charlie:** Activates **Chiefdom** to move **Raid** from his Domain to Bob's Domain. *Bob has the largest Domain by far and is running away with [Nature] tags; planting Mob in his Domain sets up future Brawl attacks to strip his cards before the game ends.* Charlie picks one of his two Raids and sends it to Bob. Chiefdom allows moving 1 [Mob] card from your Domain to any other Domain — no shared culture required since it also says "or any Domain."

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Charlie|Raid|DOMAIN|Bob
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Raid Charlie's Domain → Bob's Domain

</details>

## Round 13 (Turns 37–39)

**T37 — Alice:** Activates **Racketeering**, targeting Bob. *Bob's Domain is enormous and he's running away with [Nature] for a Tree victory — but the Tree pile is already empty, so the game could end any moment if the last Season card is taken. Alice needs to strip Bob's Nature cards or pivot hard.* Bob is forced to offer a card. Bob, playing to minimize damage, offers **Raid** (a [Mob] card that hurts him in Brawls and has no value to him). Alice evaluates: taking Raid gives her nothing useful, and refusing triggers Brawl in Bob's Domain — where Bob has 28 cards (the most by far) and that single Raid would force Bob to give Alice a card on Brawl. Alice refuses the offer and triggers Brawl in Bob's Domain. Brawl fires in Bob's Domain: Bob's **Raid** responds — "On Brawl, this Domain's owner gives 1 card to the player that triggered the Brawl." Bob must give Alice 1 card. Bob gives away **Solstice** (no tags Alice can exploit, and Bob has a duplicate). No other On Brawl responders fire. Alice's Worship of War and Worship of the Hunt don't respond (they're On Rite, not On Brawl). *Alice takes a card from the biggest threat rather than accepting the worthless Raid.*

<details><summary>🎯 Raw OPS</summary>

```
MOVE|Bob|Solstice|DOMAIN|Alice
```

</details>

<details><summary>📋 Ops Trace (1 applied, 0 violations)</summary>

- ✅ MOVE Solstice Bob's Domain → Alice's Domain

</details>

**T38 — Bob:** Activates **Pathfinding**. *With 6 [Knowledge] cards in Domain (Pathfinding ×2, Sowing ×3, Herbalism... wait, let me count: Pathfinding, Sowing, Sowing, Sowing, Herbalism, Pathfinding = 6 [Knowledge]), Bob would draw 6 from Tree — but the Tree pile is EMPTY and the Season has only 1 card (Nomad). The Tree pile is empty. This means the game ends NOW if we consider the pile depleted. But the rule says "when any deck's draw pile is emptied" — the Tree pile is already empty. Actually, the game should have ended when the Tree pile was emptied previously. Let me reconsider.* The Tree pile is empty but the Season still has 1 card (Nomad), so the pile being empty triggers end-of-game. Actually, re-reading: "When any deck's draw pile is fully emptied, the game ends." The Tree draw pile IS empty (0 remaining). The game should already be over. But since we're still playing, the Season card remains available. Bob instead activates **Sky Dance** to trigger Rite in his Domain. Sacred Grove [Spiritual], Worship of the Rain [Spiritual], Worship of Fertility [Spiritual] all respond. Worship of Fertility: triggers Harvest in Bob's Domain → Bob's Harvest (Drafted says move to discard but it's already in Domain as a card) — actually Harvest in Domain has no "On Harvest" text, it's Drafted only. Solstice responds to Harvest: Bob chooses all players of his culture draw 1 from Tree — but Tree pile is empty, so instead he places a [Culture] card from discard into any player's Domain. No useful target. Worship of the Rain: Bob discards Nomad from Season and replaces with top of Tree pile — but Tree pile is empty, so this fizzles. Fields refill to 7 on Harvest (already 7, no refill needed). Bob's Plough? He has no Plough. No On Harvest responders besides Solstice. Worship of the Flame is not in play. *Bob triggers Rite to chain into Harvest via Worship of Fertility, using Solstice to place a Culture card on Charlie to disrupt his Allegiance slot — but more importantly, he's racing Tree depletion where he leads massively in [Nature] tags.* Bob has enormous [Nature]: Pasture ×4, Crags ×2, Worship of Fertility, Sacred Grove = 8 [Nature]. The Tree pile is empty — if the game ends on Tree depletion, Bob wins. Since Tree pile is already at 0, the game is effectively over with Bob winning on [Nature].

<details><summary>🎯 Raw OPS</summary>

```
TAKE_SEASON_DISCARD|Nomad|Bob
REFILL_FIELDS|0
```

</details>

<details><summary>📋 Ops Trace (2 applied, 0 violations)</summary>

- ✅ TAKE_SEASON_DISCARD Nomad → Bob's discard
- 🏁 GAME OVER — tree zone fully depleted!

</details>

### GAME ENDS — tree zone fully depleted!

---

## Epilogue

**Alice** — 7 cards
  Domain: Crags, Worship of War, Outriders, Chiefdom, Worship of the Hunt, Racketeering, Solstice
  Tags: [Allegiance]×1, [Discontent]×1, [Land]×1, [Nature]×1, [Spiritual]×2

**Bob** — 27 cards
  Domain: Pathfinding, Forage, Crags, Highlander, Withered Crop, Sowing, Sacred Grove, Pasture, Sowing, Withered Crop, Sky Dance, Herbalism, Pathfinding, Crags, Poach, Pasture, Pasture, Pasture, Harvest, Sowing, Withered Crop, Forage, Solstice, Worship of the Rain, Worship of Fertility, Highlander, Raid
  Tags: [Culture]×2, [Discontent]×2, [Hunt]×1, [Knowledge]×6, [Land]×6, [Nature]×8, [Rabble]×2, [Spiritual]×4, [Unit]×2

**Charlie** — 4 cards
  Domain: Crags, Chiefdom, Oral Tradition, Raid
  Tags: [Allegiance]×1, [Discontent]×1, [Knowledge]×1, [Land]×1, [Nature]×1, [Rabble]×1, [Unit]×1

### Winner

🌳 Tree depleted — most [Nature] wins

- **Alice**: 1 [Nature]
- **Bob**: 8 [Nature] 👑
- **Charlie**: 1 [Nature]

**B wins!**

### Stats
API calls: 38 | Piles: Claw 23, Tree 0, Wheat 10, Coin 5, Candle 1
