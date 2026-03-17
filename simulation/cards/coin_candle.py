"""Coin and Candle deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Mine(CardBehavior):
    name = 'Mine'
    tags = ['Labour']
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain" or ctx.state.pile_remaining("coin") <= 0:
            return
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → Mine draws {drawn[0].name} from Coin")

    def on_dawn(self, ctx):
        if not ctx.player.has_card("Crags"):
            ctx.state.log(f"  → Dawn: no Crags → Mine to discard")
            ctx.player.discard.append(ctx.card)


@_register
class WorshipOfTheFlame(CardBehavior):
    name = 'Worship of the Flame'
    tags = ['Spiritual']
    deck = 'candle'
    def on_rite(self, ctx):
        # Draws handled by engine after counting all Spiritual responders
        # Just signal that we responded
        return True
