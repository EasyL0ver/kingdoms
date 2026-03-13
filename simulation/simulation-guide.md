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
- [ ] Target turn count decided (30–40 for 3 players)

---

## State Tracking

### Per player

| Field | Description |
|-------|-------------|
| **Domain** | Cards in play (ordered list) |
| **Discard** | Cards discarded from this player |
| **Access** | Which zones they can activate (starts: Claw, Tree) |

### Global

| Field | Description |
|-------|-------------|
| **Season** | Current face-up Tree cards |
| **Fields** | Current face-up Wheat cards (refill on Harvest only) |
| **Pile pointers** | Next card index for each blind-draw pile |

After every turn, write out the full state. Format:

```
- Alice: Card1, Card2, Card3
- Bob: Card1, Card2
- Charlie: *(empty)*
- Season: X, Y, Z, W
- Fields: A, B, C
```

### Snapshot (every 5 rounds)

```
=== STATE AFTER ROUND [n] ===
DOMAINS:
  Alice:   [cards]
  Bob:     [cards]
  Charlie: [cards]
DISCARDS:
  Alice:   [cards]
  Bob:     [cards]
  Charlie: [cards]
SEASON: [cards]  |  FIELDS: [cards]
Piles remaining: Claw [n], Tree [n], Wheat [n]
OBSERVATIONS:
  - [what's working / broken / emerging]
```

---

## Turn Resolution

For each turn, resolve in this order:

```
TURN [N] — [Player Name]

1. DECISION: What does the player activate? (one action per turn)
   - Draw from a zone (Season/Fields/Claw/Coin/Candle)
   - Activate a card already in Domain

2. Drafted: If the card drawn is Drafted, resolve now
   - Check conditions (e.g., "discard a Pasture or discard this card")
   - Apply effect, move to discard if specified

3. EVENT CHAINS: If an event is triggered:
   a. Announce the event
   b. Scan relevant Domains for "On [Event]" cards
   c. Resolve each responding card
   d. Check if responses trigger further events (chain reactions)

4. ZONE REFILL: Season refills when empty (4 new cards).
   Fields refill on Harvest only.

5. STATE UPDATE: Write out all Domains
```

### Turn Log Format

```
TURN [n] — [Player]:
  Action: [Activates X / Draws from Y]
  Result: [card drawn, Drafted effects]
  Chain: [events triggered → responses → results]
  Domain: [all cards]
  Discard: [if changed]
  Notes: [reasoning or narrative]
```

---

## AI Decision-Making

### Phase priorities

**Early game (turns 1–9):**
1. Grab [Nature][Land] cards from Season (Pasture, Crags)
2. Pick up [Culture] cards if you have matching Land
3. Get Sowing or Withered Crop to unlock Wheat
4. Forage to dig through Tree deck
5. Avoid Claw draws — too early for combat

**Mid game (turns 10–24):**
1. Unlock Wheat → economy cards (Mill, Animal Husbandry, Granary)
2. Build On Feast / On Harvest infrastructure (Tavern, Plough)
3. Start drawing from Claw for Warband, Poach
4. Worship cards become high-value (On Rite compounds)
5. Sacred Grove / Sky Dance for Rite engines

**Late game (turns 25+):**
1. Incite: plant Mob in enemy Domains, then Brawl them
2. Warband: trigger Brawl in biggest Domain
3. Racketeering: extort weaker players
4. Feast combos: Granary → Feast → Tavern purges Discontent
5. Rite chains: stack Worship cards for compound effects

### Decision priority (any turn)

1. **Urgent response** — [Mob] in my Domain, deal with it
2. **Score opportunity** — profitable event chain available now
3. **Build infrastructure** — draw cards that unlock future access
4. **Deny opponents** — take a Season/Fields card they need
5. **Scout** — Crags/Forage to gather information

### Scoring heuristic

| Action | Base | Modifiers |
|--------|------|-----------|
| Draw Land (Pasture/Crags) | 10 | +2 first land, -2 if 3+ already |
| Draw Culture (matching) | 8 | -5 if no matching Land |
| Unlock Wheat (Sowing/WC) | 8 | -3 if already unlocked |
| Activate Warband | 8 | +N (target's domain size) |
| Draw Harvest (Drafted) | 7 | +2 if On Harvest cards exist |
| Activate Rite trigger | 6 | +2 per Worship card in play |
| Activate Feast trigger | 6 | +2 per On Feast card you have |
| Draw from Claw | 5 | +2 after turn 9 |
| Activate Forage | 5 | always decent |

Add ±1-2 random variance to prevent predictable play.

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
- **Feast defense:** Tavern + Granary counters planted Mob
- **Arms race:** Mutual Warband draws create cold war tension

### Epilogue

Summarize each player's final domain, tag distribution, strategic identity, key moment, and unresolved threats.

---

## Scenario Seeds

### "First Blood" — Brawl
Stack Claw: first 3 draws are Raid, Raid, Warband. Forces early combat.

### "Harvest Festival" — Food Chain
Stack Tree: Harvest in round 2. Plough and Tavern in Fields. Tests Feast cascades.

### "Culture Clash" — Culture Mechanics
Stack Tree: Pasture and Crags alternating, Nomad and Highlander near top.

### "The Long Peace" — Economy
No Warband/Raid in first 10 Claw cards. Tests Wheat/Coin progression without combat.

### "Holy War" — Religion
Sacred Grove, Sky Dance, Worship cards near top. Tests Rite chains and Flame scaling.

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

---

## Logging Conventions

- Card names in **bold** on first mention per turn
- Events marked with → arrows for chain reactions
- Design observations: 🔴 problem, 🟡 concern, 🟢 working well
- End each simulation with findings summary and suggested changes
