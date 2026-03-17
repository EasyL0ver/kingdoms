"""Tree deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Highlander(CardBehavior):
    name = 'Highlander'
    tags = ['Culture', 'Trophy']
    deck = 'tree'
    def on_order(self, ctx):
        if ctx.location != "discard" or not ctx.player.has_card("Crags"):
            return
        ctx.player.discard.remove(ctx.card)
        ctx.player.add_to_domain(ctx.card, ctx.state)
        ctx.state.log(f"  → moves Highlander from discard to Domain")

    def on_dawn(self, ctx):
        if not ctx.player.has_card("Crags"):
            ctx.state.log(f"  → Dawn: no Crags → Highlander to discard")
            ctx.player.discard.append(ctx.card)


@_register
class Nomad(CardBehavior):
    name = 'Nomad'
    tags = ['Culture', 'Amenity']
    deck = 'tree'
    def on_order(self, ctx):
        if ctx.location != "discard" or not ctx.player.has_card("Pasture"):
            return
        ctx.player.discard.remove(ctx.card)
        ctx.player.add_to_domain(ctx.card, ctx.state)
        ctx.state.log(f"  → moves Nomad from discard to Domain")

    def on_dawn(self, ctx):
        if not ctx.player.has_card("Pasture"):
            ctx.state.log(f"  → Dawn: no Pasture → Nomad to discard")
            ctx.player.discard.append(ctx.card)


@_register
class Eldership(CardBehavior):
    name = 'Eldership'
    tags = ['Allegiance', 'Knowledge']
    deck = 'tree'
    def on_brawl(self, ctx):
        if ctx.target is not ctx.player:
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
            ctx.state.log(f"  → Rite")
            ctx.engine.resolve_event("Rite", ctx.player)
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
class OralTradition(CardBehavior):
    name = 'Oral Tradition'
    tags = ['Knowledge']
    deck = 'tree'
    def on_order(self, ctx):
        if (ctx.location != "domain"
                or not any(c.deck == "coin" for c in ctx.player.domain)
                or ctx.state.pile_remaining("candle") <= 0):
            return
        coin_cards = [c for c in ctx.player.domain if c.deck == "coin"]
        to_discard = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, coin_cards,
            DecisionContext(event="Order", source="Oral Tradition", intent=Intent.DISCARD))
        ctx.player.discard_from_domain(to_discard)
        candle = ctx.state.draw_from_pile("candle")
        if candle:
            ctx.state.log(f"  → discards {to_discard.name}, draws {candle.name} from Candle")
            ctx.engine.receive_card(ctx.player, candle)


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
class Pasture(CardBehavior):
    name = 'Pasture'
    tags = ['Nature', 'Land']
    deck = 'tree'
    pass  # Passive — no hooks needed


@_register
class Crags(CardBehavior):
    name = 'Crags'
    tags = ['Nature', 'Land']
    deck = 'tree'
    def on_order(self, ctx):
        if ctx.location != "domain" or ctx.state.pile_remaining("claw") <= 0:
            return
        top3 = ctx.state.peek_pile("claw", 3)
        if top3:
            ctx.state.log(f"  → scouts Claw top 3: {', '.join(c.name for c in top3)}")
            if ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, [True, False],
                    DecisionContext(event="Order", source="Crags", intent=Intent.OPTION)):
                pick = ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, top3,
                    DecisionContext(event="Order", source="Crags", intent=Intent.GAIN))
                zone = ctx.state.zone_cards["claw"]
                idx = zone.pile.index(pick)
                zone.pile.pop(idx)
                if idx < zone.pile_ptr:
                    zone.pile_ptr -= 1
                ctx.player.discard.append(pick)
                ctx.state.log(f"  → puts {pick.name} in discard")

    def on_brawl(self, ctx):
        if ctx.target is not ctx.player:
            return False
        crags_count = sum(1 for c in ctx.player.domain if c.name == "Crags")
        if crags_count < 2:
            return False
        if ctx.active_player.domain:
            if ctx.engine.strat(ctx.active_player).resolve(
                    ctx.state, ctx.active_player, [True, False],
                    DecisionContext(event="Brawl", source="Crags", intent=Intent.OPTION)):
                victim = ctx.engine.strat(ctx.active_player).resolve(
                    ctx.state, ctx.active_player, list(ctx.active_player.domain),
                    DecisionContext(event="Brawl", source="Crags", intent=Intent.DISCARD))
                ctx.active_player.discard_from_domain(victim)
                ctx.state.log(f"  → {ctx.active_player.name} discards {victim.name} to overcome Crags defense")
                return False  # Defense paid, Brawl continues
            else:
                ctx.state.log(f"  → Brawl cancelled by Crags defense")
                ctx.engine.cancel_event()
                return True
        else:
            ctx.state.log(f"  → Brawl cancelled by Crags defense (active player has no cards)")
            ctx.engine.cancel_event()
            return True


@_register
class Solstice(CardBehavior):
    name = 'Solstice'
    tags = []
    deck = 'tree'
    def on_harvest(self, ctx):
        options = ["culture_draw", "culture_place"]
        choice = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, options,
            DecisionContext(event="Harvest", source="Solstice", intent=Intent.OPTION))
        if choice == "culture_draw":
            for ally in ctx.state.players:
                if ctx.player.shares_culture(ally) or ally is ctx.player:
                    drawn = ctx.engine.draw_and_receive(ally, "tree")
                    if drawn:
                        ctx.state.log(f"  → Solstice: {ally.name} draws {drawn[0].name} from Tree")
        else:
            culture_cards = [c for c in ctx.player.discard if c.has_tag("Culture")]
            if culture_cards:
                culture = ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, culture_cards,
                    DecisionContext(event="Harvest", source="Solstice", intent=Intent.OPTION))
                target = ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, list(ctx.state.players),
                    DecisionContext(event="Harvest", source="Solstice", intent=Intent.TARGET))
                ctx.player.discard.remove(culture)
                target.add_to_domain(culture, ctx.state)
                ctx.state.log(f"  → Solstice: places {culture.name} in {target.name}'s Domain")
        return True


@_register
class Regrowth(CardBehavior):
    name = 'Regrowth'
    tags = []
    deck = 'tree'
    def on_dawn(self, ctx):
        for p in ctx.state.players:
            pastures = [c for c in p.discard if c.name == "Pasture"]
            for pas in pastures:
                p.discard.remove(pas)
                p.add_to_domain(pas, ctx.state)
                ctx.state.log(f"  → Dawn: Regrowth returns Pasture to {p.name}")
        ctx.discard_self()


@_register
class Forage(CardBehavior):
    name = 'Forage'
    tags = []
    deck = 'tree'
    def on_order(self, ctx):
        if ctx.location != "domain" or ctx.state.pile_remaining("tree") <= 0:
            return
        top3 = []
        for _ in range(3):
            c = ctx.state.draw_from_pile("tree")
            if c:
                top3.append(c)
        if not top3:
            return
        ctx.state.log(f"  → reveals: {', '.join(c.name for c in top3)}")
        for c in top3:
            ctx.player.discard.append(c)
        if ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Order", source="Forage", intent=Intent.OPTION)):
            pick = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, top3,
                DecisionContext(event="Order", source="Forage", intent=Intent.GAIN))
            ctx.player.discard.remove(pick)
            ctx.player.add_to_domain(pick, ctx.state)
            ctx.player.discard_from_domain(ctx.card)
            ctx.state.log(f"  → takes {pick.name}, discards Forage")
        else:
            ctx.state.log(f"  → keeps Forage, all to discard")


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


@_register
class WitheredCrop(CardBehavior):
    name = 'Withered Crop'
    tags = []
    deck = 'tree'
    def on_order(self, ctx):
        if (ctx.location != "domain"
                or not ctx.player.has_discard("Harvest")
                or len(ctx.state.fields) <= 0):
            return
        ctx.state.log(f"  → Orders Wheat zone via Withered Crop")
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
        s = ctx.state
        # Refill Season
        old = len(s.season)
        s.refill_season()
        if len(s.season) > old:
            s.log(f"  → Kinship: Season refilled {old} → {len(s.season)}")
        # Give any Culture cards from Season to a target player
        culture_in_season = [c for c in s.season if c.has_tag("Culture")]
        if culture_in_season:
            targets = list(s.players)
            target = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, targets,
                DecisionContext(event="Harvest", source="Kinship", intent=Intent.TARGET))
            for c in culture_in_season:
                s.season.remove(c)
                ctx.engine.receive_card(target, c)
                s.log(f"  → Kinship: gives {c.name} from Season to {target.name}")
        # Each player sharing culture with owner orders tree zone
        for p in s.other_players(ctx.player):
            if ctx.player.shares_culture(p) and s.season:
                s.log(f"  → Kinship: {p.name} shares culture, orders Tree zone")
                ctx.engine.order_zone(p, "tree")
        return True
