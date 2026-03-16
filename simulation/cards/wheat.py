"""Wheat deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Plough(CardBehavior):
    name = 'Plough'
    tags = ['Labour']
    deck = 'wheat'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        if not ctx.player.has_card("Pasture"):
            ctx.state.log(f"  → Drafted: no Pasture → Plough to discard")
            ctx.player.discard.append(ctx.card)
            return
        ctx.player.discard_from_domain(ctx.player.get_card("Pasture"))
        ctx.state.log(f"  → Drafted: discards Pasture to keep Plough")

    def on_event(self, ctx):
        if ctx.event != "Harvest":
            return False
        options = ["feast", "wheat"]
        choice = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, options,
            DecisionContext(Intent.PICK_OPTION, source="Plough",
                            consequence="On Harvest: Feast or activate Wheat zone"))
        if choice == "feast":
            ctx.state.log(f"  → {ctx.player.name}'s Plough: triggers Feast")
            ctx.engine.resolve_event("Feast", ctx.player, ctx.player)
        else:
            if ctx.state.fields:
                ctx.state.log(f"  → {ctx.player.name}'s Plough: activates Wheat zone")
                ctx.engine.activate_wheat_zone(ctx.player)
        return True


@_register
class Granary(CardBehavior):
    name = 'Granary'
    tags = ['Labour']
    deck = 'wheat'
    def can_activate(self, ctx):
        return ctx.location == "domain"

    def on_activate(self, ctx):
        ctx.player.discard_from_domain(ctx.card)
        ctx.state.log(f"  → discards Granary, triggers Feast")
        ctx.engine.resolve_event("Feast", ctx.player, ctx.player)


@_register
class Mill(CardBehavior):
    name = 'Mill'
    tags = ['Labour']
    deck = 'wheat'
    def can_activate(self, ctx):
        return ctx.location == "domain" and ctx.state.pile_remaining("coin") > 0

    def on_activate(self, ctx):
        ctx.player.discard_from_domain(ctx.card)
        coin = ctx.state.draw_from_pile("coin")
        if coin:
            ctx.state.log(f"  → discards Mill, draws {coin.name} from Coin")
            ctx.engine.receive_card(ctx.player, coin)


@_register
class Famine(CardBehavior):
    name = 'Famine'
    tags = []
    deck = 'wheat'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        targets = ctx.state.other_players(ctx.player)
        valid_targets = [p for p in targets if any(c.deck == "wheat" for c in p.domain)]
        if valid_targets:
            target = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, valid_targets,
                DecisionContext(Intent.PICK_TARGET, source="Famine",
                                consequence="they discard 1 Wheat card"))
            wheat_cards = [c for c in target.domain if c.deck == "wheat"]
            if wheat_cards:
                victim = ctx.engine.strat(ctx.player).choose_from(
                    ctx.state, ctx.player, wheat_cards,
                    DecisionContext(Intent.PICK_TARGET, source="Famine",
                                    opponent=target,
                                    consequence=f"{target.name} loses this card"))
                target.discard_from_domain(victim)
                ctx.state.log(f"  → Famine: {target.name} discards {victim.name}")
        ctx.player.discard.append(ctx.card)


@_register
class AnimalHusbandry(CardBehavior):
    name = 'Animal Husbandry'
    tags = ['Labour']
    deck = 'wheat'
    def can_activate(self, ctx):
        return ctx.location == "domain"

    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        if not ctx.player.has_card("Pasture"):
            ctx.state.log(f"  → Drafted: no Pasture → Animal Husbandry to discard")
            ctx.player.discard.append(ctx.card)
            return
        ctx.player.discard_from_domain(ctx.player.get_card("Pasture"))
        ctx.state.log(f"  → Drafted: discards Pasture to keep Animal Husbandry")

    def on_activate(self, ctx):
        options = ["wheat", "coin", "feast"]
        choice = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, options,
            DecisionContext(Intent.PICK_OPTION, source="Animal Husbandry",
                            consequence="Wheat zone, Coin draw, or Feast"))
        if choice == "wheat" and len(ctx.state.fields) > 0:
            ctx.state.log(f"  → activates Wheat zone via AH")
            ctx.engine.activate_wheat_zone(ctx.player)
        elif choice == "coin":
            coin = ctx.state.draw_from_pile("coin")
            if coin:
                ctx.state.log(f"  → draws {coin.name} from Coin via AH")
                ctx.engine.receive_card(ctx.player, coin)
        else:
            ctx.state.log(f"  → triggers Feast via AH")
            ctx.engine.resolve_event("Feast", ctx.player, ctx.player)


@_register
class Tavern(CardBehavior):
    name = 'Tavern'
    tags = ['Amenity']
    deck = 'wheat'
    def on_event(self, ctx):
        if ctx.event != "Feast" or ctx.target is not ctx.player:
            return False
        discontent = ctx.player.cards_with_tag("Discontent")
        if discontent:
            victim = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, discontent,
                DecisionContext(Intent.SACRIFICE, source="Tavern",
                                consequence="discard Discontent (cleanup)"))
            ctx.player.discard_from_domain(victim)
            ctx.state.log(f"  → Tavern: discards {victim.name}")
        return True


@_register
class FeedTheCommoners(CardBehavior):
    name = 'Feed the Commoners'
    tags = []
    deck = 'wheat'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        discontent = ctx.player.cards_with_tag("Discontent")
        if discontent:
            to_discard = ctx.engine.strat(ctx.player).choose_n(
                ctx.state, ctx.player, discontent,
                0, min(3, len(discontent)),
                DecisionContext(Intent.SACRIFICE, source="Feed the Commoners",
                                consequence="discard up to 3 Discontent"))
            for c in to_discard:
                ctx.player.discard_from_domain(c)
                ctx.state.log(f"  → Feed the Commoners discards {c.name}")


@_register
class Apprenticeship(CardBehavior):
    name = 'Apprenticeship'
    tags = ['Labour']
    deck = 'wheat'
    def can_activate(self, ctx):
        if ctx.location != "domain":
            return False
        for p in ctx.state.other_players(ctx.player):
            if p.count_tag("Craftsmanship") > 0:
                return True
        return False

    def on_activate(self, ctx):
        ctx.state.log(f"  → activates Coin zone via Apprenticeship")
        ctx.engine.activate_coin_zone(ctx.player)


@_register
class Militia(CardBehavior):
    name = 'Militia'
    tags = ['Unit']
    deck = 'wheat'
    def can_activate(self, ctx):
        return ctx.location == "domain" and ctx.player.count_tag("Mob") > 0

    def on_activate(self, ctx):
        mobs = ctx.player.cards_with_tag("Mob")
        mob = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, mobs,
            DecisionContext(Intent.SACRIFICE, source="Militia",
                            consequence="discard a Mob from your Domain"))
        ctx.player.discard_from_domain(mob)
        ctx.state.log(f"  → Militia discards {mob.name}")

    def on_event(self, ctx):
        if ctx.event != "Brawl" or ctx.target is not ctx.player:
            return False
        if ctx.engine.strat(ctx.player).choose_yes_no(
                ctx.state, ctx.player,
                DecisionContext(Intent.ACCEPT_REJECT, source="Militia",
                                consequence="sacrifice Militia to cancel Brawl")):
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
    # Well is special — any player can activate it. Handled by engine.
    pass


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
    def on_event(self, ctx):
        if ctx.event != "Rumour":
            return False
        decks = [d for d in ctx.state.piles if ctx.state.pile_remaining(d) > 0]
        if not decks:
            return False
        deck = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, decks,
            DecisionContext(Intent.PICK_OPTION, source="Village Gossip",
                            consequence="peek at top card of a pile"))
        top = ctx.state.peek_pile(deck, 1)
        if top:
            if ctx.engine.strat(ctx.player).choose_yes_no(
                    ctx.state, ctx.player,
                    DecisionContext(Intent.ACCEPT_REJECT, source="Village Gossip",
                                    consequence=f"send {top[0].name} to bottom of {deck}")):
                ctx.state.piles[deck].pop(ctx.state.pile_ptrs[deck])
                ctx.state.piles[deck].append(top[0])
                ctx.state.log(f"  → Village Gossip: {ctx.player.name} sends {top[0].name} to bottom of {deck}")
            else:
                ctx.state.log(f"  → Village Gossip: {ctx.player.name} peeks at {deck} top, leaves it")
        return True
