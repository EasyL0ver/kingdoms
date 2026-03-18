"""Zone and Presence card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Presence(CardBehavior):
    name = "Presence"
    tags = []
    deck = "zone"

    def _orderable(self, engine, card):
        beh = engine.behavior(card)
        return getattr(type(beh), 'on_order') is not getattr(CardBehavior, 'on_order')

    def on_dawn(self, ctx):
        s = ctx.state
        player = ctx.player
        options = []

        # Presence itself — zone access (claw/tree)
        zone_options = []
        if s.pile_remaining("claw") > 0:
            zone_options.append("claw")
        if s.season:
            zone_options.append("tree")
        if zone_options:
            options.append(ctx.card)  # Presence = pick a zone

        # Domain cards with on_order
        for card in player.domain:
            if self._orderable(ctx.engine, card):
                options.append(card)

        # Discard cards with on_order (deduplicate by name)
        seen = set()
        for card in player.discard:
            if card.name not in seen and self._orderable(ctx.engine, card):
                seen.add(card.name)
                options.append(card)

        # Wells in other players' domains
        for p in s.players:
            if p is player:
                continue
            for card in p.domain:
                if card.name == "Well" and self._orderable(ctx.engine, card):
                    options.append(card)

        if not options:
            s.log("  *(no valid actions)*")
            return

        pick = ctx.engine.strat(player).resolve(
            s, player, options,
            DecisionContext(event="Turn", source="Presence", intent=Intent.OPTION))
        s.log(f"**T{s.turn_num} — {player.name}:** Order {pick.name}")

        if pick is ctx.card:
            # Presence picked — choose zone
            choice = ctx.engine.strat(player).resolve(
                s, player, zone_options,
                DecisionContext(event="Order", source="Presence", intent=Intent.OPTION))
            ctx.engine.resolve_event("Order", player, scope=s.zone_cards[choice])
        else:
            ctx.engine.resolve_event("Order", player, scope=pick)


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
        if ctx.player.domain and s.opportunities:
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
        elif choice == "trade" and ctx.player.domain and s.opportunities:
            to_trade = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, list(ctx.player.domain),
                DecisionContext(event="Order", source="Coin Zone", intent=Intent.DISCARD))
            ctx.player.remove_from_domain(to_trade)
            s.wares.append(to_trade)
            pick = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, list(s.opportunities),
                DecisionContext(event="Order", source="Coin Zone", intent=Intent.GAIN))
            s.opportunities.remove(pick)
            ctx.player.add_to_domain(pick, s)
            s.log(f"  → trades {to_trade.name} into Wares, takes {pick.name} from Opportunities")
            self.refill(s, 3)
            s.log(f"  → Trade triggers Rumour!")
            ctx.engine.resolve_event("Rumour", ctx.player, scope=ctx.state.other_players(ctx.player))

    def refill(self, state, target: int = 3):
        """Refill Opportunities to target from coin pile."""
        zone = state.zone_cards["coin"]
        while len(zone.face_up) < target and zone.pile_ptr < len(zone.pile):
            zone.face_up.append(zone.pile[zone.pile_ptr])
            zone.pile_ptr += 1


@_register
class CandleZone(CardBehavior):
    name = "Candle Zone"
    tags = ["Zone"]
    deck = "zone"

    def on_order(self, ctx):
        """Draw the Revelation and replace it."""
        s = ctx.state
        if not s.revelation:
            s.log("  → Candle zone: no Revelation to claim")
            return
        rev_card = s.revelation.pop(0)
        ctx.player.add_to_domain(rev_card, s)
        s.log(f"  → claims Revelation: {rev_card.name}")
        self.refill(s)

    def refill(self, state, target: int = 1):
        """Flip top candle card as Revelation (max 1)."""
        zone = state.zone_cards["candle"]
        while len(zone.face_up) < target and zone.pile_ptr < len(zone.pile):
            zone.face_up.append(zone.pile[zone.pile_ptr])
            zone.pile_ptr += 1


@_register
class SwordZone(CardBehavior):
    name = "Sword Zone"
    tags = ["Zone"]
    deck = "zone"

    def on_order(self, ctx):
        """The Tourney: 2 face-up sword cards.
        Injustice (≥2 Mob in any single domain): take BOTH, Unit cards from
        the pair go to the tyrant's domain, non-Units go to you.
        Peace: Joust — challenge opponent, Accept = both pick one,
        Refuse = Brawl in both players' domains."""
        s = ctx.state
        tourney = list(s.zone_cards["sword"].face_up)
        if not tourney:
            s.log("  → Tourney empty, nothing to do")
            return

        # Check for injustice: any player with ≥2 Mob tags in domain
        tyrant = None
        for p in s.players:
            if p.count_tag("Mob") >= 2:
                tyrant = p
                break

        if tyrant:
            self._injustice(ctx, tourney, tyrant)
        else:
            self._joust(ctx, tourney)

    def _injustice(self, ctx, tourney, tyrant):
        s = ctx.state
        s.log(f"  → Injustice! {tyrant.name} has ≥2 Mob tags")
        face_up = s.zone_cards["sword"].face_up
        for card in tourney:
            face_up.remove(card)
            if card.has_tag("Unit"):
                # Knights march to fight injustice
                tyrant.add_to_domain(card, s)
                s.log(f"  → {card.name} (Unit) deployed to {tyrant.name}'s domain")
            else:
                ctx.player.add_to_domain(card, s)
                s.log(f"  → {card.name} claimed by {ctx.player.name}")
        self.refill(s)

    def _joust(self, ctx, tourney):
        s = ctx.state
        # Choose opponent to challenge
        opponents = s.other_players(ctx.player)
        if not opponents:
            return
        opponent = ctx.engine.strat(ctx.player).resolve(
            s, ctx.player, opponents,
            DecisionContext(event="Order", source="Sword Zone", intent=Intent.TARGET))
        s.log(f"  → Peace: {ctx.player.name} challenges {opponent.name} to a Joust")

        # Opponent decides: Accept or Refuse
        choice = ctx.engine.strat(opponent).resolve(
            s, opponent, ["accept", "refuse"],
            DecisionContext(event="Order", source="Sword Zone", intent=Intent.OPTION))

        face_up = s.zone_cards["sword"].face_up
        if choice == "accept":
            s.log(f"  → {opponent.name} accepts the Joust")
            # Both pick one card from tourney
            if len(tourney) >= 2:
                pick1 = ctx.engine.strat(ctx.player).resolve(
                    s, ctx.player, list(tourney),
                    DecisionContext(event="Order", source="Sword Zone", intent=Intent.GAIN))
                face_up.remove(pick1)
                tourney.remove(pick1)
                ctx.player.add_to_domain(pick1, s)
                s.log(f"  → {ctx.player.name} takes {pick1.name}")

                pick2 = ctx.engine.strat(opponent).resolve(
                    s, opponent, list(tourney),
                    DecisionContext(event="Order", source="Sword Zone", intent=Intent.GAIN))
                face_up.remove(pick2)
                opponent.add_to_domain(pick2, s)
                s.log(f"  → {opponent.name} takes {pick2.name}")
            elif len(tourney) == 1:
                # Only one card — challenger gets it
                card = tourney[0]
                face_up.remove(card)
                ctx.player.add_to_domain(card, s)
                s.log(f"  → {ctx.player.name} takes {card.name}")
            self.refill(s)
        else:
            s.log(f"  → {opponent.name} refuses! Brawl in both domains")
            ctx.engine.resolve_event("Brawl", ctx.player, ctx.player)
            if not s.game_over:
                ctx.engine.resolve_event("Brawl", ctx.player, opponent)

    def refill(self, state, target: int = 2):
        """Refill Tourney to 2 face-up sword cards."""
        zone = state.zone_cards["sword"]
        while len(zone.face_up) < target and zone.pile_ptr < len(zone.pile):
            zone.face_up.append(zone.pile[zone.pile_ptr])
            zone.pile_ptr += 1
