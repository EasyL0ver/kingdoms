# Kingdoms — Game Rules

> **Status:** Early design — card counts, specific effects, and scoring are TBD.

---

## 0. The Golden Rule

**If it's not on a card, it's not a rule.**

Everything in this game — zones, actions, permissions, effects — lives on the cards. This document explains how to read them.

---

## 1. Setup

1. **Place zone cards** for each deck, face-up next to their shuffled draw piles.
2. Each player starts with their **Domain** (an empty personal zone in front of them) and a **Presence** card in it.

---

## 2. How to Play

1. Players take turns clockwise.
2. **On your turn: Dawn.** Dawn fires in your Domain. All your cards with `On Dawn` text respond — you choose the order.
3. Negotiate freely with any player at any time.
4. When any deck's draw pile is emptied, the game ends.

That's it. Everything else is on the cards.

---

## 3. Core Concepts

### The Event System

All card text uses one pattern: **`On [Event] — effect`**.

There are no other keywords to learn. Every card tells you when it fires and what it does.

**Events:** Dawn, Order, Brawl, Rite, Feast, Harvest, Rumour.

### Event Scope

Events fire in a specific place. Card text always says where:

- **"on"** targets one card — e.g. "Order on the Claw zone"
- **"in"** broadcasts to a zone — e.g. "Brawl in the largest Domain"

When an event fires **in** a zone, every card there with a matching `On [Event]` responds.

### Dawn & Order

**Dawn** is the root event. It fires in your Domain at the start of your turn. Your `On Dawn` cards respond.

**Order** targets a specific card. Your starting Presence card says `On Dawn — Order on the Claw zone, the Tree zone, or a card in your Domain`. When you Order a card, its `On Order` text fires.

For example, to draw from the Tree deck:
1. Your turn begins — **Dawn** in your Domain
2. Your **Presence** responds — you may Order on a zone or a card in your Domain
3. You Order on the **Tree zone** → its `On Order` text says "take 1 card from the Season"

### The Active Player

Whenever card text needs to reference who is driving an event, it says **"the active player"** — the player whose turn it is.

### Zones

A **zone** is any place that holds cards. There are two kinds:

- **Domains** — each player's personal zone. Your cards sit face-up here. Events like Brawl, Rite, and Feast target Domains.
- **Shared zones** — Claw, Tree, Wheat, Coin. Defined by zone cards placed at setup. You interact with them by Ordering their zone card.

### Deck Access

Players do **not** automatically have access to all decks. Your Presence grants access to Claw and Tree. Other access is granted by cards (gateway cards like Sowing, Apprenticeship, etc.). Lose the card, lose the access.

### The Discard

Each player has their own **discard pile** (face-up). Other cards can reference it (e.g. Withered Crop checks for Harvest, Herbalism retrieves from discard). Cards **removed from the game** are gone permanently — they do not go to the discard.

### Tags

Tags are keywords on cards that other cards reference (e.g. [Mob], [Spiritual], [Nature]). They define what a card IS, not what it DOES.

### Event Resolution

When an event fires in a zone, resolve it one Domain at a time in play order (clockwise from the active player). Each player makes their own decisions when their Domain resolves.

---

## 4. Politics & Negotiation

- **Freeform.** Players may make any deal, alliance, threat, or promise at any time.
- **Nothing is binding.** Verbal agreements have no mechanical enforcement. Betrayal is expected.
- **Some cards require agreement.** (e.g. Apprenticeship requires another player's permission.)
- **No formal alliance system.** Alliances exist only in the social space.

---

## 5. Winning the Game

The game ends when **any deck's draw pile is fully emptied**.

- The depleted deck determines the **scoring axis**.
- The player who best matches the depleted deck's scoring criteria **wins**.
- Exact scoring rules per deck are TBD — they will be printed on the deck zone cards.

> Players must constantly watch which decks are thinning and adapt — or deliberately race a deck they're strong in.
