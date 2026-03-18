"""Game engine: generic loop, action resolution, event broadcasting.
All card-specific logic lives in cards/*.py — the engine just orchestrates."""
from __future__ import annotations
from state import GameState, Player, Card
from strategy import Strategy, Intent, DecisionContext
from cards import CardContext, CardBehavior, get_behavior
import cards.claw, cards.tree, cards.wheat, cards.coin, cards.candle, cards.sword, cards.zones


# Event responder sets — which events each card can respond to.
# Built from card behaviors at import time, but we define known sets here
# so the engine knows which cards to scan for each event type.
EVENT_NAMES = {"Dawn", "Order", "Brawl", "Rite", "Feast", "Harvest", "Rumour"}


class GameEngine:
    def __init__(self, state: GameState, strategies: dict[str, Strategy],
                 observers: list | None = None):
        self.state = state
        self.strategies = strategies
        self.observers = observers or []
        self._event_depth = 0
        self._max_event_depth = 10
        self._event_cancelled = False
        self._fired_this_dawn: set[int] = set()  # card ids that already triggered

    def _notify(self, method: str, *args, **kwargs):
        for obs in self.observers:
            getattr(obs, method)(*args, **kwargs)

    def strat(self, player: Player) -> Strategy:
        return self.strategies[player.name]

    def behavior(self, card: Card) -> CardBehavior:
        return get_behavior(card.name)

    def make_ctx(self, player: Player, card: Card, **kwargs) -> CardContext:
        return CardContext(engine=self, player=player, card=card,
                           state=self.state, **kwargs)

    def cancel_event(self):
        """Called by card behaviors (Eldership, Militia) to cancel current event."""
        self._event_cancelled = True

    # ── Main Game Loop ──

    def run_game(self, max_turns: int = 200) -> str | None:
        s = self.state
        self._notify("on_game_start", s, self.strategies)
        s.log(f"# Kingdoms Simulation\n")
        s.log(f"**Players:** {', '.join(p.name for p in s.players)} "
              f"({len(s.players)} players, max {max_turns} turns)\n")
        s.log("---\n")
        s.log("## Initial State\n")
        s.log(f"Season: {', '.join(c.name for c in s.season)}")
        s.log(f"Fields ({len(s.fields)}): {', '.join(c.name for c in s.fields)}")
        s.log(f"Opportunities ({len(s.opportunities)}): {', '.join(c.name for c in s.opportunities)}")
        s.log(f"Wares ({len(s.wares)}): {', '.join(c.name for c in s.wares)}")
        s.log(f"Tourney ({len(s.tourney)}): {', '.join(c.name for c in s.tourney)}")
        piles = ", ".join(f"{d} {s.pile_remaining(d)}"
                          for d in ("claw", "tree", "wheat", "coin", "candle", "sword") if d in s.zone_cards)
        s.log(f"Piles: {piles}")
        s.log("\n---\n")

        for t in range(1, max_turns + 1):
            if s.game_over:
                break
            s.turn_num = t
            p_idx = (t - 1) % len(s.players)
            player = s.players[p_idx]

            if p_idx == 0:
                s.round_num += 1
                end_t = min(t + len(s.players) - 1, max_turns)
                s.log(f"## Round {s.round_num} (Turns {t}–{end_t})\n")

            self.resolve_turn(player)

            if t % 10 == 0:
                self._log_state_snapshot(t)

            depleted = s.check_game_end()
            if depleted:
                s.game_over = True
                s.depleted_pile = depleted
                s.log(f"\n### 🏁 GAME ENDS — {depleted} zone fully depleted! (Turn {t})\n")

        self._log_epilogue()
        winner = self._compute_winner()
        self._notify("on_game_end", s, s.depleted_pile, winner)
        return s.depleted_pile

    def _compute_winner(self) -> str | None:
        s = self.state
        win_tags = {"tree": "Nature", "claw": "Trophy", "wheat": "Amenity", "coin": "Wealth", "candle": "Religion", "sword": "Chivalry"}
        win_tag = win_tags.get(s.depleted_pile)
        if not win_tag:
            return None
        scores = {p.name: p.count_tag_all(win_tag) for p in s.players}
        max_score = max(scores.values())
        winners = [n for n, sc in scores.items() if sc == max_score]
        return winners[0] if len(winners) == 1 else f"Tie({'/'.join(winners)})"

    def resolve_turn(self, player: Player):
        s = self.state
        self._fired_this_dawn.clear()
        self.resolve_event("Dawn", player, scope=player)
        self._notify("on_turn_end", s, player, None)
        s.log("")

    # ── Public helpers for card behaviors ──

    def order_zone(self, player: Player, zone_name: str):
        zone_card = self.state.zone_cards[zone_name]
        self.resolve_event("Order", player, scope=zone_card)


    def _card_is_placed(self, card: Card) -> bool:
        """Check if a card is already in some player's domain or discard."""
        for p in self.state.players:
            if card in p.domain or card in p.discard:
                return True
        return False

    def receive_card(self, player: Player, card: Card):
        """Handle a card being received — just place it in domain."""
        if not self._card_is_placed(card):
            player.add_to_domain(card, self.state)

        self._notify("on_card_received", self.state, player, card)

    def draw_and_receive(self, player: Player, pile: str, count: int = 1) -> list[Card]:
        """Draw cards from a pile and hand each to receive_card."""
        drawn: list[Card] = []
        for _ in range(count):
            card = self.state.draw_from_pile(pile)
            if card:
                drawn.append(card)
                self.receive_card(player, card)
        return drawn

    # ── Generic Event Resolution ──

    def resolve_event(self, event: str, active_player: Player,
                      scope: 'Card | Player | list[Player] | None' = None,
                      uprising: bool = False):
        """Fire an event to responding cards.
        scope controls what receives the event:
          Card   → just that one card (Order on a specific card/zone)
          Player → all cards in that player's domain (Brawl, local Rite)
          [Player, ...] → those players' domains (Rumour)
          None   → all domains (Harvest, Feast, global Rite)
        """
        if self._event_depth >= self._max_event_depth:
            self.state.log("  ⚠️ Event chain too deep, stopping")
            return
        self._event_depth += 1
        self._event_cancelled = False
        s = self.state

        handler_name = f"on_{event.lower()}"
        base_handler = getattr(CardBehavior, handler_name)

        # Single card scope — fire directly, skip zone broadcast and domain scan
        if isinstance(scope, Card):
            beh = self.behavior(scope)
            resp = 0
            if getattr(type(beh), handler_name) is not base_handler:
                if id(scope) in self._fired_this_dawn:
                    self._notify("on_event_fired", s, event, active_player, False, 0, scope)
                    self._event_depth -= 1
                    return
                # Find owner
                owner = active_player
                for p in s.players:
                    if scope in p.domain or scope in p.discard:
                        owner = p
                        break
                ctx = self.make_ctx(owner, scope, event=event,
                                    active_player=active_player, uprising=uprising)
                handler = getattr(beh, handler_name)
                if handler(ctx):
                    self._fired_this_dawn.add(id(scope))
                    resp = 1
            self._notify("on_event_fired", s, event, active_player, self._event_cancelled, resp, scope)
            self._event_depth -= 1
            return

        # Broadcast to zone cards first
        for zone_name, zone_card in s.zone_cards.items():
            if s.game_over or self._event_cancelled:
                break
            beh = self.behavior(zone_card)
            if getattr(type(beh), handler_name) is not base_handler:
                ctx = self.make_ctx(active_player, zone_card, event=event,
                                    active_player=active_player, uprising=uprising)
                handler = getattr(beh, handler_name)
                handler(ctx)

        # Determine which domains to scan
        all_players = s.play_order_from(active_player)
        if scope is None:
            scan_players = all_players
        elif isinstance(scope, list):
            scope_set = set(id(p) for p in scope)
            scan_players = [p for p in all_players if id(p) in scope_set]
        else:
            scan_players = [scope]

        responder_count = 0
        for p in scan_players:
            if s.game_over or self._event_cancelled:
                break

            # Find cards in this domain that might respond to this event
            responders = []
            for card in list(p.domain):
                beh = self.behavior(card)
                if getattr(type(beh), handler_name) is not base_handler:
                    responders.append(card)

            if not responders:
                continue

            # Owner chooses resolution order
            if len(responders) > 1:
                ordered = self.strat(p).sequence(
                    s, p, responders,
                    DecisionContext(event=event, source=event, intent=Intent.OPTION))
            else:
                ordered = responders

            for card in ordered:
                if self._event_cancelled or s.game_over:
                    break
                if card not in p.domain:
                    continue  # removed during earlier resolution
                if id(card) in self._fired_this_dawn:
                    continue  # already triggered this dawn

                beh = self.behavior(card)
                ctx = self.make_ctx(p, card, event=event, active_player=active_player,
                                    uprising=uprising)
                handler = getattr(beh, handler_name)
                if handler(ctx):
                    self._fired_this_dawn.add(id(card))
                    responder_count += 1

        self._notify("on_event_fired", s, event, active_player, self._event_cancelled, responder_count, scope)
        self._event_depth -= 1

    # ── Logging ──

    def _log_state_snapshot(self, turn: int):
        s = self.state
        s.log("---\n")
        s.log(f"### State after Turn {turn}\n")
        for p in s.players:
            dom = ", ".join(c.name for c in p.domain) or "*(empty)*"
            s.log(f"**{p.name}** ({len(p.domain)} cards): {dom}")
            disc = ", ".join(c.name for c in p.discard)
            if disc:
                s.log(f"  Discard: {disc}")
        s.log("")
        s.log(f"Season: {', '.join(c.name for c in s.season)}")
        s.log(f"Fields ({len(s.fields)}): {', '.join(c.name for c in s.fields)}")
        s.log(f"Opportunities ({len(s.opportunities)}): {', '.join(c.name for c in s.opportunities)}")
        s.log(f"Wares ({len(s.wares)}): {', '.join(c.name for c in s.wares)}")
        s.log(f"Tourney ({len(s.tourney)}): {', '.join(c.name for c in s.tourney)}")
        piles = ", ".join(f"{d} {s.pile_remaining(d)}"
                          for d in ("claw", "tree", "wheat", "coin", "candle", "sword") if d in s.zone_cards)
        s.log(f"Piles: {piles}")
        s.log("\n---\n")

    def _log_epilogue(self):
        s = self.state
        s.log("---\n")
        s.log("## Epilogue\n")

        win_conditions = {
            "tree": ("Nature", "🌳 Tree depleted — most [Nature] wins"),
            "claw": ("Trophy", "🐾 Claw depleted — most [Trophy] wins"),
            "wheat": ("Amenity", "🌾 Wheat depleted — most [Amenity] wins"),
            "coin": ("Wealth", "🪙 Coin depleted — most [Wealth] wins"),
            "candle": ("Religion", "🕯️ Candle depleted — most [Religion] wins"),
            "sword": ("Chivalry", "⚔️ Sword depleted — most [Chivalry] wins"),
        }

        for p in s.players:
            dom = ", ".join(c.name for c in p.domain) or "*(empty)*"
            s.log(f"**{p.name}** — {len(p.domain)} cards")
            s.log(f"  Domain: {dom}")
            tag_counts: dict[str, int] = {}
            for c in p.domain:
                for tag in c.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            if tag_counts:
                tag_str = ", ".join(f"[{t}]×{n}" for t, n in sorted(tag_counts.items()))
                s.log(f"  Tags: {tag_str}")
            s.log("")

        if s.game_over and s.depleted_pile:
            wc = win_conditions.get(s.depleted_pile)
            if wc:
                win_tag, label = wc
                s.log(f"### Winner\n")
                s.log(f"{label}\n")
                scores = {}
                for p in s.players:
                    scores[p.name] = p.count_tag_all(win_tag)
                max_score = max(scores.values()) if scores else 0
                winners = [name for name, sc in scores.items() if sc == max_score]
                for p in s.players:
                    marker = " 👑" if scores[p.name] == max_score else ""
                    s.log(f"- **{p.name}**: {scores[p.name]} [{win_tag}]{marker}")
                if len(winners) > 1:
                    s.log(f"\n**Tie between {' and '.join(winners)}!**")
                else:
                    s.log(f"\n**{winners[0]} wins!**")
            else:
                s.log(f"### Game ended — {s.depleted_pile} depleted (no scoring axis defined)")

        piles = ", ".join(f"{d} {s.pile_remaining(d)}"
                          for d in ("claw", "tree", "wheat", "coin", "candle", "sword") if d in s.zone_cards)
        s.log(f"\n### Stats")
        s.log(f"Turns: {s.turn_num} | Piles: {piles}")
