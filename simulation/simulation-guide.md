# Kingdoms — Simulation Guide

How to run turn-by-turn simulations for playtesting. For card texts see **game-cards.md**.

---

## Using the Draw Script

```powershell
cd simulation
. .\draw.ps1
```

Shuffles all decks and shows card counts. Commands:

```powershell
Show-Season          # See the 4 face-up Tree cards
Show-Fields          # See the face-up Wheat cards
Draw-Card tree       # Take from Season (top card)
Draw-Card claw       # Draw blind from Claw
Draw-Card wheat      # Take from Fields (top card)
Draw-Card coin       # Draw from Coin
Show-Deck claw       # See remaining cards in a pile
Reset-Decks          # Reshuffle everything
```

- Season/Fields are face-up — use `Show-` to see them, `Draw-Card` to take
- Claw is blind — no peeking
- Log your game — copy output into a new .md file in this folder

---

## Setup

```
PLAYERS: [names, count]
STARTING ACCESS: Claw, Tree (default)

SEASON (Tree face-up, 4 cards): [list]
FIELDS (Wheat face-up, 7 cards): [list]
CLAW PILE (shuffled): [list or count]
TREE PILE (remaining after Season): [list or count]
WHEAT PILE (remaining after Fields): [list or count]
```

Shuffle randomly or seed intentionally to test specific scenarios.

### Checklist

- [ ] All decks built with correct card counts
- [ ] Decks shuffled with recorded order
- [ ] Season (4 face-up Tree) and Fields (7 face-up Wheat) set
- [ ] Player access rights noted (everyone starts with Claw + Tree)
- [ ] State tracking ready
- [ ] Target turn count decided (50–60 for 3 players)

---

## Turn Resolution

For each turn, resolve in this order:

1. **Decision:** What does the player activate? (one action per turn)
   - Take from Season (Tree zone) or draw blind from Claw
   - Activate a card already in Domain
   - Activate a gateway-locked zone (Wheat, Coin, Candle) if you have access

2. **Drafted:** If the card drawn has Drafted text, resolve now
   - Check conditions (e.g., "discard a Pasture or discard this card")
   - Apply effect, move to discard if specified

3. **Event chains:** If an event is triggered:
   a. Announce the event
   b. Scan relevant Domains for "On [Event]" cards
   c. Resolve each responding card
   d. Check if responses trigger further events (chain reactions)

4. **Zone refill:** Season refills when empty (4 new cards).
   Fields refill on Harvest only.

---

## AI Decision-Making

### Decision priority (any turn)

1. **Urgent response** — [Mob] in my Domain, deal with it
2. **Pick up strong cards** — grab high-value cards from Season, Fields, or Claw that fit your strategy or carry winning tags. Season and Fields are precise (you see what you get), Claw is blind but powerful — two cards at once with high upside and risk.
3. **Score opportunity** — profitable event chain available now
4. **Build infrastructure** — draw cards that unlock future access
5. **Deny opponents** — take a Season/Fields card they need
6. **Recover from discard** — activate a card from discard if prerequisites are now met
7. **Scout** — Crags/Forage to gather information

### Event payoff rule

**Never trigger an event without a concrete payoff.** Activating a card that triggers Brawl, Rite, Feast, or Harvest is a wasted turn if nothing meaningful responds:

- **Brawl** is only worth triggering if the target Domain has [Mob] cards (Raid, Scavenge, Marauders) that will fire On Brawl effects. Without Mob, Brawl does nothing — a completely wasted turn.
- **Rite** is only worth triggering if On Rite responders will produce a tangible effect for YOU (the triggering player). Worship of Fertility chains into Harvest, but Harvest on full Fields with no On Harvest cards in play does nothing — don't trigger Rite just because you can.
- **Feast** is only worth triggering if you have On Feast responders (Tavern, Share the Spoils, Marauders) that will actually fire.
- **Harvest** is primarily about triggering On Harvest effects on Wheat cards (Plough, Solstice), not about refilling Fields.

If no responders exist, spend your turn drawing cards or building infrastructure instead.

### Event targeting

Think about WHERE an event fires and WHO benefits:

- **Rite** — ALL Worship cards (On Rite) benefit the **triggering player**, NOT the Worship card owner. If Bob holds Worship of War and Alice triggers Rite, *Alice* gets to Brawl — Bob's card is exploited against him. This means: trigger Rite when opponents hold useful Worship cards to steal their effects. Conversely, holding Worship cards when opponents trigger Rite more than you is a liability.
- **Brawl** — On Brawl cards split into offensive and defensive. **Offensive Mob** (Raid, Scavenge) fire in the targeted Domain and benefit the *attacker* — plant these in enemy Domains via Incite/Chiefdom. **Defensive** cards (Crags, Militia, Eldership) fire in your *own* Domain and protect you. **Payoff** cards like Foray give YOU a benefit when Brawl fires in your Domain — if you hold Foray, triggering Brawl on yourself is a valid play for the free Tree draw.
- **Feast** in YOUR Domain feeds your On Feast cards (Tavern, Share the Spoils). Don't trigger Feast if opponents have more On Feast responders than you.
- **Harvest** is global — all On Harvest cards everywhere respond. Consider whether opponents' On Harvest cards (Plough, Solstice) outweigh yours before triggering.

---

## Narrative

### When to add flavour

- Round starts (every 3 turns): brief scene-setting
- First Brawl, first Rite chain reaction
- Betrayal moments (Incite, Racketeering)
- Dramatic comebacks
- Final state summary

### Story hooks to watch for

- **Geography → Culture:** Crags vs Pasture determines Highlander vs Nomad
- **Spiritual kingmaker:** Worship of Fertility benefits everyone who triggers Rites
- **Mob infiltration:** Incite → Brawl combos are the dramatic peak
- **Feast loops:** Tavern purges Discontent on Feast, Share the Spoils draws on Feast
- **Arms race:** Mutual Warband draws create cold war tension

### Epilogue

Summarize each player's final domain, tag distribution, strategic identity, key moment, and unresolved threats.

---

## What to Watch For

**Red flags:** Dead cards (never activated), dominant cards (always best), game-locking combos, empty turns, Fields empty too long, no Brawls for 10+ turns.

**Good signs:** Genuine dilemmas, surprising chain reactions, organic culture alliances, multiple viable strategies, narrative from mechanics.

---

## Common Mistakes

1. **Auto-refilling Fields** — Fields only refill on Harvest, not when cards are taken
2. **Mob ownership in Brawl** — they fight for the attacker, not the domain owner
3. **Drafted cards staying in Domain** — Harvest, Gathering, etc. discard themselves
4. **Rite benefit direction** — benefits go to whoever *triggered* the Rite, not the Worship card owner
5. **Crags defense cost** — attacker must discard, not the defender
6. **Missing event chains** — On Rite can trigger Harvest → On Harvest → Feast... follow the full chain


