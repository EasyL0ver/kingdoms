"""Coin and Candle deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Rumour(CardBehavior):
    name = 'Rumour'
    tags = []
    deck = 'coin'
    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        ctx.state.log(f"  → Drafted: Rumour triggers!")
        ctx.engine.resolve_event("Rumour", ctx.player)
        ctx.discard_self()


@_register
class Mine(CardBehavior):
    name = 'Mine'
    tags = ['Labour']
    deck = 'coin'
    def can_activate(self, ctx):
        return ctx.location == "domain" and ctx.state.pile_remaining("coin") > 0

    def on_activate(self, ctx):
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → Mine draws {drawn[0].name} from Coin")

    def on_location_change(self, ctx, from_loc, to_loc):
        if from_loc != "pile":
            return
        if not ctx.player.has_card("Crags"):
            ctx.state.log(f"  → Drafted: no Crags → Mine to discard")
            ctx.player.discard.append(ctx.card)
            return
        ctx.player.discard_from_domain(ctx.player.get_card("Crags"))
        ctx.state.log(f"  → Drafted: discards Crags to keep Mine")


@_register
class WorshipOfTheFlame(CardBehavior):
    name = 'Worship of the Flame'
    tags = ['Spiritual']
    deck = 'candle'
    def on_event(self, ctx):
        if not ctx.responds_to("Rite"):
            return False
        # Draws handled by engine after counting all Spiritual responders
        # Just signal that we responded
        return True
