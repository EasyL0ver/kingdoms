"""Claw deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Warband(CardBehavior):
    name = 'Warband'
    tags = ['Discontent']
    deck = 'claw'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        targets = sorted(ctx.state.other_players(ctx.player),
                         key=lambda p: len(p.domain), reverse=True)
        if not targets:
            return
        max_cards = len(targets[0].domain)
        tied = [p for p in targets if len(p.domain) == max_cards]
        target = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, tied,
            DecisionContext(event="Order", source="Warband", intent=Intent.TARGET))
        # Move 1 Mob card to target before brawl
        mobs = [c for c in ctx.player.domain if c.has_tag("Mob") and c is not ctx.card]
        if mobs:
            mob = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, mobs,
                DecisionContext(event="Order", source="Warband", intent=Intent.GIVE_AWAY))
            ctx.player.remove_from_domain(mob)
            target.add_to_domain(mob, ctx.state)
            ctx.state.log(f"  → moves {mob.name} to {target.name}'s Domain")
        ctx.state.log(f"  → Brawl in {target.name}'s Domain")
        ctx.engine.resolve_event("Brawl", ctx.player, target)


@_register
class Raid(CardBehavior):
    name = 'Raid'
    tags = ['Unit', 'Mob', 'Discontent']
    deck = 'claw'
    def on_brawl(self, ctx):
        giveable = [c for c in ctx.player.domain if c is not ctx.card]
        if not giveable:
            return True
        if ctx.uprising:
            victim = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, giveable,
                DecisionContext(event="Brawl", source="Raid", intent=Intent.DISCARD))
            ctx.player.discard_from_domain(victim)
            ctx.state.log(f"  → Raid: {ctx.player.name} discards {victim.name} (Uprising)")
        else:
            victim = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, giveable,
                DecisionContext(event="Brawl", source="Raid", intent=Intent.GIVE_AWAY))
            ctx.player.remove_from_domain(victim)
            ctx.active_player.add_to_domain(victim, ctx.state)
            ctx.state.log(f"  → Raid: {ctx.player.name} gives {victim.name} to {ctx.active_player.name}")
        return True


@_register
class Scavenge(CardBehavior):
    name = 'Scavenge'
    tags = ['Unit', 'Mob', 'Discontent']
    deck = 'claw'
    def on_brawl(self, ctx):
        if not ctx.player.discard:
            return True
        if ctx.uprising:
            ctx.state.log(f"  → Scavenge: no effect (Uprising)")
        else:
            victim = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, list(ctx.player.discard),
                DecisionContext(event="Brawl", source="Scavenge", intent=Intent.GIVE_AWAY))
            ctx.player.discard.remove(victim)
            ctx.active_player.add_to_domain(victim, ctx.state)
            ctx.state.log(f"  → Scavenge: {ctx.active_player.name} takes {victim.name} from {ctx.player.name}'s discard")
        return True


@_register
class BloodOffering(CardBehavior):
    name = 'Blood Offering'
    tags = []
    deck = 'claw'
    def on_order(self, ctx):
        if ctx.location != "domain" or len(ctx.player.domain) <= 1:
            return
        sacrificeable = [c for c in ctx.player.domain if c is not ctx.card]
        victim = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, sacrificeable,
            DecisionContext(event="Order", source="Blood Offering", intent=Intent.DISCARD))
        ctx.player.discard_from_domain(victim)
        ctx.state.log(f"  → discards {victim.name}, Rite")
        ctx.engine.resolve_event("Rite", ctx.player)


@_register
class Poach(CardBehavior):
    name = 'Poach'
    tags = ['Unit', 'Mob', 'Hunt', 'Discontent']
    deck = 'claw'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        # Only works if no other player has a Hunt card in domain
        for p in ctx.state.players:
            if p is ctx.player:
                continue
            if p.cards_with_tag("Hunt"):
                ctx.state.log(f"  → Poach blocked: {p.name} has Hunt in domain")
                return
        # Hunt: discard top 1 from claw pile
        killed = ctx.state.draw_from_pile("claw")
        if killed:
            ctx.player.discard.append(killed)
            ctx.state.log(f"  → Poach: hunts {killed.name} (to discard)")
        # Feast
        ctx.state.log(f"  → Feast in {ctx.player.name}'s Domain")
        ctx.engine.resolve_event("Feast", ctx.player, ctx.player)
        # Draw 1 from claw
        drawn = ctx.state.draw_from_pile("claw")
        if drawn:
            ctx.state.log(f"  → Poach: draws {drawn.name} from Claw")
            ctx.engine.receive_card(ctx.player, drawn)


@_register
class WorshipOfTheHunt(CardBehavior):
    name = 'Worship of the Hunt'
    tags = ['Spiritual']
    deck = 'claw'
    def on_rite(self, ctx):
        s = ctx.state
        dumped = []
        for _ in range(5):
            card = s.draw_from_pile("claw")
            if card:
                ctx.active_player.discard.append(card)
                dumped.append(card.name)
        if dumped:
            s.log(f"  → Worship of the Hunt: {ctx.active_player.name} hunts {', '.join(dumped)} (to discard)")
        return True


@_register
class WorshipOfWar(CardBehavior):
    name = 'Worship of War'
    tags = ['Spiritual']
    deck = 'claw'
    def on_rite(self, ctx):
        targets = list(ctx.state.players)
        target = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, targets,
            DecisionContext(event="Rite", source="Worship of War", intent=Intent.TARGET))
        ctx.state.log(f"  → {ctx.player.name}'s Worship of War: {ctx.active_player.name} Brawls {target.name}")
        ctx.engine.resolve_event("Brawl", ctx.active_player, target)
        return True


@_register
class Incite(CardBehavior):
    name = 'Incite'
    tags = []
    deck = 'claw'
    def on_dawn(self, ctx):
        mobs = ctx.player.cards_with_tag("Mob")
        targets = ctx.state.other_players(ctx.player)
        if mobs and targets:
            to_move = ctx.engine.strat(ctx.player).resolve_n(
                ctx.state, ctx.player, mobs, 0, min(3, len(mobs)),
                DecisionContext(event="Dawn", source="Incite", intent=Intent.OPTION))
            for mob in to_move:
                target = ctx.engine.strat(ctx.player).resolve(
                    ctx.state, ctx.player, targets,
                    DecisionContext(event="Dawn", source="Incite", intent=Intent.TARGET))
                ctx.player.remove_from_domain(mob)
                target.add_to_domain(mob, ctx.state)
                ctx.state.log(f"  → Incite: moves {mob.name} to {target.name}")
        ctx.state.log(f"  → Incite discarded")
        ctx.discard_self()


@_register
class Chiefdom(CardBehavior):
    name = 'Chiefdom'
    tags = ['Trophy']
    deck = 'claw'
    def on_dawn(self, ctx):
        if ctx.location != "domain":
            return
        mob_sources = []
        for mob in ctx.player.cards_with_tag("Mob"):
            if mob is not ctx.card:
                mob_sources.append((ctx.player, mob))
        for p in ctx.state.other_players(ctx.player):
            if ctx.player.shares_culture(p):
                for mob in p.cards_with_tag("Mob"):
                    mob_sources.append((p, mob))
        if not mob_sources:
            return
        # Move up to 2 mobs
        to_move = ctx.engine.strat(ctx.player).resolve_n(
            ctx.state, ctx.player, mob_sources,
            1, min(2, len(mob_sources)),
            DecisionContext(event="Dawn", source="Chiefdom", intent=Intent.OPTION))
        for source_player, mob in to_move:
            targets = [p for p in ctx.state.players if p is not source_player]
            target = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, targets,
                DecisionContext(event="Dawn", source="Chiefdom", intent=Intent.TARGET))
            source_player.remove_from_domain(mob)
            target.add_to_domain(mob, ctx.state)
            ctx.state.log(f"  → Chiefdom: moves {mob.name} from {source_player.name} to {target.name}")


@_register
class Racketeering(CardBehavior):
    name = 'Racketeering'
    tags = ['Discontent']
    deck = 'claw'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        targets = ctx.state.other_players(ctx.player)
        if not targets:
            return
        target = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, targets,
            DecisionContext(event="Order", source="Racketeering", intent=Intent.TARGET))
        if not target.domain:
            ctx.state.log(f"  → {target.name} has no cards to offer")
            return
        offered = ctx.engine.strat(target).resolve(
            ctx.state, target, list(target.domain),
            DecisionContext(event="Order", source="Racketeering", intent=Intent.GIVE_AWAY))
        take_it = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, [True, False],
            DecisionContext(event="Order", source="Racketeering", intent=Intent.OPTION))
        if take_it:
            target.remove_from_domain(offered)
            ctx.player.add_to_domain(offered, ctx.state)
            ctx.state.log(f"  → takes {offered.name} from {target.name}")
        else:
            ctx.state.log(f"  → refuses {offered.name}, Brawl in {target.name}'s Domain")
            ctx.engine.resolve_event("Brawl", ctx.player, target)


@_register
class Tyranny(CardBehavior):
    name = 'Tyranny'
    tags = ['Trophy', 'Discontent']
    deck = 'claw'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        discontent_count = ctx.player.count_tag("Discontent")
        drawn = ctx.engine.draw_and_receive(ctx.player, "claw", discontent_count)
        ctx.state.log(f"  → draws {len(drawn)} from Claw ({discontent_count} Discontent)")
        if ctx.state.game_over:
            return
        ctx.state.log(f"  → self-Brawl (spoils discarded, not given)")
        ctx.engine.resolve_event("Brawl", ctx.player, ctx.player, uprising=True)


@_register
class Marauders(CardBehavior):
    name = 'Marauders'
    tags = ['Unit', 'Mob', 'Discontent']
    deck = 'claw'
    def on_feast(self, ctx):
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
    def on_feast(self, ctx):
        drawn = ctx.engine.draw_and_receive(ctx.player, "claw")
        if drawn:
            ctx.state.log(f"  → Share the Spoils: draws {drawn[0].name} from Claw")
        return True


@_register
class Outriders(CardBehavior):
    name = 'Outriders'
    tags = []
    deck = 'claw'
    def on_order(self, ctx):
        if ctx.location != "domain" or ctx.state.pile_remaining("claw") <= 0:
            return
        drawn = []
        for _ in range(3):
            c = ctx.state.draw_from_pile("claw")
            if c:
                drawn.append(c)
        if not drawn:
            return
        ctx.state.log(f"  → draws 3 from Claw: {', '.join(c.name for c in drawn)}")
        if len(drawn) > 1:
            to_discard = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, drawn,
                DecisionContext(event="Order", source="Outriders", intent=Intent.DISCARD))
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
    def on_order(self, ctx):
        if ctx.location != "domain" or not any(c.has_tag("Land") for c in ctx.state.season):
            return
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
    def on_order(self, ctx):
        if (ctx.location != "domain" or len(ctx.player.domain) <= 1
                or (ctx.state.pile_remaining("claw") <= 0 and len(ctx.state.season) <= 0)):
            return
        sacrificeable = [c for c in ctx.player.domain if c is not ctx.card]
        victim = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, sacrificeable,
            DecisionContext(event="Order", source="Ransack", intent=Intent.DISCARD))
        ctx.player.discard_from_domain(victim)
        ctx.state.log(f"  → discards {victim.name}")
        for _ in range(2):
            c = ctx.state.draw_from_pile("claw")
            if c:
                ctx.state.log(f"  → Claw: draws {c.name}")
                ctx.engine.receive_card(ctx.player, c)
        if ctx.state.season:
            pick = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, list(ctx.state.season),
                DecisionContext(event="Order", source="Ransack", intent=Intent.GAIN))
            ctx.state.season.remove(pick)
            ctx.state.log(f"  → Tree: takes {pick.name} from Season")
            ctx.engine.receive_card(ctx.player, pick)
            ctx.state.refill_season()


@_register
class RiteOfPassage(CardBehavior):
    name = 'Rite of Passage'
    tags = ['Discontent']
    deck = 'claw'
    def on_brawl(self, ctx):
        drawn = ctx.engine.draw_and_receive(ctx.player, "tree")
        if drawn:
            ctx.state.log(f"  → Rite of Passage: {ctx.player.name} draws {drawn[0].name} from Tree")
        return True


@_register
class Culling(CardBehavior):
    name = 'Culling'
    tags = ['Discontent']
    deck = 'claw'
    def on_dawn(self, ctx):
        all_players = sorted(ctx.state.players, key=lambda p: len(p.domain), reverse=True)
        max_count = len(all_players[0].domain)
        tied = [p for p in all_players if len(p.domain) == max_count]
        target = (ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, tied,
            DecisionContext(event="Dawn", source="Culling", intent=Intent.TARGET))
            if len(tied) > 1 else tied[0])
        if target.domain:
            to_discard = ctx.engine.strat(target).resolve_n(
                ctx.state, target, list(target.domain),
                1, min(2, len(target.domain)),
                DecisionContext(event="Dawn", source="Culling", intent=Intent.GIVE_AWAY))
            for c in to_discard:
                target.discard_from_domain(c)
                ctx.state.log(f"  → Culling: {target.name} discards {c.name}")
        ctx.discard_self()


@_register
class Ivory(CardBehavior):
    name = 'Ivory'
    tags = ['Trophy', 'Wealth']
    deck = 'claw'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        ctx.state.log(f"  → Ivory: sold at market")
        ctx.discard_self()
        ctx.engine.order_zone(ctx.player, "coin")


@_register
class MartialExcellence(CardBehavior):
    name = 'Martial Excellence'
    tags = ['Trophy', 'Chivalry']
    deck = 'claw'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        # Prereq: need another Trophy tag in domain (besides this card)
        other_trophies = [c for c in ctx.player.domain
                         if c.has_tag("Trophy") and c is not ctx.card]
        if not other_trophies:
            return
        ctx.state.log(f"  → Martial Excellence: proven warrior enters the Tourney")
        ctx.engine.order_zone(ctx.player, "sword")


@_register
class Hunger(CardBehavior):
    name = 'Hunger'
    tags = ['Discontent']
    deck = 'claw'
    def on_harvest(self, ctx):
        """Hunger persists despite harvest — top claw card lost to owner's discard."""
        killed = ctx.state.draw_from_pile("claw")
        if killed:
            ctx.player.discard.append(killed)
            ctx.state.log(f"  → Hunger: {ctx.player.name} loses {killed.name} from claw pile (to discard)")
        return True

    def on_feast(self, ctx):
        """Properly fed — recycle 1 card from own discard to top of claw pile."""
        s = ctx.state
        candidates = list(ctx.player.discard)
        if not candidates:
            return False
        pick = ctx.engine.strat(ctx.player).resolve(
            s, ctx.player, candidates,
            DecisionContext(event="Feast", source="Hunger", intent=Intent.OPTION))
        if pick is None:
            return False
        ctx.player.discard.remove(pick)
        s.return_to_pile("claw", pick)
        s.log(f"  → Hunger: {ctx.player.name} recycles {pick.name} from discard to claw pile")
        return True


