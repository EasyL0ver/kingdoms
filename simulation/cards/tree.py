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
class WorshipOfTheDawn(CardBehavior):
    name = 'Worship of the Dawn'
    tags = ['Spiritual']
    deck = 'tree'

    def _dusk_exists(self, ctx):
        for p in ctx.state.players:
            if p.has_card("Worship of the Dusk"):
                return True
        return False

    def on_rite(self, ctx):
        if not ctx.player.discard:
            return False
        n = 2 if self._dusk_exists(ctx) else 1
        n = min(n, len(ctx.player.discard))
        to_recover = ctx.engine.strat(ctx.player).resolve_n(
            ctx.state, ctx.player, list(ctx.player.discard),
            1, n,
            DecisionContext(event="Rite", source="Worship of the Dawn", intent=Intent.GAIN))
        for c in to_recover:
            ctx.player.discard.remove(c)
            ctx.player.add_to_domain(c, ctx.state)
        names = ", ".join(c.name for c in to_recover)
        doubled = " (Dusk in play)" if n == 2 else ""
        ctx.state.log(f"  → Worship of the Dawn: {ctx.player.name} recovers {names}{doubled}")
        return True


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
        options = ["brawl", "rite", "rumour"]
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
        elif choice == "rite":
            ctx.state.log(f"  → Gathering: Rite in {ctx.player.name}'s Domain")
            ctx.engine.resolve_event("Rite", ctx.player)
        else:
            ctx.state.log(f"  → Gathering: Rumour spreads")
            ctx.engine.resolve_event("Rumour", ctx.player,
                                     scope=ctx.state.other_players(ctx.player))
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
class Floods(CardBehavior):
    name = 'Floods'
    tags = ['Nature']
    deck = 'tree'

    # Alternative design tested (v2): unconditional Brawl cancel, On Dawn
    # with two Floods every player discards 4 then all Floods discard.
    # More dramatic but one-shot; v1 grind was stronger in tree_search sims.

    def _another_floods_in_play(self, ctx):
        for p in ctx.state.players:
            for c in p.domain:
                if c.name == 'Floods' and c is not ctx.card:
                    return True
        return False

    def on_brawl(self, ctx):
        if not self._another_floods_in_play(ctx):
            return False
        ctx.state.log(f"  → Floods cancels Brawl (two Floods in play)")
        ctx.engine.cancel_event()
        return True

    def on_dawn(self, ctx):
        ctx.state.refill_season()
        ctx.state.log(f"  → Floods: Season refilled to {len(ctx.state.season)}")
        if self._another_floods_in_play(ctx):
            ctx.state.log(f"  → Floods: two in play — each player discards 1")
            for p in ctx.state.players:
                if p.domain:
                    victim = ctx.engine.strat(p).resolve(
                        ctx.state, p, list(p.domain),
                        DecisionContext(event="Dawn", source="Floods", intent=Intent.DISCARD))
                    p.discard_from_domain(victim)
                    ctx.state.log(f"    {p.name} discards {victim.name}")


@_register
class Regrowth(CardBehavior):
    name = 'Regrowth'
    tags = []
    deck = 'tree'
    def on_dawn(self, ctx):
        total = 0
        for p in ctx.state.players:
            nature_cards = [c for c in p.discard
                           if c.has_tag("Nature") and c.name != "Regrowth"]
            for c in nature_cards:
                p.discard.remove(c)
                p.add_to_domain(c, ctx.state)
                ctx.state.log(f"  → Regrowth: {c.name} returns to {p.name}'s Domain")
                total += 1
        if total:
            ctx.state.log(f"  → Regrowth restored {total} [Nature] cards game-wide")
        ctx.discard_self()


