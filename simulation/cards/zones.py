"""Zone and Presence card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Presence(CardBehavior):
    name = "Presence"
    tags = []
    deck = "zone"

    def on_order(self, ctx):
        options = []
        if ctx.state.pile_remaining("claw") > 0:
            options.append("claw")
        if ctx.state.season:
            options.append("tree")
        if not options:
            ctx.state.log("  → No zones available")
            return
        choice = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, options,
            DecisionContext(event="Order", source="Presence", intent=Intent.OPTION))
        zone_card = ctx.state.zone_cards[choice]
        zone_beh = ctx.engine.behavior(zone_card)
        zone_ctx = ctx.engine.make_ctx(ctx.player, zone_card)
        zone_beh.on_order(zone_ctx)


@_register
class ClawZone(CardBehavior):
    name = "Claw Zone"
    tags = ["Zone"]
    deck = "zone"

    def on_order(self, ctx):
        for _ in range(2):
            card = ctx.state.draw_from_pile("claw")
            if card:
                ctx.state.log(f"  draws {card.name} from Claw")
                ctx.engine.receive_card(ctx.player, card)
            if ctx.state.game_over:
                break


@_register
class TreeZone(CardBehavior):
    name = "Tree Zone"
    tags = ["Zone"]
    deck = "zone"

    def on_order(self, ctx):
        if ctx.state.season:
            pick = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, list(ctx.state.season),
                DecisionContext(event="Order", source="Tree Zone", intent=Intent.GAIN))
            if pick in ctx.state.season:
                ctx.state.season.remove(pick)
                ctx.state.log(f"  → takes {pick.name} from Season")
                ctx.engine.receive_card(ctx.player, pick)
                self.refill(ctx.state)

    def refill(self, state, target: int = 4):
        """Refill Season up to target."""
        zone = state.zone_cards["tree"]
        while len(zone.face_up) < target and zone.pile_ptr < len(zone.pile):
            zone.face_up.append(zone.pile[zone.pile_ptr])
            zone.pile_ptr += 1


@_register
class WheatZone(CardBehavior):
    name = "Wheat Zone"
    tags = ["Zone"]
    deck = "zone"

    def on_order(self, ctx):
        s = ctx.state
        if not s.fields:
            s.log("  → Fields empty, nothing to take")
            return
        max_take = min(3, len(s.fields))
        to_take = ctx.engine.strat(ctx.player).resolve_n(
            s, ctx.player, list(s.fields), 1, max_take,
            DecisionContext(event="Order", source="Wheat Zone", intent=Intent.GAIN))
        for c in to_take:
            if c in s.fields:
                s.fields.remove(c)
                ctx.engine.receive_card(ctx.player, c)
                s.log(f"  → takes {c.name} from Fields")
        tax = len(to_take)
        s.log(f"  → Claw tax: draws {tax}")
        for _ in range(tax):
            claw = s.draw_from_pile("claw")
            if claw:
                s.log(f"    → tax: {claw.name}")
                ctx.engine.receive_card(ctx.player, claw)

    def refill(self, state, target: int = 5):
        """Refill Fields up to target."""
        zone = state.zone_cards["wheat"]
        while len(zone.face_up) < target and zone.pile_ptr < len(zone.pile):
            zone.face_up.append(zone.pile[zone.pile_ptr])
            zone.pile_ptr += 1

    def on_harvest(self, ctx):
        s = ctx.state
        old_count = len(s.fields)
        self.refill(s)
        new_count = len(s.fields)
        if new_count > old_count:
            s.log(f"  → Fields refilled: {old_count} → {new_count}")
        return True


@_register
class CoinZone(CardBehavior):
    name = "Coin Zone"
    tags = ["Zone"]
    deck = "zone"

    def on_order(self, ctx):
        s = ctx.state
        options = []
        if s.wares:
            options.append("buy")
        if ctx.player.domain and s.pile_remaining("coin") > 0:
            options.append("trade")
        if not options:
            s.log("  → Coin zone: nothing to do")
            return
        choice = ctx.engine.strat(ctx.player).resolve(
            s, ctx.player, options,
            DecisionContext(event="Order", source="Coin Zone", intent=Intent.OPTION))
        if choice == "buy" and s.wares:
            pick = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, list(s.wares),
                DecisionContext(event="Order", source="Coin Zone", intent=Intent.GAIN))
            s.wares.remove(pick)
            ctx.player.add_to_domain(pick, s)
            s.log(f"  → buys {pick.name} from Wares")
            self.refill(s)
        elif choice == "trade" and ctx.player.domain:
            to_trade = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, list(ctx.player.domain),
                DecisionContext(event="Order", source="Coin Zone", intent=Intent.DISCARD))
            ctx.player.remove_from_domain(to_trade)
            s.wares.append(to_trade)
            coin = s.draw_from_pile("coin")
            if coin:
                s.log(f"  → trades {to_trade.name} into Wares, draws {coin.name} from Coin")
                ctx.engine.receive_card(ctx.player, coin)
            s.log(f"  → Trade triggers Rumour!")
            ctx.engine.resolve_event("Rumour", ctx.player, exclude_active=True)

    def refill(self, state, target: int = None):
        """Refill Wares from coin pile. No limit by default."""
        zone = state.zone_cards["coin"]
        limit = target if target is not None else len(zone.pile)
        while len(zone.face_up) < limit and zone.pile_ptr < len(zone.pile):
            zone.face_up.append(zone.pile[zone.pile_ptr])
            zone.pile_ptr += 1


@_register
class CandleZone(CardBehavior):
    name = "Candle Zone"
    tags = ["Zone"]
    deck = "zone"

    def on_order(self, ctx):
        """Clergy-gated: take Revelation + peek N from pile (N = players with
        Religion tags across the board), keep 1, set 1 as new Revelation, exile rest."""
        s = ctx.state
        if not s.revelation:
            s.log("  → Candle zone: no Revelation to claim")
            return

        # Claim the Revelation card
        rev_card = s.revelation.pop(0)
        ctx.player.add_to_domain(rev_card, s)
        s.log(f"  → claims Revelation: {rev_card.name}")

        # Dig depth = number of players with at least one Religion tag in domain
        faithful_count = sum(1 for p in s.players
                            if any(c.has_tag("Religion") for c in p.domain))
        peek_n = min(faithful_count, s.pile_remaining("candle"))

        if peek_n <= 0:
            # No cards to peek — just flip next Revelation if available
            self.refill(s)
            return

        peeked = []
        for _ in range(peek_n):
            card = s.draw_from_pile("candle")
            if card:
                peeked.append(card)

        if not peeked:
            self.refill(s)
            return

        s.log(f"  → peeks {len(peeked)} from candle pile ({faithful_count} faithful)")

        if len(peeked) == 1:
            # Only one card: choose keep or set as Revelation
            choice = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, ["keep", "revelation"],
                DecisionContext(event="Order", source="Candle Zone", intent=Intent.OPTION))
            if choice == "keep":
                ctx.player.add_to_domain(peeked[0], s)
                s.log(f"  → keeps {peeked[0].name}")
                self.refill(s)
            else:
                s.revelation.append(peeked[0])
                s.log(f"  → sets {peeked[0].name} as Revelation")
        else:
            # Pick 1 to keep
            keep = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, peeked,
                DecisionContext(event="Order", source="Candle Zone", intent=Intent.GAIN))
            peeked.remove(keep)
            ctx.player.add_to_domain(keep, s)
            s.log(f"  → keeps {keep.name}")

            # Pick 1 to set as new Revelation
            if peeked:
                new_rev = ctx.engine.strat(ctx.player).resolve(
                    s, ctx.player, peeked,
                    DecisionContext(event="Order", source="Candle Zone", intent=Intent.OPTION))
                peeked.remove(new_rev)
                s.revelation.append(new_rev)
                s.log(f"  → sets {new_rev.name} as Revelation")

            # Exile the rest (remove from game)
            for card in peeked:
                s.log(f"  → exiles {card.name}")

    def refill(self, state, target: int = 1):
        """Flip top candle card as Revelation (max 1)."""
        zone = state.zone_cards["candle"]
        while len(zone.face_up) < target and zone.pile_ptr < len(zone.pile):
            zone.face_up.append(zone.pile[zone.pile_ptr])
            zone.pile_ptr += 1
