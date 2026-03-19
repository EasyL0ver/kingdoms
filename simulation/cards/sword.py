"""Sword deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class RoyalHunt(CardBehavior):
    name = 'Royal Hunt'
    tags = ['Unit', 'Trophy', 'Hunt']
    deck = 'sword'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        # Only works if no other player has a Hunt card in domain
        for p in ctx.state.players:
            if p is ctx.player:
                continue
            if p.cards_with_tag("Hunt"):
                ctx.state.log(f"  → Royal Hunt blocked: {p.name} has Hunt in domain")
                return
        # Hunt: discard top 2 from claw pile
        for i in range(2):
            killed = ctx.state.draw_from_pile("claw")
            if killed:
                ctx.player.discard.append(killed)
                ctx.state.log(f"  → Royal Hunt: hunts {killed.name} (to discard)")
        # Feast twice
        for i in range(2):
            ctx.state.log(f"  → Feast ({i+1}/2) in {ctx.player.name}'s Domain")
            ctx.engine.resolve_event("Feast", ctx.player, ctx.player)
            if ctx.state.game_over:
                break
        # Draw 1 from claw
        drawn = ctx.state.draw_from_pile("claw")
        if drawn:
            ctx.state.log(f"  → Royal Hunt: draws {drawn.name} from Claw")
            ctx.engine.receive_card(ctx.player, drawn)


@_register
class KnightOfTheGoldCoat(CardBehavior):
    name = 'Knight of the Gold Coat'
    tags = ['Unit', 'Chivalry', 'Wealth']
    deck = 'sword'

    def _hunt_unit(self, ctx, event_name):
        all_units = []
        for p in ctx.state.players:
            for c in p.domain:
                if c.has_tag("Unit") and c is not ctx.card:
                    all_units.append((p, c))
        if not all_units:
            return False
        options = [c for _, c in all_units]
        victim = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, options,
            DecisionContext(event=event_name, source="Knight of the Gold Coat", intent=Intent.TARGET))
        for owner, c in all_units:
            if c is victim:
                owner.discard_from_domain(c)
                ctx.state.log(f"  → Knight of the Gold Coat: destroys {c.name} in {owner.name}'s Domain")
                if owner is not ctx.player:
                    ctx.player.remove_from_domain(ctx.card)
                    owner.add_to_domain(ctx.card, ctx.state)
                    ctx.state.log(f"  → Knight moves to {owner.name}'s Domain")
                return True
        return False

    def on_rumour(self, ctx):
        return self._hunt_unit(ctx, "Rumour")

    def on_brawl(self, ctx):
        return self._hunt_unit(ctx, "Brawl")


@_register
class KnightOfTheIronCrown(CardBehavior):
    name = 'Knight of the Iron Crown'
    tags = ['Unit', 'Chivalry', 'Trophy']
    deck = 'sword'

    def _hunt_unit(self, ctx, event_name):
        all_units = []
        for p in ctx.state.players:
            for c in p.domain:
                if c.has_tag("Unit") and c is not ctx.card:
                    all_units.append((p, c))
        if not all_units:
            return False
        options = [c for _, c in all_units]
        victim = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, options,
            DecisionContext(event=event_name, source="Knight of the Iron Crown", intent=Intent.TARGET))
        for owner, c in all_units:
            if c is victim:
                owner.discard_from_domain(c)
                ctx.state.log(f"  → Knight of the Iron Crown: destroys {c.name} in {owner.name}'s Domain")
                if owner is not ctx.player:
                    ctx.player.remove_from_domain(ctx.card)
                    owner.add_to_domain(ctx.card, ctx.state)
                    ctx.state.log(f"  → Knight moves to {owner.name}'s Domain")
                return True
        return False

    def on_dawn(self, ctx):
        return self._hunt_unit(ctx, "Dawn")


@_register
class KnightOfTheGreenMantle(CardBehavior):
    name = 'Knight of the Green Mantle'
    tags = ['Unit', 'Chivalry', 'Nature']
    deck = 'sword'

    def _hunt_unit(self, ctx, event_name):
        all_units = []
        for p in ctx.state.players:
            for c in p.domain:
                if c.has_tag("Unit") and c is not ctx.card:
                    all_units.append((p, c))
        if not all_units:
            return False
        options = [c for _, c in all_units]
        victim = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, options,
            DecisionContext(event=event_name, source="Knight of the Green Mantle", intent=Intent.TARGET))
        for owner, c in all_units:
            if c is victim:
                owner.discard_from_domain(c)
                ctx.state.log(f"  → Knight of the Green Mantle: destroys {c.name} in {owner.name}'s Domain")
                if owner is not ctx.player:
                    ctx.player.remove_from_domain(ctx.card)
                    owner.add_to_domain(ctx.card, ctx.state)
                    ctx.state.log(f"  → Knight moves to {owner.name}'s Domain")
                return True
        return False

    def on_harvest(self, ctx):
        return self._hunt_unit(ctx, "Harvest")


@_register
class KnightOfTheWhiteShield(CardBehavior):
    name = 'Knight of the White Shield'
    tags = ['Unit', 'Chivalry', 'Amenity']
    deck = 'sword'

    def _hunt_unit(self, ctx, event_name):
        all_units = []
        for p in ctx.state.players:
            for c in p.domain:
                if c.has_tag("Unit") and c is not ctx.card:
                    all_units.append((p, c))
        if not all_units:
            return False
        options = [c for _, c in all_units]
        victim = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, options,
            DecisionContext(event=event_name, source="Knight of the White Shield", intent=Intent.TARGET))
        for owner, c in all_units:
            if c is victim:
                owner.discard_from_domain(c)
                ctx.state.log(f"  → Knight of the White Shield: destroys {c.name} in {owner.name}'s Domain")
                if owner is not ctx.player:
                    ctx.player.remove_from_domain(ctx.card)
                    owner.add_to_domain(ctx.card, ctx.state)
                    ctx.state.log(f"  → Knight moves to {owner.name}'s Domain")
                return True
        return False

    def on_feast(self, ctx):
        return self._hunt_unit(ctx, "Feast")


@_register
class KnightOfTheHolyCross(CardBehavior):
    name = 'Knight of the Holy Cross'
    tags = ['Unit', 'Chivalry', 'Religion']
    deck = 'sword'

    def _hunt_unit(self, ctx, event_name):
        all_units = []
        for p in ctx.state.players:
            for c in p.domain:
                if c.has_tag("Unit") and c is not ctx.card:
                    all_units.append((p, c))
        if not all_units:
            return False
        options = [c for _, c in all_units]
        victim = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, options,
            DecisionContext(event=event_name, source="Knight of the Holy Cross", intent=Intent.TARGET))
        for owner, c in all_units:
            if c is victim:
                owner.discard_from_domain(c)
                ctx.state.log(f"  → Knight of the Holy Cross: destroys {c.name} in {owner.name}'s Domain")
                if owner is not ctx.player:
                    ctx.player.remove_from_domain(ctx.card)
                    owner.add_to_domain(ctx.card, ctx.state)
                    ctx.state.log(f"  → Knight moves to {owner.name}'s Domain")
                return True
        return False

    def on_rite(self, ctx):
        return self._hunt_unit(ctx, "Rite")
