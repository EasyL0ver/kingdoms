"""Wheat deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class AnimalHusbandry(CardBehavior):
    name = 'Animal Husbandry'
    tags = ['Labour']
    deck = 'wheat'

    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        ctx.state.log(f"  → AH: orders Coin zone")
        ctx.engine.order_zone(ctx.player, "coin")
        ctx.state.log(f"  → AH: Feast")
        ctx.engine.resolve_event("Feast", ctx.player, ctx.player)



@_register
class Tavern(CardBehavior):
    name = 'Tavern'
    tags = ['Amenity']
    deck = 'wheat'
    def on_feast(self, ctx):
        s = ctx.state
        acted = False
        # Optionally return 1 Discontent from domain to top of Claw pile
        discontent = ctx.player.cards_with_tag("Discontent")
        if discontent:
            options = discontent + [None]
            pick = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, options,
                DecisionContext(event="Feast", source="Tavern", intent=Intent.DISCARD))
            if pick is not None:
                ctx.player.remove_from_domain(pick)
                s.return_to_pile("claw", pick)
                s.log(f"  → Tavern: returns {pick.name} to top of Claw pile")
                acted = True
        # Optionally return 1 Claw card from discard to top of Claw pile
        claw_in_discard = [c for c in ctx.player.discard if c.deck == "claw"]
        if claw_in_discard:
            options = claw_in_discard + [None]
            pick = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, options,
                DecisionContext(event="Feast", source="Tavern", intent=Intent.DISCARD))
            if pick is not None:
                ctx.player.discard.remove(pick)
                s.return_to_pile("claw", pick)
                s.log(f"  → Tavern: returns {pick.name} from discard to top of Claw pile")
                acted = True
        return acted



@_register
class Militia(CardBehavior):
    name = 'Militia'
    tags = ['Unit']
    deck = 'wheat'
    def on_rumour(self, ctx):
        mobs = ctx.player.cards_with_tag("Mob")
        if not mobs:
            return False
        mob = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, mobs,
            DecisionContext(event="Rumour", source="Militia", intent=Intent.DISCARD))
        ctx.player.discard_from_domain(mob)
        ctx.state.log(f"  → Militia kills {mob.name}")
        return True

    def on_brawl(self, ctx):
        if ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Brawl", source="Militia", intent=Intent.OPTION)):
            ctx.player.discard_from_domain(ctx.card)
            ctx.state.log(f"  → Militia cancels Brawl (Militia discarded)")
            ctx.engine.cancel_event()
            return True
        return False



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
class CrookedInn(CardBehavior):
    name = 'Crooked Inn'
    tags = ['Amenity', 'Discontent']
    deck = 'wheat'

    def on_rumour(self, ctx):
        # Return 1 Mob from discard to domain
        mobs = [c for c in ctx.player.discard if c.has_tag("Mob")]
        if not mobs:
            return False
        mob = mobs[0]
        ctx.player.discard.remove(mob)
        ctx.player.add_to_domain(mob, ctx.state)
        ctx.state.log(f"  → Crooked Inn: {mob.name} crawls back to {ctx.player.name}'s domain")
        return True


@_register
class Enclosure(CardBehavior):
    name = 'Enclosure'
    tags = ['Labour', 'Amenity']
    deck = 'wheat'

    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        village = ctx.state.fields
        if not village:
            return False
        # Pick any card from the Village
        pick = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(village),
            f"Enclosure: take which card from Village?"
        )
        idx = village.index(pick)
        village.remove(pick)
        ctx.player.add_to_domain(pick, ctx.state)
        ctx.state.log(f"  → Enclosure: takes {pick.name} from Village")
        # Put a card from domain back into the same slot
        returnable = [c for c in ctx.player.domain if c is not ctx.card and c is not pick]
        if returnable:
            give_back = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, returnable + [None],
                f"Enclosure: put which card back into Village?"
            )
            if give_back is not None:
                ctx.player.remove_from_domain(give_back)
                village.insert(min(idx, len(village)), give_back)
                ctx.state.log(f"  → Enclosure: puts {give_back.name} back into Village")
        return True


@_register
class TurnipPatch(CardBehavior):
    name = 'Turnip Patch'
    tags = ['Labour']
    deck = 'wheat'

    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        ctx.state.log(f"  → Turnip Patch: orders Village")
        ctx.engine.order_zone(ctx.player, "wheat")
        return True

    def on_harvest(self, ctx):
        ctx.state.log(f"  → Turnip Patch: orders Village")
        ctx.engine.order_zone(ctx.player, "wheat")
        return True


@_register
class RitualPyre(CardBehavior):
    name = 'Ritual Pyre'
    tags = ['Nature', 'Spiritual']
    deck = 'wheat'

    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        # Sacrifice any card from domain
        targets = [c for c in ctx.player.domain if c is not ctx.card]
        if not targets:
            return False
        victim = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, targets + [None],
            f"Ritual Pyre: sacrifice which card?"
        )
        if victim is None:
            return False
        ctx.player.discard_from_domain(victim)
        ctx.state.log(f"  → Ritual Pyre: {ctx.player.name} sacrifices {victim.name}")
        ctx.state.log(f"  → Ritual Pyre: Harvest!")
        ctx.engine.resolve_event("Harvest", ctx.player, ctx.player)
        ctx.state.log(f"  → Ritual Pyre: Rite!")
        ctx.engine.resolve_event("Rite", ctx.player, ctx.player)
        return True


@_register
class FolkHero(CardBehavior):
    name = 'Folk Hero'
    tags = ['Unit', 'Trophy']
    deck = 'wheat'

    def on_dawn(self, ctx):
        # Move 1 Mob or Wheat card between domains that have wheat
        wheat_domains = [p for p in ctx.state.players
                         if any(c.deck == "wheat" for c in p.domain)]
        sources = []
        for p in wheat_domains:
            for c in p.domain:
                if c is ctx.card:
                    continue
                if c.has_tag("Mob") or c.has_tag("Labour") or c.has_tag("Amenity"):
                    sources.append((p, c))
        if not sources:
            return False
        chosen = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, sources + [None],
            f"Folk Hero: move a card? (from_player, card)"
        )
        if chosen is None:
            return False
        source_player, card = chosen
        targets = [p for p in wheat_domains if p is not source_player]
        if not targets:
            return False
        target = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, targets,
            f"Folk Hero: send {card.name} to?"
        )
        source_player.remove_from_domain(card)
        target.add_to_domain(card, ctx.state)
        ctx.state.log(f"  → Folk Hero: moves {card.name} from {source_player.name} to {target.name}")
        return True


@_register
class HerbGarden(CardBehavior):
    name = 'Herb Garden'
    tags = ['Nature']
    deck = 'wheat'

    def on_harvest(self, ctx):
        zone = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, ["tree", "wheat"],
            f"Herb Garden: order Tree or Village?"
        )
        ctx.state.log(f"  → Herb Garden: {ctx.player.name} orders {zone}")
        ctx.engine.order_zone(ctx.player, zone)
        return True


@_register
class WolfPack(CardBehavior):
    name = 'Wolf Pack'
    tags = ['Mob', 'Nature', 'Discontent']
    deck = 'wheat'

    def on_harvest(self, ctx):
        if ctx.active_player == ctx.player:
            # You control the wolves — move them to an enemy
            others = [p for p in ctx.state.players if p is not ctx.player]
            if not others:
                return False
            target = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, others,
                f"Wolf Pack: send to which player?"
            )
            ctx.player.remove_from_domain(ctx.card)
            target.add_to_domain(ctx.card, ctx.state)
            ctx.state.log(f"  → Wolf Pack: {ctx.player.name} sends wolves to {target.name}")
            return True
        else:
            # Wolves ravage your domain
            ctx.state.log(f"  → Wolf Pack: wolves ravage {ctx.player.name}'s domain!")
            # Discard 2 from domain
            targets = [c for c in ctx.player.domain if c is not ctx.card]
            to_discard = min(2, len(targets))
            for _ in range(to_discard):
                targets = [c for c in ctx.player.domain if c is not ctx.card]
                if not targets:
                    break
                victim = ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, targets,
                    f"Wolf Pack: discard which card?"
                )
                ctx.player.discard_from_domain(victim)
                ctx.state.log(f"  → Wolf Pack: wolves destroy {victim.name}")
            # Draw 2 Claw
            drawn = ctx.engine.draw_and_receive(ctx.player, "claw", 2)
            names = [c.name for c in drawn] if drawn else []
            ctx.state.log(f"  → Wolf Pack: draws {len(names)} Claw: {names}")
            return True


@_register
class Orchard(CardBehavior):
    name = 'Orchard'
    tags = ['Nature', 'Labour']
    deck = 'wheat'

    def on_harvest(self, ctx):
        drawn = ctx.engine.draw_and_receive(ctx.player, "tree", 1)
        if drawn:
            ctx.state.log(f"  → Orchard: {ctx.player.name} draws {drawn[0].name} from Tree")
        ctx.state.log(f"  → Orchard: Feast")
        ctx.engine.resolve_event("Feast", ctx.player, ctx.player)
        return True


@_register
class Reeve(CardBehavior):
    name = 'Reeve'
    tags = ['Unit']
    deck = 'wheat'

    def on_dawn(self, ctx):
        # Pick a wheat card in domain to fire its on_order
        wheat_cards = [c for c in ctx.player.domain
                       if c.deck == "wheat" and c is not ctx.card]
        if not wheat_cards:
            return False
        pick = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, wheat_cards + [None],
            f"Reeve: order which wheat card?"
        )
        if pick is None:
            return False
        ctx.state.log(f"  → Reeve: {ctx.player.name} orders {pick.name}")
        ctx.engine.resolve_event("Order", ctx.player, pick)
        return True



@_register
class TaxCollectors(CardBehavior):
    name = 'Tax Collectors'
    tags = ['Mob', 'Discontent']
    deck = 'wheat'

    def on_order(self, ctx):
        """Collect tax — requires 3+ Labour tags in domain."""
        if ctx.location != "domain":
            return
        if ctx.player.count_tag("Labour") < 3:
            return
        ctx.state.log(f"  → Tax Collectors: {ctx.player.name} collects tax (3+ Labour)")
        ctx.engine.order_zone(ctx.player, "coin")
        ctx.state.log(f"  → Tax Collectors: Rumour!")
        ctx.engine.resolve_event("Rumour", ctx.player, ctx.player)
        return True


@_register
class Lookout(CardBehavior):
    name = 'Lookout'
    tags = []
    deck = 'wheat'
    def on_dawn(self, ctx):
        if ctx.player.count_tag("Discontent") > 0:
            ctx.state.log(f"  → Lookout: spots trouble, spreads Rumour locally")
            ctx.engine.resolve_event("Rumour", ctx.player, scope=ctx.player)
            return True
        return False


@_register
class IllTidings(CardBehavior):
    name = 'Ill Tidings'
    tags = []
    deck = 'wheat'
    def on_rumour(self, ctx):
        options = ["panic", "fortify"]
        choice = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, options,
            DecisionContext(event="Rumour", source="Ill Tidings", intent=Intent.OPTION))
        if choice == "panic":
            drawn = ctx.engine.draw_and_receive(ctx.player, "claw", 2)
            names = ", ".join(c.name for c in drawn) if drawn else "nothing"
            ctx.state.log(f"  → Ill Tidings: PANIC! {ctx.player.name} draws {names} from Claw")
        else:
            discontent = ctx.player.cards_with_tag("Discontent")
            if discontent:
                victim = ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, discontent,
                    DecisionContext(event="Rumour", source="Ill Tidings", intent=Intent.DISCARD))
                ctx.player.remove_from_domain(victim)
                ctx.state.return_to_pile("claw", victim)
                ctx.state.log(f"  → Ill Tidings: FORTIFY! {ctx.player.name} returns {victim.name} to Claw pile")
            else:
                ctx.state.log(f"  → Ill Tidings: FORTIFY! No Discontent to return")
        # One-shot: discard after use
        ctx.player.discard_from_domain(ctx.card)
        ctx.state.log(f"  → Ill Tidings: discarded")
        return True


@_register
class OraEtLabora(CardBehavior):
    name = 'Ora et Labora'
    tags = ['Labour', 'Spiritual']
    deck = 'wheat'

    def on_harvest(self, ctx):
        ctx.state.log(f"  → Ora et Labora: {ctx.player.name} prays — orders Candle")
        ctx.engine.order_zone(ctx.player, "candle")
        return True

    def on_rite(self, ctx):
        ctx.state.log(f"  → Ora et Labora: {ctx.player.name} works — orders Village")
        ctx.engine.order_zone(ctx.player, "wheat")
        return True


@_register
class WorshipOfTheBread(CardBehavior):
    name = 'Worship of the Bread'
    tags = ['Spiritual']
    deck = 'wheat'

    def on_rite(self, ctx):
        village = ctx.state.fields
        if len(village) < 2:
            return False
        # Rearrange the Village belt
        ordered = []
        remaining = list(village)
        for _ in range(len(remaining)):
            pick = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, remaining,
                f"Worship of the Bread: place next in Village (bottom first)"
            )
            ordered.append(pick)
            remaining.remove(pick)
        village.clear()
        village.extend(ordered)
        ctx.state.log(f"  → Worship of the Bread: rearranges Village")
        return True


@_register
class Pilgrimage(CardBehavior):
    name = 'Pilgrimage'
    tags = ['Spiritual']
    deck = 'wheat'

    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        giveable = [c for c in ctx.player.domain if c is not ctx.card]
        targets = ctx.state.other_players(ctx.player)
        if not giveable or not targets:
            ctx.player.discard_from_domain(ctx.card)
            return
        target = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, targets,
            DecisionContext(event="Order", source="Pilgrimage", intent=Intent.TARGET))
        to_give = ctx.engine.strat(ctx.player).resolve_n(
            ctx.state, ctx.player, giveable,
            1, len(giveable),
            DecisionContext(event="Order", source="Pilgrimage", intent=Intent.GIVE_AWAY))
        for c in to_give:
            ctx.player.remove_from_domain(c)
            target.add_to_domain(c, ctx.state)
        n = len(to_give)
        names = ", ".join(c.name for c in to_give)
        ctx.state.log(f"  → Pilgrimage: gives {names} to {target.name}")
        # Target decides if pilgrim gets rewarded
        accept = ctx.engine.strat(target).resolve(
            ctx.state, target, [True, False],
            f"Pilgrimage: {ctx.player.name} gave you {names}. Reward them with {n} Candle?")
        if accept:
            ctx.state.log(f"  → Pilgrimage: {target.name} accepts — draws {n} Candle")
            drawn = ctx.engine.draw_and_receive(ctx.player, "candle", n)
            if drawn:
                ctx.state.log(f"    receives {', '.join(c.name for c in drawn)}")
        else:
            ctx.state.log(f"  → Pilgrimage: {target.name} refuses — no reward")
        ctx.player.discard_from_domain(ctx.card)
