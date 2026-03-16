"""Zone and Domain card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Domain(CardBehavior):
    name = "Domain"
    tags = []
    deck = "zone"

    def can_activate(self, ctx):
        return True

    def on_activate(self, ctx):
        options = []
        if ctx.state.pile_remaining("claw") > 0:
            options.append("claw")
        if ctx.state.season:
            options.append("tree")
        if not options:
            ctx.state.log("  → No zones available")
            return
        choice = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, options,
            DecisionContext(Intent.PICK_OPTION, source="Domain",
                            consequence="activate Claw or Tree zone"))
        zone_card = ctx.state.zone_cards[choice]
        zone_beh = ctx.engine.behavior(zone_card)
        zone_ctx = ctx.engine.make_ctx(ctx.player, zone_card)
        zone_beh.on_activate(zone_ctx)


@_register
class ClawZone(CardBehavior):
    name = "Claw Zone"
    tags = ["Zone"]
    deck = "zone"

    def on_activate(self, ctx):
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

    def on_activate(self, ctx):
        if ctx.state.season:
            pick = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, list(ctx.state.season),
                DecisionContext(Intent.GAIN, source="Tree Zone",
                                consequence="take from Season"))
            if pick in ctx.state.season:
                ctx.state.season.remove(pick)
                ctx.state.log(f"  → takes {pick.name} from Season")
                ctx.engine.receive_card(ctx.player, pick)
                self.refill(ctx.state)

    def refill(self, state):
        """Refill Season to 4 when empty."""
        zone = state.zone_cards["tree"]
        if len(zone.face_up) == 0:
            while len(zone.face_up) < 4 and zone.pile_ptr < len(zone.pile):
                zone.face_up.append(zone.pile[zone.pile_ptr])
                zone.pile_ptr += 1
            if zone.face_up:
                names = ", ".join(c.name for c in zone.face_up)
                state.log(f"  🔄 Season refilled: {names}")


@_register
class WheatZone(CardBehavior):
    name = "Wheat Zone"
    tags = ["Zone"]
    deck = "zone"

    def on_activate(self, ctx):
        s = ctx.state
        if not s.fields:
            s.log("  → Fields empty, nothing to take")
            return
        max_take = min(3, len(s.fields))
        to_take = ctx.engine.strat(ctx.player).choose_n(
            s, ctx.player, list(s.fields), 1, max_take,
            DecisionContext(Intent.GAIN, source="Wheat Zone",
                            consequence="Claw tax: draw 1 per card taken"))
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

    def on_event(self, ctx):
        if not ctx.responds_to("Harvest"):
            return False
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

    def on_activate(self, ctx):
        s = ctx.state
        options = []
        if s.wares:
            options.append("buy")
        if ctx.player.domain and s.pile_remaining("coin") > 0:
            options.append("trade")
        if not options:
            s.log("  → Coin zone: nothing to do")
            return
        choice = ctx.engine.strat(ctx.player).choose_from(
            s, ctx.player, options,
            DecisionContext(Intent.PICK_OPTION, source="Coin Zone",
                            consequence="Buy from Wares or Trade"))
        if choice == "buy" and s.wares:
            pick = ctx.engine.strat(ctx.player).choose_from(
                s, ctx.player, list(s.wares),
                DecisionContext(Intent.GAIN, source="Coin Zone",
                                consequence="take from Wares"))
            s.wares.remove(pick)
            ctx.player.add_to_domain(pick, s)
            s.log(f"  → buys {pick.name} from Wares")
            self.refill(s)
        elif choice == "trade" and ctx.player.domain:
            to_trade = ctx.engine.strat(ctx.player).choose_from(
                s, ctx.player, list(ctx.player.domain),
                DecisionContext(Intent.SACRIFICE, source="Coin Zone",
                                consequence="put in Wares, draw blind from Coin"))
            ctx.player.remove_from_domain(to_trade)
            s.wares.append(to_trade)
            coin = s.draw_from_pile("coin")
            if coin:
                s.log(f"  → trades {to_trade.name} into Wares, draws {coin.name} from Coin")
                ctx.engine.receive_card(ctx.player, coin)

    def refill(self, state, target: int = 3):
        """Refill Wares up to target."""
        zone = state.zone_cards["coin"]
        while len(zone.face_up) < target and zone.pile_ptr < len(zone.pile):
            zone.face_up.append(zone.pile[zone.pile_ptr])
            zone.pile_ptr += 1
