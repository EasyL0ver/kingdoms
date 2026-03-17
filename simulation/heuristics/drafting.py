"""Drafting and resource management heuristics."""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import Heuristic, _register_heuristic
from strategy import Intent

if TYPE_CHECKING:
    from state import GameState, Player
    from strategy import DecisionContext


@_register_heuristic
class FavorClaw(Heuristic):
    """Prefer drafting from the Claw zone over Tree."""
    name = "favor_claw"

    def score_resolve(self, state, player, options, ctx):
        if ctx.source != "Domain" or ctx.intent != Intent.OPTION:
            return {}
        scores = {}
        for o in options:
            if o == "claw":
                scores[o] = 3.0
            elif o == "tree":
                scores[o] = -0.5
        return scores


@_register_heuristic
class FavorTree(Heuristic):
    """Prefer drafting from the Tree zone over Claw."""
    name = "favor_tree"

    def score_resolve(self, state, player, options, ctx):
        if ctx.source != "Domain" or ctx.intent != Intent.OPTION:
            return {}
        scores = {}
        for o in options:
            if o == "tree":
                scores[o] = 3.0
            elif o == "claw":
                scores[o] = -0.5
        return scores


@_register_heuristic
class Hoarder(Heuristic):
    """Prefer gaining cards, avoid sacrificing valuable ones.

    State-aware: protects cards with more tags (assumed more valuable).
    """
    name = "hoarder"

    def score_resolve(self, state, player, options, ctx):
        if ctx.intent == Intent.GAIN:
            scores = []
            for o in options:
                if hasattr(o, "tags"):
                    scores.append((o, 0.5 * len(o.tags)))
            return scores

        if ctx.intent in (Intent.DISCARD, Intent.GIVE_AWAY):
            # Protect cards with many tags (negate gain + explicit protection)
            scores = []
            for o in options:
                if hasattr(o, "tags"):
                    scores.append((o, -0.5 * len(o.tags)))
            return scores

        if ctx.intent == Intent.OPTION and True in options and False in options:
            return {True: 0.3, False: -0.3}

        return {}
