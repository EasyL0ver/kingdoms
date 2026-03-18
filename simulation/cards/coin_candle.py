"""Coin and Candle deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Treasure(CardBehavior):
    name = 'Treasure'
    tags = ['Trophy', 'Amenity', 'Wealth']
    deck = 'coin'


@_register
class Market(CardBehavior):
    name = 'Market'
    tags = []
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        ctx.engine.order_zone(ctx.player, "coin")

    def on_rumour(self, ctx):
        if not ctx.player.domain or not ctx.state.wares:
            return False
        if not ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Rumour", source="Market", intent=Intent.OPTION)):
            return False
        to_trade = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.player.domain),
            DecisionContext(event="Rumour", source="Market", intent=Intent.DISCARD))
        ctx.player.remove_from_domain(to_trade)
        ctx.state.wares.append(to_trade)
        pick = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.state.wares),
            DecisionContext(event="Rumour", source="Market", intent=Intent.GAIN))
        ctx.state.wares.remove(pick)
        ctx.player.add_to_domain(pick, ctx.state)
        ctx.state.log(f"  → Market: {ctx.player.name} trades {to_trade.name} for {pick.name}")
        return True


@_register
class Smuggler(CardBehavior):
    name = 'Smuggler'
    tags = ['Mob']
    deck = 'coin'
    def on_brawl(self, ctx):
        if ctx.target is None:
            return False
        defender = ctx.target
        moveable = [c for c in defender.domain if c is not ctx.card]
        if not moveable:
            return False
        victim = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, moveable,
            DecisionContext(event="Brawl", source="Smuggler", intent=Intent.DISCARD))
        defender.remove_from_domain(victim)
        ctx.state.wares.append(victim)
        ctx.state.log(f"  → Smuggler: {victim.name} from {defender.name} goes to Wares")
        return True

    def on_rumour(self, ctx):
        if ctx.active_player is None or ctx.active_player is ctx.player:
            return False
        ctx.player.remove_from_domain(ctx.card)
        ctx.active_player.add_to_domain(ctx.card, ctx.state)
        ctx.state.log(f"  → Smuggler: moves to {ctx.active_player.name}")
        return True


@_register
class Sellsword(CardBehavior):
    name = 'Sellsword'
    tags = ['Unit']
    deck = 'coin'
    def on_brawl(self, ctx):
        if ctx.target is not ctx.player:
            return False
        if not ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Brawl", source="Sellsword", intent=Intent.OPTION)):
            return False
        ctx.player.remove_from_domain(ctx.card)
        ctx.state.wares.append(ctx.card)
        ctx.state.log(f"  → Sellsword cancels Brawl (goes to Wares)")
        ctx.engine.cancel_event()
        return True


@_register
class Windfall(CardBehavior):
    name = 'Windfall'
    tags = []
    deck = 'coin'
    def on_dawn(self, ctx):
        if len(ctx.state.wares) < 4:
            return
        max_take = min(3, len(ctx.state.wares))
        picks = ctx.engine.strat(ctx.player).resolve_n(
            ctx.state, ctx.player, list(ctx.state.wares),
            1, max_take,
            DecisionContext(event="Dawn", source="Windfall", intent=Intent.GAIN))
        for pick in picks:
            ctx.state.wares.remove(pick)
            ctx.player.add_to_domain(pick, ctx.state)
            ctx.state.log(f"  → Windfall: {ctx.player.name} takes {pick.name} from Wares")
        ctx.player.discard_from_domain(ctx.card)
        ctx.state.log(f"  → Windfall discarded")


@_register
class Prosperity(CardBehavior):
    name = 'Prosperity'
    tags = ['Wealth']
    deck = 'coin'
    def on_dawn(self, ctx):
        wealth_count = sum(1 for c in ctx.player.domain
                          if c.has_tag("Wealth") and c is not ctx.card)
        if wealth_count >= 2 and ctx.state.pile_remaining("coin") > 0:
            drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
            if drawn:
                ctx.state.log(f"  → Prosperity: {ctx.player.name} draws {drawn[0].name}")


@_register
class Embassy(CardBehavior):
    name = 'Embassy'
    tags = ['Wealth']
    deck = 'coin'
    def on_dawn(self, ctx):
        if not ctx.state.wares:
            return
        for other in ctx.state.other_players(ctx.player):
            if ctx.player.shares_culture(other) and ctx.state.wares:
                # Owner picks from wares
                if ctx.state.wares:
                    pick = ctx.engine.strat(ctx.player).resolve(
                        ctx.state, ctx.player, list(ctx.state.wares),
                        DecisionContext(event="Dawn", source="Embassy", intent=Intent.GAIN))
                    ctx.state.wares.remove(pick)
                    ctx.player.add_to_domain(pick, ctx.state)
                    ctx.state.log(f"  → Embassy: {ctx.player.name} takes {pick.name} from Wares")
                # Ally picks from wares
                if ctx.state.wares:
                    ally_pick = ctx.engine.strat(other).resolve(
                        ctx.state, other, list(ctx.state.wares),
                        DecisionContext(event="Dawn", source="Embassy", intent=Intent.GAIN))
                    ctx.state.wares.remove(ally_pick)
                    other.add_to_domain(ally_pick, ctx.state)
                    ctx.state.log(f"  → Embassy: {other.name} takes {ally_pick.name} from Wares")
                break  # Only one culture ally needed


@_register
class Efficiency(CardBehavior):
    name = 'Efficiency'
    tags = []
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        orderable = [c for c in ctx.player.domain
                     if c is not ctx.card and ctx.engine._has_on_order(c)]
        if not orderable:
            ctx.player.discard_from_domain(ctx.card)
            ctx.state.log(f"  → Efficiency: nothing to order, discarded")
            return
        max_orders = min(4, len(orderable))
        to_order = ctx.engine.strat(ctx.player).resolve_n(
            ctx.state, ctx.player, orderable,
            0, max_orders,
            DecisionContext(event="Order", source="Efficiency", intent=Intent.OPTION))
        for card in to_order:
            if card not in ctx.player.domain:
                continue
            beh = ctx.engine.behavior(card)
            sub_ctx = ctx.engine.make_ctx(ctx.player, card, active_player=ctx.player)
            ctx.state.log(f"  → Efficiency orders {card.name}")
            beh.on_order(sub_ctx)
        ctx.player.discard_from_domain(ctx.card)
        ctx.state.log(f"  → Efficiency discarded")


@_register
class SpiceMarket(CardBehavior):
    name = 'Spice Market'
    tags = ['Wealth']
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        unique_tags = set()
        for c in ctx.player.domain:
            for tag in c.tags:
                unique_tags.add(tag)
        draw_count = min(len(unique_tags), ctx.state.pile_remaining("coin"))
        if draw_count <= 0:
            ctx.state.log(f"  → Spice Market: {len(unique_tags)} unique tags but no coin left")
            return
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin", draw_count)
        names = ", ".join(c.name for c in drawn)
        ctx.state.log(f"  → Spice Market: {len(unique_tags)} unique tags → draws {len(drawn)}: {names}")


@_register
class Commodities(CardBehavior):
    name = 'Commodities'
    tags = []
    deck = 'coin'
    def on_rumour(self, ctx):
        piles = [d for d in ("tree", "claw", "wheat", "coin")
                 if ctx.state.pile_remaining(d) > 0]
        if not piles:
            return False
        pile = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, piles,
            DecisionContext(event="Rumour", source="Commodities", intent=Intent.OPTION))
        card = ctx.state.draw_from_pile(pile)
        if card:
            ctx.state.wares.append(card)
            ctx.state.log(f"  → Commodities: {ctx.player.name} adds {card.name} from {pile} to Wares")
            return True
        return False


@_register
class Mine(CardBehavior):
    name = 'Mine'
    tags = ['Labour']
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain" or ctx.state.pile_remaining("coin") <= 0:
            return
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → Mine draws {drawn[0].name} from Coin")

    def on_dawn(self, ctx):
        if not ctx.player.has_card("Crags"):
            ctx.state.log(f"  → Dawn: no Crags → Mine to discard")
            ctx.player.discard.append(ctx.card)


@_register
class Provisions(CardBehavior):
    name = 'Provisions'
    tags = ['Amenity']
    deck = 'coin'
    def on_feast(self, ctx):
        if ctx.state.pile_remaining("coin") <= 0:
            return False
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → Provisions: {ctx.player.name} draws {drawn[0].name} from Coin")
            return True
        return False


@_register
class Indulgence(CardBehavior):
    name = 'Indulgence'
    tags = ['Religion']
    deck = 'candle'
    def on_order(self, ctx):
        if ctx.location != "domain" or ctx.state.pile_remaining("coin") <= 0:
            return
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → Indulgence: {ctx.player.name} draws {drawn[0].name} from Coin")
        # Refill wares from coin pile
        from cards.zones import CoinZone
        coin_zone = ctx.engine.behavior(ctx.state.zone_cards["coin"])
        coin_zone.refill(ctx.state)
        # Choose: trigger 2 Rumours or stay silent
        if ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Order", source="Indulgence", intent=Intent.OPTION)):
            ctx.state.log(f"  → Indulgence: spectacle! Two Rumours spread")
            ctx.engine.resolve_event("Rumour", ctx.player, exclude_active=True)
            ctx.engine.resolve_event("Rumour", ctx.player, exclude_active=True)
        else:
            ctx.state.log(f"  → Indulgence: silence — no Rumour")


@_register
class WorshipOfTheFlame(CardBehavior):
    name = 'Worship of the Flame'
    tags = ['Spiritual']
    deck = 'candle'
    def on_rite(self, ctx):
        return True