@_register
class Uprising(CardBehavior):
    name = 'Uprising'
    tags = ['Discontent']
    deck = 'claw'
    def on_dawn(self, ctx):
        ctx.state.log(f"  → Dawn: Uprising — self-Brawl (no benefits)")
        ctx.engine.resolve_event("Brawl", ctx.player, ctx.player, uprising=True)
        ctx.discard_self()


@_register
class SpoilsOfWar(CardBehavior):
    name = 'Spoils of War'
    tags = ['Trophy', 'Mob']
    deck = 'claw'
    def on_dawn(self, ctx):
        targets = ctx.state.other_players(ctx.player)
        if targets:
            target = ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, targets,
                DecisionContext(event="Dawn", source="Spoils of War", intent=Intent.TARGET))
            ctx.player.remove_from_domain(ctx.card)
            target.add_to_domain(ctx.card, ctx.state)
            ctx.state.log(f"  → Spoils of War placed in {target.name}'s Domain")

    def on_brawl(self, ctx):
        if ctx.uprising:
            ctx.state.log(f"  → Spoils of War: no effect (Uprising)")
            return True
        ctx.player.remove_from_domain(ctx.card)
        ctx.active_player.add_to_domain(ctx.card, ctx.state)
        trophy_count = ctx.active_player.count_tag("Trophy")
        ctx.state.log(f"  → Spoils of War → {ctx.active_player.name}, draws {trophy_count} Claw + {trophy_count} Tree")
        ctx.engine.draw_and_receive(ctx.active_player, "claw", trophy_count)
        ctx.engine.draw_and_receive(ctx.active_player, "tree", trophy_count)
        return True


