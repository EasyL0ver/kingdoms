"""Tree deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Eldership(CardBehavior):
    name = 'Eldership'
    tags = ['Knowledge']
    deck = 'tree'
    def on_brawl(self, ctx):
        if ctx.active_player is ctx.player:
            return False
        if not ctx.active_player.shares_culture(ctx.player):
            return False
        if ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Brawl", source="Eldership", intent=Intent.OPTION)):
            drawn = ctx.engine.draw_and_receive(ctx.active_player, "tree")
            if drawn:
                ctx.state.log(f"  → Eldership cancels Brawl. {ctx.active_player.name} draws {drawn[0].name}")
            else:
                ctx.state.log(f"  → Eldership cancels Brawl")
            ctx.engine.cancel_event()
            return True
        return False


@_register
class SkyDance(CardBehavior):
    name = 'Sky Dance'
    tags = ['Spiritual']
    deck = 'tree'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        ctx.state.log(f"  → Rite")
        ctx.engine.resolve_event("Rite", ctx.player)


@_register
class Harvest(CardBehavior):
    name = 'Harvest'
    tags = []
    deck = 'tree'
    def on_dawn(self, ctx):
        ctx.state.log(f"  → Dawn: Harvest triggers!")
        ctx.engine.resolve_event("Harvest", ctx.player)
        ctx.discard_self()


@_register
class Gathering(CardBehavior):
    name = 'Gathering'
    tags = []
    deck = 'tree'
    def on_dawn(self, ctx):
        options = ["brawl", "rite"]
        choice = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, options,
            DecisionContext(event="Dawn", source="Gathering", intent=Intent.OPTION))
        if choice == "brawl":
            ctx.state.log(f"  → Gathering: Brawl in {ctx.player.name}'s Domain")
            ctx.engine.resolve_event("Brawl", ctx.player, ctx.player)
            for p in ctx.state.other_players(ctx.player):
                if ctx.player.shares_culture(p):
                    ctx.state.log(f"  → Gathering: Brawl also in {p.name}'s Domain (shared culture)")
                    ctx.engine.resolve_event("Brawl", ctx.player, p)
        else:
            ctx.state.log(f"  → Gathering: Rite in {ctx.player.name}'s Domain")
            ctx.engine.resolve_event("Rite", ctx.player)
        ctx.discard_self()


@_register
class SacredGrove(CardBehavior):
    name = 'Sacred Grove'
    tags = ['Nature', 'Spiritual']
    deck = 'tree'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        options = ["rite", "scry"]
        choice = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, options,
            DecisionContext(event="Order", source="Sacred Grove", intent=Intent.OPTION))
        if choice == "rite":
            ctx.state.log(f"  → Sacred Grove: local Rite")
            ctx.engine.resolve_event("Rite", ctx.player, scope=ctx.player)
        else:
            top3 = ctx.state.peek_pile("tree", 3)
            spiritual = [c for c in top3 if c.has_tag("Spiritual")]
            if spiritual:
                for sc in spiritual:
                    ctx.state.zone_cards["tree"].pile_ptr += 1
                    ctx.player.add_to_domain(sc, ctx.state)
                    ctx.state.log(f"  → takes {sc.name} (Spiritual) from Tree top")
                remaining = [c for c in top3 if c not in spiritual]
                for c in remaining:
                    ctx.state.zone_cards["tree"].pile_ptr += 1
                if remaining:
                    zone = ctx.state.zone_cards["tree"]
                    ptr = zone.pile_ptr
                    for i, c in enumerate(remaining):
                        zone.pile.insert(ptr - len(remaining) + i, c)
                    zone.pile_ptr -= len(remaining)
            else:
                ctx.state.log(f"  → scries top 3 Tree: {', '.join(c.name for c in top3)}. No Spiritual found.")



@_register
class Herbalism(CardBehavior):
    name = 'Herbalism'
    tags = ['Knowledge']
    deck = 'tree'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        has_cost = any(c.has_tag("Knowledge") or c.has_tag("Nature")
                       for c in ctx.player.domain if c is not ctx.card)
        if not has_cost or len(ctx.player.discard) <= 0:
            return
        costs = [c for c in ctx.player.domain
                 if (c.has_tag("Knowledge") or c.has_tag("Nature")) and c is not ctx.card]
        cost_card = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, costs,
            DecisionContext(event="Order", source="Herbalism", intent=Intent.DISCARD))
        ctx.player.discard_from_domain(cost_card)
        target_card = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.player.discard),
            DecisionContext(event="Order", source="Herbalism", intent=Intent.GAIN))
        ctx.player.discard.remove(target_card)
        ctx.player.add_to_domain(target_card, ctx.state)
        ctx.state.log(f"  → discards {cost_card.name}, recovers {target_card.name} from discard")


@_register
class WorshipOfTheRain(CardBehavior):
    name = 'Worship of the Rain'
    tags = ['Spiritual']
    deck = 'tree'
    def on_rite(self, ctx):
        if not ctx.state.season:
            return False
        to_discard = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, list(ctx.state.season),
            DecisionContext(event="Rite", source="Worship of the Rain", intent=Intent.OPTION))
        ctx.state.season.remove(to_discard)
        replacement = ctx.state.draw_from_pile("tree")
        if replacement:
            ctx.state.season.append(replacement)
            ctx.state.log(f"  → Worship of the Rain: swaps {to_discard.name} → {replacement.name}")
        else:
            ctx.state.log(f"  → Worship of the Rain: removed {to_discard.name}, no replacement")
        return True


@_register
class WorshipOfFertility(CardBehavior):
    name = 'Worship of Fertility'
    tags = ['Nature', 'Spiritual']
    deck = 'tree'
    def on_rite(self, ctx):
        ctx.state.log(f"  → {ctx.player.name}'s Worship of Fertility: triggers Harvest for {ctx.active_player.name}")
        ctx.engine.resolve_event("Harvest", ctx.active_player)
        return True


@_register
class Forage(CardBehavior):
    name = 'Forage'
    tags = []
    deck = 'tree'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        dumped = []
        for _ in range(2):
            c = ctx.state.draw_from_pile("tree")
            if c:
                ctx.player.discard.append(c)
                dumped.append(c)
        for _ in range(2):
            c = ctx.state.draw_from_pile("claw")
            if c:
                ctx.player.discard.append(c)
                dumped.append(c)
        if dumped:
            ctx.state.log(f"  → Forage dumps {', '.join(c.name for c in dumped)} to discard")
        ctx.engine.resolve_event("Feast", ctx.player, ctx.player)
        ctx.state.log(f"  → Forage triggers Feast")


@_register
class Sowing(CardBehavior):
    name = 'Sowing'
    tags = ['Knowledge']
    deck = 'tree'
    def on_order(self, ctx):
        if (ctx.location != "domain"
                or ctx.player.count_tag("Nature") < 2
                or len(ctx.state.fields) <= 0):
            return
        ctx.state.log(f"  → Orders Wheat zone via Sowing")
        ctx.engine.order_zone(ctx.player, "wheat")

    def on_harvest(self, ctx):
        s = ctx.state
        old_count = len(s.fields)
        s.refill_fields()
        if len(s.fields) > old_count:
            s.log(f"  → Sowing: Fields refilled {old_count} → {len(s.fields)}")
        return True


@_register
class WitheredCrop(CardBehavior):
    name = 'Withered Crop'
    tags = []
    deck = 'tree'
    def on_order(self, ctx):
        if ctx.location != "domain" or not ctx.player.discard:
            return
        to_exile = ctx.engine.strat(ctx.player).resolve_n(
            ctx.state, ctx.player, list(ctx.player.discard),
            1, len(ctx.player.discard),
            DecisionContext(event="Order", source="Withered Crop", intent=Intent.DISCARD))
        for c in to_exile:
            ctx.player.discard.remove(c)
        ctx.state.log(f"  → Withered Crop: exiles {len(to_exile)} cards, restocks fields")
        old = len(ctx.state.fields)
        ctx.state.refill_fields(old + len(to_exile))
        new = len(ctx.state.fields)
        if new > old:
            ctx.state.log(f"  → Fields refilled {old} → {new}")
        if ctx.state.fields:
            ctx.engine.order_zone(ctx.player, "wheat")


@_register
class Remembrance(CardBehavior):
    name = 'Remembrance'
    tags = ['Knowledge']
    deck = 'tree'
    def on_order(self, ctx):
        if (ctx.location != "domain"
                or ctx.player.count_tag("Knowledge") <= 0
                or len(ctx.player.discard) <= 0):
            return
        knowledge_count = ctx.player.count_tag("Knowledge")
        to_recover = ctx.engine.strat(ctx.player).resolve_n(
            ctx.state, ctx.player, list(ctx.player.discard),
            1, min(knowledge_count, len(ctx.player.discard)),
            DecisionContext(event="Order", source="Remembrance", intent=Intent.GAIN))
        for c in to_recover:
            ctx.player.discard.remove(c)
            ctx.player.add_to_domain(c, ctx.state)
            ctx.state.log(f"  → recovers {c.name} from discard")


@_register
class Kinship(CardBehavior):
    name = 'Kinship'
    tags = []
    deck = 'tree'
    def on_harvest(self, ctx):
        ctx.state.log(f"  → Kinship: {ctx.player.name} orders Tree zone")
        ctx.engine.order_zone(ctx.player, "tree")
        return True


@_register
class Pilgrimage(CardBehavior):
    name = 'Pilgrimage'
    tags = ['Spiritual']
    deck = 'tree'

    def _claim_revelation(self, ctx):
        s = ctx.state
        if not s.revelation:
            return
        rev_card = s.revelation.pop(0)
        ctx.player.add_to_domain(rev_card, s)
        s.log(f"  → Pilgrimage: {ctx.player.name} claims Revelation ({rev_card.name})")
        from cards import get_behavior
        get_behavior("Candle Zone").refill(s)

    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        self._claim_revelation(ctx)

    def on_rite(self, ctx):
        self._claim_revelation(ctx)
        return True
