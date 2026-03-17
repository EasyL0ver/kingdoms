"""Wheat deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Plough(CardBehavior):
    name = 'Plough'
    tags = ['Labour']
    deck = 'wheat'

    def on_order(self, ctx):
        if ctx.location != "domain" or not ctx.state.fields:
            return
        # Optionally sacrifice a Pasture for double wheat order
        pastures = [c for c in ctx.player.domain if c.name == "Pasture"]
        double = False
        if pastures:
            if ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, [True, False],
                    DecisionContext(event="Order", source="Plough", intent=Intent.OPTION)):
                ctx.player.discard_from_domain(pastures[0])
                ctx.state.log(f"  → Plough: sacrifices Pasture for double wheat order")
                double = True
        ctx.engine.order_zone(ctx.player, "wheat")
        if double and ctx.state.fields:
            ctx.engine.order_zone(ctx.player, "wheat")

    def on_harvest(self, ctx):
        options = ["feast", "wheat"]
        choice = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, options,
            DecisionContext(event="Harvest", source="Plough", intent=Intent.OPTION))
        if choice == "feast":
            ctx.state.log(f"  → {ctx.player.name}'s Plough: Feast")
            ctx.engine.resolve_event("Feast", ctx.player, ctx.player)
        else:
            if ctx.state.fields:
                ctx.state.log(f"  → {ctx.player.name}'s Plough: Orders Wheat zone")
                ctx.engine.order_zone(ctx.player, "wheat")
        return True


@_register
class Granary(CardBehavior):
    name = 'Granary'
    tags = ['Labour']
    deck = 'wheat'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        ctx.player.discard_from_domain(ctx.card)
        ctx.state.log(f"  → discards Granary, Feast")
        ctx.engine.resolve_event("Feast", ctx.player, ctx.player)


@_register
class Mill(CardBehavior):
    name = 'Mill'
    tags = ['Labour']
    deck = 'wheat'
    def on_order(self, ctx):
        if ctx.location != "domain" or ctx.state.pile_remaining("coin") <= 0:
            return
        ctx.player.discard_from_domain(ctx.card)
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → discards Mill, draws {drawn[0].name} from Coin")


@_register
class Famine(CardBehavior):
    name = 'Famine'
    tags = []
    deck = 'wheat'
    def on_dawn(self, ctx):
        targets = ctx.state.other_players(ctx.player)
        valid_targets = [p for p in targets if any(c.deck == "wheat" for c in p.domain)]
        if valid_targets:
            target = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, valid_targets,
                DecisionContext(event="Dawn", source="Famine", intent=Intent.TARGET))
            wheat_cards = [c for c in target.domain if c.deck == "wheat"]
            if wheat_cards:
                victim = ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, wheat_cards,
                    DecisionContext(event="Dawn", source="Famine", intent=Intent.TARGET))
                target.discard_from_domain(victim)
                ctx.state.log(f"  → Famine: {target.name} discards {victim.name}")
        ctx.discard_self()


@_register
class AnimalHusbandry(CardBehavior):
    name = 'Animal Husbandry'
    tags = ['Labour']
    deck = 'wheat'

    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        options = ["wheat", "coin", "feast"]
        choice = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, options,
            DecisionContext(event="Order", source="Animal Husbandry", intent=Intent.OPTION))
        # Optionally sacrifice a Pasture to draw 2 from chosen pile
        pastures = [c for c in ctx.player.domain if c.name == "Pasture"]
        double = False
        if pastures:
            if ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, [True, False],
                    DecisionContext(event="Order", source="Animal Husbandry", intent=Intent.OPTION)):
                ctx.player.discard_from_domain(pastures[0])
                ctx.state.log(f"  → AH: sacrifices Pasture")
                double = True
        if choice == "wheat" and len(ctx.state.fields) > 0:
            ctx.state.log(f"  → Orders Wheat zone via AH")
            ctx.engine.order_zone(ctx.player, "wheat")
            if double and ctx.state.fields:
                ctx.engine.order_zone(ctx.player, "wheat")
        elif choice == "coin":
            coin = ctx.state.draw_from_pile("coin")
            if coin:
                ctx.state.log(f"  → draws {coin.name} from Coin via AH")
                ctx.engine.receive_card(ctx.player, coin)
            if double:
                coin2 = ctx.state.draw_from_pile("coin")
                if coin2:
                    ctx.state.log(f"  → draws {coin2.name} from Coin via AH (bonus)")
                    ctx.engine.receive_card(ctx.player, coin2)
        else:
            ctx.state.log(f"  → Feast via AH")
            ctx.engine.resolve_event("Feast", ctx.player, ctx.player)
            if double:
                ctx.state.log(f"  → Feast via AH (bonus)")
                ctx.engine.resolve_event("Feast", ctx.player, ctx.player)


@_register
class Tavern(CardBehavior):
    name = 'Tavern'
    tags = ['Amenity']
    deck = 'wheat'
    def on_feast(self, ctx):
        if ctx.target is not ctx.player:
            return False
        discontent = ctx.player.cards_with_tag("Discontent")
        if discontent:
            victim = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, discontent,
                DecisionContext(event="Feast", source="Tavern", intent=Intent.DISCARD))
            ctx.player.remove_from_domain(victim)
            ctx.state.return_to_pile("claw", victim)
            ctx.state.log(f"  → Tavern: returns {victim.name} to claw pile")
        return True


@_register
class FeedTheCommoners(CardBehavior):
    name = 'Feed the Commoners'
    tags = []
    deck = 'wheat'
    def on_dawn(self, ctx):
        discontent = ctx.player.cards_with_tag("Discontent")
        if discontent:
            to_return = ctx.engine.strat(ctx.player).resolve_n(
                ctx.state, ctx.player, discontent,
                0, min(3, len(discontent)),
                DecisionContext(event="Dawn", source="Feed the Commoners", intent=Intent.DISCARD))
            for c in to_return:
                ctx.player.remove_from_domain(c)
                ctx.state.return_to_pile("claw", c)
                ctx.state.log(f"  → Feed the Commoners returns {c.name} to claw pile")
        ctx.discard_self()


@_register
class Apprenticeship(CardBehavior):
    name = 'Apprenticeship'
    tags = ['Labour']
    deck = 'wheat'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        if not any(p.count_tag("Craftsmanship") > 0 for p in ctx.state.other_players(ctx.player)):
            return
        ctx.state.log(f"  → Orders Coin zone via Apprenticeship")
        ctx.engine.order_zone(ctx.player, "coin")


@_register
class Militia(CardBehavior):
    name = 'Militia'
    tags = ['Unit']
    deck = 'wheat'
    def on_order(self, ctx):
        if ctx.location != "domain" or ctx.player.count_tag("Mob") <= 0:
            return
        mobs = ctx.player.cards_with_tag("Mob")
        mob = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, mobs,
            DecisionContext(event="Order", source="Militia", intent=Intent.DISCARD))
        ctx.player.discard_from_domain(mob)
        ctx.state.log(f"  → Militia discards {mob.name}")

    def on_brawl(self, ctx):
        if ctx.target is not ctx.player:
            return False
        if ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Brawl", source="Militia", intent=Intent.OPTION)):
            ctx.player.discard_from_domain(ctx.card)
            ctx.state.log(f"  → Militia cancels Brawl (Militia discarded)")
            ctx.engine.cancel_event()
            return True
        return False


@_register
class Well(CardBehavior):
    name = 'Well'
    tags = ['Amenity']
    deck = 'wheat'

    def on_order(self, ctx):
        if not ctx.state.season:
            return
        tree_zone = ctx.state.zone_cards["tree"]
        tree_beh = ctx.engine.behavior(tree_zone)
        ctx.state.log("  → Orders Well (Tree zone ×2)")
        for _ in range(2):
            tree_ctx = ctx.engine.make_ctx(ctx.player, tree_zone)
            tree_beh.on_order(tree_ctx)


@_register
class Maypole(CardBehavior):
    name = 'Maypole'
    tags = ['Amenity']
    deck = 'wheat'
    pass  # Pure [Amenity] tag, no effects


@_register
class VillageGossip(CardBehavior):
    name = 'Village Gossip'
    tags = []
    deck = 'wheat'
    def on_rumour(self, ctx):
        decks = [d for d in ctx.state.zone_cards if ctx.state.pile_remaining(d) > 0]
        if not decks:
            return False
        deck = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, decks,
            DecisionContext(event="Rumour", source="Village Gossip", intent=Intent.OPTION))
        top = ctx.state.peek_pile(deck, 1)
        if top:
            if ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, [True, False],
                    DecisionContext(event="Rumour", source="Village Gossip", intent=Intent.OPTION)):
                zone = ctx.state.zone_cards[deck]
                zone.pile.pop(zone.pile_ptr)
                zone.pile.append(top[0])
                ctx.state.log(f"  → Village Gossip: {ctx.player.name} sends {top[0].name} to bottom of {deck}")
            else:
                ctx.state.log(f"  → Village Gossip: {ctx.player.name} peeks at {deck} top, leaves it")
        return True


@_register
class Orchard(CardBehavior):
    name = 'Orchard'
    tags = ['Nature', 'Land']
    deck = 'wheat'

    def on_order(self, ctx):
        if ctx.location != "domain" or not ctx.state.fields:
            return
        card = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.state.fields),
            DecisionContext(event="Order", source="Orchard", intent=Intent.GAIN))
        if card and card in ctx.state.fields:
            ctx.state.fields.remove(card)
            ctx.engine.receive_card(ctx.player, card)
            ctx.state.log(f"  → Orchard: {ctx.player.name} picks {card.name} from Fields (no tax)")


@_register
class Stewardship(CardBehavior):
    name = 'Stewardship'
    tags = []
    deck = 'wheat'

    def on_dawn(self, ctx):
        options = []
        if ctx.state.fields:
            options.append("wheat")
        if ctx.state.season:
            options.append("tree")
        if not options:
            return
        choice = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, options,
            DecisionContext(event="Dawn", source="Stewardship", intent=Intent.OPTION))
        ctx.state.log(f"  → Stewardship: {ctx.player.name} orders {choice} zone")
        ctx.engine.order_zone(ctx.player, choice)
