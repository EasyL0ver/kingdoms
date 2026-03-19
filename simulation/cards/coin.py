"""Coin deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Treasure(CardBehavior):
    name = 'Treasure'
    tags = ['Trophy', 'Amenity', 'Wealth']
    deck = 'coin'


@_register
class PawnShop(CardBehavior):
    name = 'Pawn Shop'
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
                DecisionContext(event="Rumour", source="Pawn Shop", intent=Intent.OPTION)):
            return False
        to_trade = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.player.domain),
            DecisionContext(event="Rumour", source="Pawn Shop", intent=Intent.DISCARD))
        ctx.player.remove_from_domain(to_trade)
        ctx.state.wares.append(to_trade)
        pick = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.state.wares),
            DecisionContext(event="Rumour", source="Pawn Shop", intent=Intent.GAIN))
        ctx.state.wares.remove(pick)
        ctx.player.add_to_domain(pick, ctx.state)
        ctx.state.log(f"  → Pawn Shop: {ctx.player.name} trades {to_trade.name} for {pick.name}")
        return True


@_register
class Smuggler(CardBehavior):
    name = 'Smuggler'
    tags = ['Mob']
    deck = 'coin'
    def on_brawl(self, ctx):
        if not ctx.state.wares or ctx.active_player is None:
            return False
        # Controller picks which Ware the brawl starter gets
        pick = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.state.wares),
            DecisionContext(event="Brawl", source="Smuggler", intent=Intent.DISCARD))
        ctx.state.wares.remove(pick)
        ctx.active_player.add_to_domain(pick, ctx.state)
        ctx.state.log(f"  → Smuggler: {ctx.player.name} gives {pick.name} from Wares to {ctx.active_player.name}")
        # Smuggler moves to brawl starter's domain
        if ctx.active_player is not ctx.player:
            ctx.player.remove_from_domain(ctx.card)
            ctx.active_player.add_to_domain(ctx.card, ctx.state)
            ctx.state.log(f"  → Smuggler moves to {ctx.active_player.name}")
        return True


@_register
class Sellsword(CardBehavior):
    name = 'Sellsword'
    tags = ['Unit']
    deck = 'coin'
    def on_brawl(self, ctx):
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
class Swindle(CardBehavior):
    name = 'Swindle'
    tags = []
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain" or not ctx.state.wares:
            return
        target = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.state.players),
            DecisionContext(event="Order", source="Swindle", intent=Intent.OPTION))
        # Target takes ALL wares
        taken = list(ctx.state.wares)
        for card in taken:
            ctx.state.wares.remove(card)
            target.add_to_domain(card, ctx.state)
        names = ", ".join(c.name for c in taken)
        ctx.state.log(f"  → Swindle: {target.name} takes all Wares ({len(taken)}): {names}")
        # Brawl in their domain
        ctx.state.log(f"  → Swindle: Brawl erupts in {target.name}'s domain!")
        ctx.engine.resolve_event("Brawl", ctx.player, scope=target)
        # Self-discard
        ctx.player.discard_from_domain(ctx.card)
        ctx.state.log(f"  → Swindle discarded")


@_register
class Prosperity(CardBehavior):
    name = 'Prosperity'
    tags = ['Wealth']
    deck = 'coin'
    def on_dawn(self, ctx):
        if not ctx.state.opportunities or ctx.state.pile_remaining("coin") <= 0:
            return
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
        from cards import CardBehavior as _CB
        orderable = [c for c in ctx.player.domain
                     if c is not ctx.card
                     and getattr(type(ctx.engine.behavior(c)), 'on_order') is not getattr(_CB, 'on_order')]
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
            ctx.state.log(f"  → Efficiency orders {card.name}")
            ctx.engine.resolve_event("Order", ctx.player, scope=card)
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
class Market(CardBehavior):
    name = 'Market'
    tags = []
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain" or not ctx.state.wares:
            return
        # Offer a Ware — buyer picks which one
        targets = ctx.state.other_players(ctx.player)
        if not targets:
            return
        target = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(targets),
            DecisionContext(event="Order", source="Market", intent=Intent.OPTION))
        pick = ctx.engine.strat(target).resolve(
            ctx.state, target, list(ctx.state.wares),
            DecisionContext(event="Order", source="Market", intent=Intent.GAIN))
        # Target decides to accept or not
        accept = ctx.engine.strat(target).resolve(
            ctx.state, target, [True, False],
            DecisionContext(event="Order", source="Market", intent=Intent.OPTION))
        if accept:
            ctx.state.wares.remove(pick)
            target.add_to_domain(pick, ctx.state)
            ctx.state.log(f"  → Market: {target.name} buys {pick.name} from Wares")
            ctx.engine.order_zone(ctx.player, "coin")
        else:
            ctx.state.log(f"  → Market: {target.name} declines")


@_register
class Stockpile(CardBehavior):
    name = 'Stockpile'
    tags = []
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        moveable = [c for c in ctx.player.domain if c is not ctx.card]
        if not moveable:
            return
        pick = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, moveable,
            DecisionContext(event="Order", source="Stockpile", intent=Intent.DISCARD))
        ctx.player.remove_from_domain(pick)
        ctx.state.wares.append(pick)
        ctx.state.log(f"  → Stockpile: {ctx.player.name} puts {pick.name} into Wares")
        ctx.engine.order_zone(ctx.player, "coin")


@_register
class Forgery(CardBehavior):
    name = 'Forgery'
    tags = ['Discontent']
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        # Need a coin card in domain to push the forgery
        has_coin = any(c for c in ctx.player.domain
                       if c is not ctx.card and c.deck == "coin")
        if not has_coin:
            return
        ctx.player.remove_from_domain(ctx.card)
        ctx.state.wares.append(ctx.card)
        ctx.state.log(f"  → Forgery: {ctx.player.name} dumps Forgery into Wares")
        ctx.engine.order_zone(ctx.player, "coin")


@_register
class Usurer(CardBehavior):
    name = 'Usurer'
    tags = []
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        moveable = [c for c in ctx.player.domain if c is not ctx.card]
        if not moveable:
            return
        pick = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, moveable,
            DecisionContext(event="Order", source="Usurer", intent=Intent.DISCARD))
        ctx.player.remove_from_domain(pick)
        ctx.state.wares.append(pick)
        ctx.state.log(f"  → Usurer: {ctx.player.name} puts {pick.name} into Wares")

    def on_rumour(self, ctx):
        ctx.state.log(f"  → Usurer: {ctx.player.name} orders Coin zone on Rumour")
        ctx.engine.order_zone(ctx.player, "coin")
        return True


@_register
class Highwaymen(CardBehavior):
    name = 'Highwaymen'
    tags = ['Mob']
    deck = 'coin'
    def on_brawl(self, ctx):
        moveable = [c for c in ctx.player.domain if c is not ctx.card]
        if not moveable or ctx.active_player is None:
            return False
        pick = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, moveable,
            DecisionContext(event="Brawl", source="Highwaymen", intent=Intent.DISCARD))
        ctx.player.remove_from_domain(pick)
        ctx.state.wares.append(pick)
        ctx.state.log(f"  → Highwaymen: {pick.name} goes to Wares")
        ctx.state.log(f"  → Highwaymen: {ctx.active_player.name} orders Coin zone")
        ctx.engine.order_zone(ctx.active_player, "coin")
        return True




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
class WorshipOfGold(CardBehavior):
    name = 'Worship of Gold'
    tags = ['Spiritual']
    deck = 'coin'
    def on_rite(self, ctx):
        if not ctx.state.wares:
            return False
        pick = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, list(ctx.state.wares),
            DecisionContext(event="Rite", source="Worship of Gold", intent=Intent.GAIN))
        ctx.state.wares.remove(pick)
        ctx.active_player.add_to_domain(pick, ctx.state)
        ctx.state.log(f"  → Worship of Gold: {ctx.active_player.name} takes {pick.name} from Wares")
        return True
