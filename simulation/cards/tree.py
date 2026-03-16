"""Tree deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Highlander(CardBehavior):
    name = 'Highlander'
    tags = ['Culture']
    deck = 'tree'
    def can_activate(self, ctx):
        return ctx.location == "discard" and ctx.player.has_card("Crags")

    def on_activate(self, ctx):
        ctx.player.discard.remove(ctx.card)
        ctx.player.add_to_domain(ctx.card, ctx.state)
        ctx.state.log(f"  → moves Highlander from discard to Domain")

    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc == "pile" and not ctx.player.has_card("Crags"):
            ctx.state.log(f"  → Drafted: no Crags → Highlander to discard")
            ctx.player.discard.append(ctx.card)


@_register
class Nomad(CardBehavior):
    name = 'Nomad'
    tags = ['Culture']
    deck = 'tree'
    def can_activate(self, ctx):
        return ctx.location == "discard" and ctx.player.has_card("Pasture")

    def on_activate(self, ctx):
        ctx.player.discard.remove(ctx.card)
        ctx.player.add_to_domain(ctx.card, ctx.state)
        ctx.state.log(f"  → moves Nomad from discard to Domain")

    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc == "pile" and not ctx.player.has_card("Pasture"):
            ctx.state.log(f"  → Drafted: no Pasture → Nomad to discard")
            ctx.player.discard.append(ctx.card)


@_register
class Eldership(CardBehavior):
    name = 'Eldership'
    tags = ['Allegiance', 'Knowledge']
    deck = 'tree'
    def on_event(self, ctx):
        if ctx.event != "Brawl" or ctx.target is not ctx.player:
            return False
        if not ctx.triggerer.shares_culture(ctx.player):
            return False
        if ctx.engine.strat(ctx.player).choose_yes_no(
                ctx.state, ctx.player,
                DecisionContext(Intent.ACCEPT_REJECT, source="Eldership",
                                opponent=ctx.triggerer,
                                consequence="cancel Brawl, triggerer draws Tree")):
            tree = ctx.state.draw_from_pile("tree")
            if tree:
                ctx.state.log(f"  → Eldership cancels Brawl. {ctx.triggerer.name} draws {tree.name}")
                ctx.engine.receive_card(ctx.triggerer, tree)
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
    def can_activate(self, ctx):
        return ctx.location == "domain"

    def on_activate(self, ctx):
        ctx.state.log(f"  → triggers Rite")
        ctx.engine.resolve_event("Rite", ctx.player)


@_register
class Harvest(CardBehavior):
    name = 'Harvest'
    tags = []
    deck = 'tree'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        ctx.state.log(f"  → Drafted: Harvest triggers!")
        ctx.engine.resolve_event("Harvest", ctx.player)
        ctx.player.discard.append(ctx.card)


@_register
class Gathering(CardBehavior):
    name = 'Gathering'
    tags = []
    deck = 'tree'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        options = ["brawl", "rite"]
        choice = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, options,
            DecisionContext(Intent.PICK_OPTION, source="Gathering",
                            consequence="event fires in your Domain + cultural allies"))
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
        ctx.player.discard.append(ctx.card)


@_register
class SacredGrove(CardBehavior):
    name = 'Sacred Grove'
    tags = ['Nature', 'Spiritual']
    deck = 'tree'
    def can_activate(self, ctx):
        return ctx.location == "domain"

    def on_activate(self, ctx):
        options = ["rite", "scry"]
        choice = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, options,
            DecisionContext(Intent.PICK_OPTION, source="Sacred Grove",
                            consequence="Rite or scry Tree top 3 for Spiritual"))
        if choice == "rite":
            ctx.state.log(f"  → triggers Rite")
            ctx.engine.resolve_event("Rite", ctx.player)
        else:
            top3 = ctx.state.peek_pile("tree", 3)
            spiritual = [c for c in top3 if c.has_tag("Spiritual")]
            if spiritual:
                for sc in spiritual:
                    ctx.state.pile_ptrs["tree"] += 1
                    ctx.player.add_to_domain(sc, ctx.state)
                    ctx.state.log(f"  → takes {sc.name} (Spiritual) from Tree top")
                remaining = [c for c in top3 if c not in spiritual]
                for c in remaining:
                    ctx.state.pile_ptrs["tree"] += 1
                if remaining:
                    ptr = ctx.state.pile_ptrs["tree"]
                    for i, c in enumerate(remaining):
                        ctx.state.piles["tree"].insert(ptr - len(remaining) + i, c)
                    ctx.state.pile_ptrs["tree"] -= len(remaining)
            else:
                ctx.state.log(f"  → scries top 3 Tree: {', '.join(c.name for c in top3)}. No Spiritual found.")


@_register
class OralTradition(CardBehavior):
    name = 'Oral Tradition'
    tags = ['Knowledge']
    deck = 'tree'
    def can_activate(self, ctx):
        return (ctx.location == "domain"
                and any(c.deck == "coin" for c in ctx.player.domain)
                and ctx.state.pile_remaining("candle") > 0)

    def on_activate(self, ctx):
        coin_cards = [c for c in ctx.player.domain if c.deck == "coin"]
        to_discard = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, coin_cards,
            DecisionContext(Intent.SACRIFICE, source="Oral Tradition",
                            consequence="draw 1 from Candle"))
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
    def can_activate(self, ctx):
        if ctx.location != "domain":
            return False
        has_cost = any(c.has_tag("Knowledge") or c.has_tag("Nature")
                       for c in ctx.player.domain if c is not ctx.card)
        return has_cost and len(ctx.player.discard) > 0

    def on_activate(self, ctx):
        costs = [c for c in ctx.player.domain
                 if (c.has_tag("Knowledge") or c.has_tag("Nature")) and c is not ctx.card]
        cost_card = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, costs,
            DecisionContext(Intent.SACRIFICE, source="Herbalism",
                            consequence="recover a card from discard"))
        ctx.player.discard_from_domain(cost_card)
        target_card = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, list(ctx.player.discard),
            DecisionContext(Intent.GAIN, source="Herbalism",
                            consequence="recovered from discard to Domain"))
        ctx.player.discard.remove(target_card)
        ctx.player.add_to_domain(target_card, ctx.state)
        ctx.state.log(f"  → discards {cost_card.name}, recovers {target_card.name} from discard")


@_register
class WorshipOfTheRain(CardBehavior):
    name = 'Worship of the Rain'
    tags = ['Spiritual']
    deck = 'tree'
    def on_event(self, ctx):
        if ctx.event != "Rite":
            return False
        if not ctx.state.season:
            return False
        to_discard = ctx.engine.strat(ctx.triggerer).choose_from(
            ctx.state, ctx.triggerer, list(ctx.state.season),
            DecisionContext(Intent.PICK_OPTION, source="Worship of the Rain",
                            consequence="swap Season card for Tree top"))
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
    def on_event(self, ctx):
        if ctx.event != "Rite":
            return False
        ctx.state.log(f"  → {ctx.player.name}'s Worship of Fertility: triggers Harvest for {ctx.triggerer.name}")
        ctx.engine.resolve_event("Harvest", ctx.triggerer)
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
    def can_activate(self, ctx):
        return ctx.location == "domain" and ctx.state.pile_remaining("claw") > 0

    def on_activate(self, ctx):
        top3 = ctx.state.peek_pile("claw", 3)
        if top3:
            ctx.state.log(f"  → scouts Claw top 3: {', '.join(c.name for c in top3)}")
            if ctx.engine.strat(ctx.player).choose_yes_no(
                    ctx.state, ctx.player,
                    DecisionContext(Intent.ACCEPT_REJECT, source="Crags",
                                    consequence="put one Claw card in your discard")):
                pick = ctx.engine.strat(ctx.player).choose_from(
                    ctx.state, ctx.player, top3,
                    DecisionContext(Intent.GAIN, source="Crags",
                                    consequence="goes to your discard (scout)"))
                idx = ctx.state.piles["claw"].index(pick)
                ctx.state.piles["claw"].pop(idx)
                if idx < ctx.state.pile_ptrs["claw"]:
                    ctx.state.pile_ptrs["claw"] -= 1
                ctx.player.discard.append(pick)
                ctx.state.log(f"  → puts {pick.name} in discard")

    def on_event(self, ctx):
        if ctx.event != "Brawl" or ctx.target is not ctx.player:
            return False
        crags_count = sum(1 for c in ctx.player.domain if c.name == "Crags")
        if crags_count < 2:
            return False
        if ctx.triggerer.domain:
            if ctx.engine.strat(ctx.triggerer).choose_yes_no(
                    ctx.state, ctx.triggerer,
                    DecisionContext(Intent.ACCEPT_REJECT, source="Crags",
                                    opponent=ctx.player,
                                    consequence="discard a card to proceed with Brawl")):
                victim = ctx.engine.strat(ctx.triggerer).choose_from(
                    ctx.state, ctx.triggerer, list(ctx.triggerer.domain),
                    DecisionContext(Intent.SACRIFICE, source="Crags",
                                    consequence="overcome Crags defense"))
                ctx.triggerer.discard_from_domain(victim)
                ctx.state.log(f"  → {ctx.triggerer.name} discards {victim.name} to overcome Crags defense")
                return False  # Defense paid, Brawl continues
            else:
                ctx.state.log(f"  → Brawl cancelled by Crags defense")
                ctx.engine.cancel_event()
                return True
        else:
            ctx.state.log(f"  → Brawl cancelled by Crags defense (triggerer has no cards)")
            ctx.engine.cancel_event()
            return True


@_register
class Solstice(CardBehavior):
    name = 'Solstice'
    tags = []
    deck = 'tree'
    def on_event(self, ctx):
        if ctx.event != "Harvest":
            return False
        options = ["culture_draw", "culture_place"]
        choice = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, options,
            DecisionContext(Intent.PICK_OPTION, source="Solstice",
                            consequence="culture allies draw Tree, or place Culture from discard"))
        if choice == "culture_draw":
            for ally in ctx.state.players:
                if ctx.player.shares_culture(ally) or ally is ctx.player:
                    tree = ctx.state.draw_from_pile("tree")
                    if tree:
                        ctx.state.log(f"  → Solstice: {ally.name} draws {tree.name} from Tree")
                        ctx.engine.receive_card(ally, tree)
        else:
            culture_cards = [c for c in ctx.player.discard if c.has_tag("Culture")]
            if culture_cards:
                culture = ctx.engine.strat(ctx.player).choose_from(
                    ctx.state, ctx.player, culture_cards,
                    DecisionContext(Intent.PICK_OPTION, source="Solstice",
                                    consequence="place Culture in a Domain"))
                target = ctx.engine.strat(ctx.player).choose_from(
                    ctx.state, ctx.player, list(ctx.state.players),
                    DecisionContext(Intent.PICK_TARGET, source="Solstice",
                                    consequence=f"receives {culture.name}"))
                ctx.player.discard.remove(culture)
                target.add_to_domain(culture, ctx.state)
                ctx.state.log(f"  → Solstice: places {culture.name} in {target.name}'s Domain")
        return True


@_register
class Regrowth(CardBehavior):
    name = 'Regrowth'
    tags = []
    deck = 'tree'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        for p in ctx.state.players:
            pastures = [c for c in p.discard if c.name == "Pasture"]
            for pas in pastures:
                p.discard.remove(pas)
                p.add_to_domain(pas, ctx.state)
                ctx.state.log(f"  → Regrowth: returns Pasture to {p.name}")
        ctx.player.discard.append(ctx.card)


@_register
class Forage(CardBehavior):
    name = 'Forage'
    tags = []
    deck = 'tree'
    def can_activate(self, ctx):
        return ctx.location == "domain" and ctx.state.pile_remaining("tree") > 0

    def on_activate(self, ctx):
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
        if ctx.engine.strat(ctx.player).choose_yes_no(
                ctx.state, ctx.player,
                DecisionContext(Intent.ACCEPT_REJECT, source="Forage",
                                consequence="sacrifice Forage to take one card to Domain")):
            pick = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, top3,
                DecisionContext(Intent.GAIN, source="Forage",
                                consequence="take from revealed to Domain"))
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
    def can_activate(self, ctx):
        return (ctx.location == "domain"
                and ctx.player.count_tag("Nature") >= 2
                and len(ctx.state.fields) > 0)

    def on_activate(self, ctx):
        ctx.state.log(f"  → activates Wheat zone via Sowing")
        ctx.engine.activate_wheat_zone(ctx.player)


@_register
class WitheredCrop(CardBehavior):
    name = 'Withered Crop'
    tags = []
    deck = 'tree'
    def can_activate(self, ctx):
        return (ctx.location == "domain"
                and ctx.player.has_discard("Harvest")
                and len(ctx.state.fields) > 0)

    def on_activate(self, ctx):
        ctx.state.log(f"  → activates Wheat zone via Withered Crop")
        ctx.engine.activate_wheat_zone(ctx.player)


@_register
class Remembrance(CardBehavior):
    name = 'Remembrance'
    tags = ['Knowledge']
    deck = 'tree'
    def can_activate(self, ctx):
        return (ctx.location == "domain"
                and ctx.player.count_tag("Knowledge") > 0
                and len(ctx.player.discard) > 0)

    def on_activate(self, ctx):
        knowledge_count = ctx.player.count_tag("Knowledge")
        to_recover = ctx.engine.strat(ctx.player).choose_n(
            ctx.state, ctx.player, list(ctx.player.discard),
            1, min(knowledge_count, len(ctx.player.discard)),
            DecisionContext(Intent.GAIN, source="Remembrance",
                            consequence="recover from discard to Domain"))
        for c in to_recover:
            ctx.player.discard.remove(c)
            ctx.player.add_to_domain(c, ctx.state)
            ctx.state.log(f"  → recovers {c.name} from discard")
