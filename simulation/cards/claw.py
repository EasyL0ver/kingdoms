"""Claw deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Warband(CardBehavior):
    name = 'Warband'
    tags = ['Discontent']
    deck = 'claw'
    def can_activate(self, ctx):
        return ctx.location == "domain"

    def on_activate(self, ctx):
        targets = sorted(ctx.state.other_players(ctx.player),
                         key=lambda p: len(p.domain), reverse=True)
        if not targets:
            return
        max_cards = len(targets[0].domain)
        tied = [p for p in targets if len(p.domain) == max_cards]
        target = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, tied,
            DecisionContext(Intent.PICK_TARGET, source="Warband",
                            consequence="Brawl in their Domain"))
        ctx.state.log(f"  → triggers Brawl in {target.name}'s Domain")
        ctx.engine.resolve_event("Brawl", ctx.player, target)


@_register
class Raid(CardBehavior):
    name = 'Raid'
    tags = ['Unit', 'Mob', 'Discontent']
    deck = 'claw'
    def on_event(self, ctx):
        if not ctx.responds_to("Brawl", targeted=True):
            return False
        giveable = [c for c in ctx.player.domain if c is not ctx.card]
        if not giveable:
            return True
        if ctx.uprising:
            victim = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, giveable,
                DecisionContext(Intent.SACRIFICE, source="Raid",
                                consequence="discarded (Uprising)"))
            ctx.player.discard_from_domain(victim)
            ctx.state.log(f"  → Raid: {ctx.player.name} discards {victim.name} (Uprising)")
        else:
            victim = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, giveable,
                DecisionContext(Intent.GIVE_AWAY, source="Raid", opponent=ctx.triggerer,
                                consequence="card goes to attacker"))
            ctx.player.remove_from_domain(victim)
            ctx.triggerer.add_to_domain(victim, ctx.state)
            ctx.state.log(f"  → Raid: {ctx.player.name} gives {victim.name} to {ctx.triggerer.name}")
        return True


@_register
class Scavenge(CardBehavior):
    name = 'Scavenge'
    tags = ['Unit', 'Mob', 'Discontent']
    deck = 'claw'
    def on_event(self, ctx):
        if not ctx.responds_to("Brawl", targeted=True):
            return False
        if not ctx.player.discard:
            return True
        if ctx.uprising:
            ctx.state.log(f"  → Scavenge: no effect (Uprising)")
        else:
            victim = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, list(ctx.player.discard),
                DecisionContext(Intent.GIVE_AWAY, source="Scavenge", opponent=ctx.triggerer,
                                consequence="discard card goes to attacker"))
            ctx.player.discard.remove(victim)
            ctx.triggerer.add_to_domain(victim, ctx.state)
            ctx.state.log(f"  → Scavenge: {ctx.triggerer.name} takes {victim.name} from {ctx.player.name}'s discard")
        return True


@_register
class BloodOffering(CardBehavior):
    name = 'Blood Offering'
    tags = []
    deck = 'claw'
    def can_activate(self, ctx):
        return ctx.location == "domain" and len(ctx.player.domain) > 1

    def on_activate(self, ctx):
        sacrificeable = [c for c in ctx.player.domain if c is not ctx.card]
        victim = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, sacrificeable,
            DecisionContext(Intent.SACRIFICE, source="Blood Offering",
                            consequence="triggers Rite"))
        ctx.player.discard_from_domain(victim)
        ctx.state.log(f"  → discards {victim.name}, triggers Rite")
        ctx.engine.resolve_event("Rite", ctx.player)


@_register
class Poach(CardBehavior):
    name = 'Poach'
    tags = ['Unit', 'Mob', 'Hunt', 'Discontent']
    deck = 'claw'
    def can_activate(self, ctx):
        if ctx.location != "domain":
            return False
        hunt_limit = 1 + sum(1 for c in ctx.player.domain if c.name == "Pasture")
        return ctx.state.hunt_uses_this_round < hunt_limit

    def on_activate(self, ctx):
        ctx.state.hunt_uses_this_round += 1
        ctx.state.log(f"  → triggers Feast in {ctx.player.name}'s Domain")
        ctx.engine.resolve_event("Feast", ctx.player, ctx.player)


@_register
class WorshipOfTheHunt(CardBehavior):
    name = 'Worship of the Hunt'
    tags = ['Spiritual']
    deck = 'claw'
    def on_event(self, ctx):
        if not ctx.responds_to("Rite"):
            return False
        hunts = ctx.triggerer.cards_with_tag("Hunt")
        for h in hunts:
            ctx.state.log(f"  → {ctx.player.name}'s Worship of the Hunt: {ctx.triggerer.name} feasts via {h.name}")
            ctx.engine.resolve_event("Feast", ctx.triggerer, ctx.triggerer)
        return True


@_register
class WorshipOfWar(CardBehavior):
    name = 'Worship of War'
    tags = ['Spiritual']
    deck = 'claw'
    def on_event(self, ctx):
        if not ctx.responds_to("Rite"):
            return False
        targets = list(ctx.state.players)
        target = ctx.engine.strat(ctx.triggerer).choose_from(
            ctx.state, ctx.triggerer, targets,
            DecisionContext(Intent.PICK_TARGET, source="Worship of War",
                            consequence="Brawl in their Domain"))
        ctx.state.log(f"  → {ctx.player.name}'s Worship of War: {ctx.triggerer.name} Brawls {target.name}")
        ctx.engine.resolve_event("Brawl", ctx.triggerer, target)
        return True


@_register
class Incite(CardBehavior):
    name = 'Incite'
    tags = []
    deck = 'claw'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        mobs = ctx.player.cards_with_tag("Mob")
        targets = ctx.state.other_players(ctx.player)
        if mobs and targets:
            to_move = ctx.engine.strat(ctx.player).choose_n(
                ctx.state, ctx.player, mobs, 0, min(3, len(mobs)),
                DecisionContext(Intent.PICK_OPTION, source="Incite",
                                consequence="Mob moved to opponent's Domain"))
            for mob in to_move:
                target = ctx.engine.strat(ctx.player).choose_from(
                    ctx.state, ctx.player, targets,
                    DecisionContext(Intent.PICK_TARGET, source="Incite",
                                    consequence=f"receives {mob.name}"))
                ctx.player.remove_from_domain(mob)
                target.add_to_domain(mob, ctx.state)
                ctx.state.log(f"  → Incite: moves {mob.name} to {target.name}")
        ctx.state.log(f"  → Incite discarded")
        ctx.discard_self()


@_register
class Chiefdom(CardBehavior):
    name = 'Chiefdom'
    tags = ['Allegiance', 'Trophy']
    deck = 'claw'
    def can_activate(self, ctx):
        if ctx.location != "domain":
            return False
        if ctx.player.count_tag("Mob") > 0:
            return True
        for p in ctx.state.other_players(ctx.player):
            if ctx.player.shares_culture(p) and p.count_tag("Mob") > 0:
                return True
        return False

    def on_activate(self, ctx):
        mob_sources = []
        for mob in ctx.player.cards_with_tag("Mob"):
            mob_sources.append((ctx.player, mob))
        for p in ctx.state.other_players(ctx.player):
            if ctx.player.shares_culture(p):
                for mob in p.cards_with_tag("Mob"):
                    mob_sources.append((p, mob))
        if mob_sources:
            source_player, mob = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, mob_sources,
                DecisionContext(Intent.PICK_OPTION, source="Chiefdom",
                                consequence="Mob moved to target Domain"))
            targets = [p for p in ctx.state.players if p is not source_player]
            target = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, targets,
                DecisionContext(Intent.PICK_TARGET, source="Chiefdom",
                                consequence=f"receives {mob.name}"))
            source_player.remove_from_domain(mob)
            target.add_to_domain(mob, ctx.state)
            ctx.state.log(f"  → moves {mob.name} from {source_player.name} to {target.name}")


@_register
class Racketeering(CardBehavior):
    name = 'Racketeering'
    tags = ['Discontent']
    deck = 'claw'
    def can_activate(self, ctx):
        return ctx.location == "domain"

    def on_activate(self, ctx):
        targets = ctx.state.other_players(ctx.player)
        if not targets:
            return
        target = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, targets,
            DecisionContext(Intent.PICK_TARGET, source="Racketeering",
                            consequence="they offer you a card"))
        if not target.domain:
            ctx.state.log(f"  → {target.name} has no cards to offer")
            return
        offered = ctx.engine.strat(target).choose_from(
            ctx.state, target, list(target.domain),
            DecisionContext(Intent.GIVE_AWAY, source="Racketeering", opponent=ctx.player,
                            consequence="opponent may take this card"))
        take_it = ctx.engine.strat(ctx.player).choose_yes_no(
            ctx.state, ctx.player,
            DecisionContext(Intent.ACCEPT_REJECT, source="Racketeering", opponent=target,
                            consequence="refuse triggers Brawl"))
        if take_it:
            target.remove_from_domain(offered)
            ctx.player.add_to_domain(offered, ctx.state)
            ctx.state.log(f"  → takes {offered.name} from {target.name}")
        else:
            ctx.state.log(f"  → refuses {offered.name}, triggers Brawl in {target.name}'s Domain")
            ctx.engine.resolve_event("Brawl", ctx.player, target)


@_register
class Tyranny(CardBehavior):
    name = 'Tyranny'
    tags = ['Trophy', 'Discontent']
    deck = 'claw'
    def can_activate(self, ctx):
        return ctx.location == "domain"

    def on_activate(self, ctx):
        discontent_count = ctx.player.count_tag("Discontent")
        drawn = ctx.engine.draw_and_receive(ctx.player, "claw", discontent_count)
        ctx.state.log(f"  → draws {len(drawn)} from Claw ({discontent_count} Discontent)")
        if ctx.state.game_over:
            return
        ctx.state.log(f"  → triggers self-Brawl (spoils discarded, not given)")
        ctx.engine.resolve_event("Brawl", ctx.player, ctx.player, uprising=True)


@_register
class Marauders(CardBehavior):
    name = 'Marauders'
    tags = ['Unit', 'Mob', 'Discontent']
    deck = 'claw'
    def on_event(self, ctx):
        if not ctx.responds_to("Feast", targeted=True):
            return False
        ctx.player.discard_from_domain(ctx.card)
        drawn = ctx.engine.draw_and_receive(ctx.player, "claw")
        if drawn:
            ctx.state.log(f"  → Marauders: self-destructs, draws {drawn[0].name} from Claw")
        else:
            ctx.state.log(f"  → Marauders: self-destructs")
        return True


@_register
class ShareTheSpoils(CardBehavior):
    name = 'Share the Spoils'
    tags = []
    deck = 'claw'
    def on_event(self, ctx):
        if not ctx.responds_to("Feast", targeted=True):
            return False
        drawn = ctx.engine.draw_and_receive(ctx.player, "claw")
        if drawn:
            ctx.state.log(f"  → Share the Spoils: draws {drawn[0].name} from Claw")
        return True


@_register
class Outriders(CardBehavior):
    name = 'Outriders'
    tags = []
    deck = 'claw'
    def can_activate(self, ctx):
        return ctx.location == "domain" and ctx.state.pile_remaining("claw") > 0

    def on_activate(self, ctx):
        drawn = []
        for _ in range(3):
            c = ctx.state.draw_from_pile("claw")
            if c:
                drawn.append(c)
        if not drawn:
            return
        ctx.state.log(f"  → draws 3 from Claw: {', '.join(c.name for c in drawn)}")
        if len(drawn) > 1:
            to_discard = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, drawn,
                DecisionContext(Intent.SACRIFICE, source="Outriders",
                                consequence="discarded, keep the other 2"))
            drawn.remove(to_discard)
            ctx.player.discard.append(to_discard)
            ctx.state.log(f"  → discards {to_discard.name}")
        for c in drawn:
            ctx.engine.receive_card(ctx.player, c)


@_register
class LandGrab(CardBehavior):
    name = 'Land Grab'
    tags = ['Discontent']
    deck = 'claw'
    def can_activate(self, ctx):
        return ctx.location == "domain" and any(c.has_tag("Land") for c in ctx.state.season)

    def on_activate(self, ctx):
        lands = [c for c in ctx.state.season if c.has_tag("Land")]
        for land in lands:
            ctx.state.season.remove(land)
            ctx.player.add_to_domain(land, ctx.state)
            ctx.state.log(f"  → takes {land.name} from Season")
        ctx.player.discard_from_domain(ctx.card)
        ctx.state.log(f"  → discards Land Grab")
        ctx.state.refill_season()


@_register
class Ransack(CardBehavior):
    name = 'Ransack'
    tags = []
    deck = 'claw'
    def can_activate(self, ctx):
        return (ctx.location == "domain" and len(ctx.player.domain) > 1
                and (ctx.state.pile_remaining("claw") > 0 or len(ctx.state.season) > 0))

    def on_activate(self, ctx):
        sacrificeable = [c for c in ctx.player.domain if c is not ctx.card]
        victim = ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, sacrificeable,
            DecisionContext(Intent.SACRIFICE, source="Ransack",
                            consequence="then draw 2 Claw + take 1 Season"))
        ctx.player.discard_from_domain(victim)
        ctx.state.log(f"  → discards {victim.name}")
        for _ in range(2):
            c = ctx.state.draw_from_pile("claw")
            if c:
                ctx.state.log(f"  → Claw: draws {c.name}")
                ctx.engine.receive_card(ctx.player, c)
        if ctx.state.season:
            pick = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, list(ctx.state.season),
                DecisionContext(Intent.GAIN, source="Ransack",
                                consequence="take from Season"))
            ctx.state.season.remove(pick)
            ctx.state.log(f"  → Tree: takes {pick.name} from Season")
            ctx.engine.receive_card(ctx.player, pick)
            ctx.state.refill_season()


@_register
class RiteOfPassage(CardBehavior):
    name = 'Rite of Passage'
    tags = ['Discontent']
    deck = 'claw'
    def on_event(self, ctx):
        if not ctx.responds_to("Brawl", targeted=True):
            return False
        drawn = ctx.engine.draw_and_receive(ctx.player, "tree")
        if drawn:
            ctx.state.log(f"  → Rite of Passage: {ctx.player.name} draws {drawn[0].name} from Tree")
        return True


@_register
class Culling(CardBehavior):
    name = 'Culling'
    tags = ['Discontent']
    deck = 'claw'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        all_players = sorted(ctx.state.players, key=lambda p: len(p.domain), reverse=True)
        max_count = len(all_players[0].domain)
        tied = [p for p in all_players if len(p.domain) == max_count]
        target = (ctx.engine.strat(ctx.player).choose_from(
            ctx.state, ctx.player, tied,
            DecisionContext(Intent.PICK_TARGET, source="Culling",
                            consequence="they discard 2 cards"))
            if len(tied) > 1 else tied[0])
        if target.domain:
            to_discard = ctx.engine.strat(target).choose_n(
                ctx.state, target, list(target.domain),
                1, min(2, len(target.domain)),
                DecisionContext(Intent.GIVE_AWAY, source="Culling",
                                consequence="forced discard", tags=["forced"]))
            for c in to_discard:
                target.discard_from_domain(c)
                ctx.state.log(f"  → Culling: {target.name} discards {c.name}")
        ctx.discard_self()


@_register
class Ingenuity(CardBehavior):
    name = 'Ingenuity'
    tags = ['Craftsmanship', 'Discontent']
    deck = 'claw'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → Ingenuity: draws {drawn[0].name} from Coin")


@_register
class Uprising(CardBehavior):
    name = 'Uprising'
    tags = ['Discontent']
    deck = 'claw'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        ctx.state.log(f"  → Drafted: Uprising — self-Brawl (no benefits)")
        ctx.player.add_to_domain(ctx.card, ctx.state)
        ctx.engine.resolve_event("Brawl", ctx.player, ctx.player, uprising=True)


@_register
class SpoilsOfWar(CardBehavior):
    name = 'Spoils of War'
    tags = ['Trophy', 'Mob']
    deck = 'claw'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        targets = ctx.state.other_players(ctx.player)
        if targets:
            target = ctx.engine.strat(ctx.player).choose_from(
                ctx.state, ctx.player, targets,
                DecisionContext(Intent.PICK_TARGET, source="Spoils of War",
                                consequence="placed in their Domain as Mob"))
            target.add_to_domain(ctx.card, ctx.state)
            ctx.state.log(f"  → Spoils of War placed in {target.name}'s Domain")

    def on_event(self, ctx):
        if not ctx.responds_to("Brawl", targeted=True):
            return False
        if ctx.uprising:
            ctx.state.log(f"  → Spoils of War: no effect (Uprising)")
            return True
        ctx.player.remove_from_domain(ctx.card)
        ctx.triggerer.add_to_domain(ctx.card, ctx.state)
        trophy_count = ctx.triggerer.count_tag("Trophy")
        ctx.state.log(f"  → Spoils of War → {ctx.triggerer.name}, draws {trophy_count} Claw + {trophy_count} Tree")
        ctx.engine.draw_and_receive(ctx.triggerer, "claw", trophy_count)
        ctx.engine.draw_and_receive(ctx.triggerer, "tree", trophy_count)
        return True


@_register
class DuskRite(CardBehavior):
    name = 'Dusk Rite'
    tags = ['Spiritual', 'Discontent']
    deck = 'claw'
    def can_activate(self, ctx):
        return ctx.location == "domain" and len(ctx.player.discard) > 0

    def on_activate(self, ctx):
        if ctx.player.discard:
            to_remove = ctx.engine.strat(ctx.player).choose_n(
                ctx.state, ctx.player, list(ctx.player.discard),
                1, len(ctx.player.discard),
                DecisionContext(Intent.SACRIFICE, source="Dusk Rite",
                                consequence="removed permanently, draw Claw+Tree equal to count"))
            for c in to_remove:
                ctx.player.discard.remove(c)
            removed_count = len(to_remove)
            ctx.state.log(f"  → removes {removed_count} cards from discard permanently")
            for c in ctx.engine.draw_and_receive(ctx.player, "claw", removed_count):
                ctx.state.log(f"  → draws {c.name} from Claw")
            for c in ctx.engine.draw_and_receive(ctx.player, "tree", removed_count):
                ctx.state.log(f"  → draws {c.name} from Tree")
            ctx.player.discard_from_domain(ctx.card)
            ctx.state.log(f"  → discards Dusk Rite, triggers Rite")
            ctx.engine.resolve_event("Rite", ctx.player)
