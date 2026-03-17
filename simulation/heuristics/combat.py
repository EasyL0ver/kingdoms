"""Combat-oriented heuristics."""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import Heuristic, _register_heuristic, _leader_player
from strategy import Intent

if TYPE_CHECKING:
    from state import GameState, Player
    from strategy import DecisionContext


@_register_heuristic
class Aggressive(Heuristic):
    """Prefer fights, target the leader, accept offensive abilities.

    State-aware: targets the player with the most domain cards.
    """
    name = "aggressive"

    def score_resolve(self, state, player, options, ctx):
        if ctx.intent == Intent.TARGET:
            leader = _leader_player(state, player)
            if leader and leader in options:
                return [(leader, 3.0)]
            return {}

        if ctx.intent == Intent.OPTION:
            scores = []
            # Prefer Mob cards for ordering (turn actions)
            for a in options:
                if hasattr(a, "card") and a.card and hasattr(a.card, "tags"):
                    if "Mob" in a.card.tags:
                        scores.append((a, 2.0))
            # Prefer brawl events
            for o in options:
                if isinstance(o, str):
                    if o == "brawl":
                        scores.append((o, 2.0))
                    elif o == "rite":
                        scores.append((o, -0.5))
            # Yes/no: aggressive accepts, especially brawls
            if True in options and False in options:
                if "brawl" in ctx.source.lower() or ctx.event == "Brawl":
                    scores.extend([(True, 1.5), (False, -1.5)])
                else:
                    scores.extend([(True, 0.5), (False, -0.5)])
            return scores

        return {}