@_register
class DuskRite(CardBehavior):
    name = 'Dusk Rite'
    tags = ['Spiritual', 'Discontent']
    deck = 'claw'
    def on_order(self, ctx):
        if ctx.location != "domain" or len(ctx.player.discard) <= 0:
            return
        if ctx.player.discard:
            to_remove = ctx.engine.strat(ctx.player).resolve_n(
                ctx.state, ctx.player, list(ctx.player.discard),
                1, len(ctx.player.discard),
                DecisionContext(event="Order", source="Dusk Rite", intent=Intent.DISCARD))
            for c in to_remove:
                ctx.player.discard.remove(c)
            removed_count = len(to_remove)
            ctx.state.log(f"  → removes {removed_count} cards from discard permanently")
            for c in ctx.engine.draw_and_receive(ctx.player, "claw", removed_count):
                ctx.state.log(f"  → draws {c.name} from Claw")
            for c in ctx.engine.draw_and_receive(ctx.player, "tree", removed_count):
                ctx.state.log(f"  → draws {c.name} from Tree")
            ctx.player.discard_from_domain(ctx.card)
            ctx.state.log(f"  → discards Dusk Rite, Rite")
            ctx.engine.resolve_event("Rite", ctx.player)


@_register
class BloodFeud(CardBehavior):
    name = 'Blood Feud'
    tags = ['Mob', 'Discontent']
    deck = 'claw'
    def on_brawl(self, ctx):
        if ctx.uprising:
            return False
        # Draw 2 from claw
        drawn = ctx.engine.draw_and_receive(ctx.player, "claw", 2)
        for c in drawn:
            ctx.state.log(f"  → Blood Feud: {ctx.player.name} draws {c.name}")
        # Move up to 2 Mob cards to the attacker
        mobs = [c for c in ctx.player.domain if c.has_tag("Mob") and c is not ctx.card]
        to_move = min(2, len(mobs))
        for i in range(to_move):
            mob = mobs[i]
            ctx.player.remove_from_domain(mob)
            ctx.active_player.add_to_domain(mob, ctx.state)
            ctx.state.log(f"  → Blood Feud: moves {mob.name} to {ctx.active_player.name}")
        # Discard self before retaliating
        ctx.player.discard_from_domain(ctx.card)
        ctx.state.log(f"  → Blood Feud discarded")
        # Retaliate — brawl the attacker back
        ctx.state.log(f"  → Blood Feud: {ctx.player.name} retaliates!")
        ctx.engine.resolve_event("Brawl", ctx.player, ctx.active_player)
        return True


@_register
class Enforcers(CardBehavior):
    name = 'Enforcers'
    tags = ['Mob', 'Discontent']
    deck = 'claw'
    def on_brawl(self, ctx):
        if ctx.uprising:
            return False
        # Both sides draw 2 claw — arms race
        for c in ctx.engine.draw_and_receive(ctx.player, "claw", 2):
            ctx.state.log(f"  → Enforcers: {ctx.player.name} draws {c.name}")
        for c in ctx.engine.draw_and_receive(ctx.active_player, "claw", 2):
            ctx.state.log(f"  → Enforcers: {ctx.active_player.name} draws {c.name}")
        return True
