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