@_register
class WorshipOfTheHearth(CardBehavior):
    name = 'Worship of the Hearth'
    tags = ['Nature', 'Spiritual']
    deck = 'tree'
    def on_rite(self, ctx):
        kinship_players = [p for p in ctx.state.players
                           if p.has_card("Kinship")]
        if not kinship_players:
            return False
        names = ", ".join(p.name for p in kinship_players)
        ctx.state.log(f"  → Worship of the Hearth: Harvest for {names}")
        for p in kinship_players:
            ctx.engine.resolve_event("Harvest", p)
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
class Vigil(CardBehavior):
    name = 'Vigil'
    tags = []
    deck = 'tree'
    def on_harvest(self, ctx):
        allies = [p for p in ctx.state.other_players(ctx.player)
                  if p.has_card("Kinship")]
        if not allies or not ctx.player.discard:
            return False
        n = min(len(allies), len(ctx.player.discard))
        to_recover = ctx.engine.strat(ctx.player).resolve_n(
            ctx.state, ctx.player, list(ctx.player.discard),
            1, n,
            DecisionContext(event="Harvest", source="Vigil", intent=Intent.GAIN))
        for c in to_recover:
            ctx.player.discard.remove(c)
            ctx.player.add_to_domain(c, ctx.state)
            ctx.state.log(f"  → Vigil: recovers {c.name} ({len(allies)} allies with Kinship)")
        return True


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
class Hospitality(CardBehavior):
    name = 'Hospitality'
    tags = []
    deck = 'tree'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        from cards import CardBehavior, get_behavior
        # Find players with Kinship
        partners = [p for p in ctx.state.other_players(ctx.player)
                    if p.has_card("Kinship")]
        if not partners:
            ctx.state.log(f"  → Hospitality: no player with Kinship")
            return
        partner = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, partners,
            DecisionContext(event="Order", source="Hospitality", intent=Intent.OPTION))
        ctx.state.log(f"  → Hospitality: exchange with {partner.name}")
        # Owner orders 1 card in partner's domain
        orderable_theirs = [c for c in partner.domain
                            if getattr(type(get_behavior(c.name)), 'on_order')
                            is not CardBehavior.on_order]
        if orderable_theirs:
            pick = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, orderable_theirs,
                DecisionContext(event="Order", source="Hospitality", intent=Intent.OPTION))
            ctx.state.log(f"  → {ctx.player.name} orders {pick.name} in {partner.name}'s Domain")
            ctx.engine.resolve_event("Order", ctx.player, scope=pick)
        # Partner orders 1 card in owner's domain
        orderable_mine = [c for c in ctx.player.domain
                          if c is not ctx.card
                          and getattr(type(get_behavior(c.name)), 'on_order')
                          is not CardBehavior.on_order]
        if orderable_mine:
            pick2 = ctx.engine.strat(partner).resolve(
                ctx.state, partner, orderable_mine,
                DecisionContext(event="Order", source="Hospitality", intent=Intent.OPTION))
            ctx.state.log(f"  → {partner.name} orders {pick2.name} in {ctx.player.name}'s Domain")
            ctx.engine.resolve_event("Order", partner, scope=pick2)


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
        # Gather participants — owner always joins, others may opt in
        participants = [ctx.player]
        for p in ctx.state.other_players(ctx.player):
            if ctx.engine.strat(p).resolve(
                    ctx.state, p, [True, False],
                    DecisionContext(event="Order", source="Pilgrimage", intent=Intent.OPTION)):
                participants.append(p)
                ctx.state.log(f"  → {p.name} joins the Pilgrimage")
        # Draw from Candle for each participant
        drawn = []
        for _ in participants:
            c = ctx.state.draw_from_pile("candle")
            if c:
                drawn.append(c)
        if not drawn:
            ctx.state.log(f"  → Pilgrimage: Candle pile empty")
            return
        ctx.state.log(f"  → Pilgrimage: {len(participants)} pilgrims, drew {', '.join(c.name for c in drawn)}")
        # Owner distributes cards among participants
        for c in drawn:
            recipient = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, participants,
                DecisionContext(event="Order", source="Pilgrimage", intent=Intent.OPTION))
            recipient.add_to_domain(c, ctx.state)
            ctx.state.log(f"    {recipient.name} receives {c.name}")

    def on_rite(self, ctx):
        self._claim_revelation(ctx)
        return True
