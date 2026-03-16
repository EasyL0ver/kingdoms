"""Combat-oriented heuristics."""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import Heuristic, _register_heuristic, _leader_player
from strategy import Intent

if TYPE_CHECKING:
    from state import GameState, Player, Action
    from strategy import DecisionContext


@_register_heuristic
class Aggressive(Heuristic):
    """Prefer fights, target the leader, accept offensive abilities.

    State-aware: targets the player with the most domain cards.
    """
    name = "aggressive"

    def score_activate(self, state, player, actions, ctx):
        scores = []
        for a in actions:
            if hasattr(a, "card") and a.card and hasattr(a.card, "tags"):
                if "Mob" in a.card.tags:
                    scores.append((a, 2.0))
        return scores

    def score_resolution_choice(self, state, player, options, ctx):
        if ctx.intent == Intent.PICK_TARGET:
            leader = _leader_player(state, player)
            if leader and leader in options:
                return [(leader, 3.0)]
        if ctx.intent == Intent.PICK_OPTION:
            scores = {}
            for o in options:
                if isinstance(o, str):
                    if o in ("brawl",):
                        scores[o] = 2.0
                    elif o in ("rite",):
                        scores[o] = -0.5
            return scores
        if ctx.intent == Intent.ACCEPT_REJECT:
            if "brawl" in ctx.source.lower() or "event:Brawl" in ctx.tags:
                return {True: 1.5, False: -1.5}
            return {True: 0.5, False: -0.5}
        return {}
