"""Drafting and resource management heuristics."""
from __future__ import annotations
from typing import TYPE_CHECKING

from heuristics import Heuristic, _register_heuristic
from strategy import Intent

if TYPE_CHECKING:
    from state import GameState, Player, Action
    from strategy import DecisionContext


@_register_heuristic
class FavorClaw(Heuristic):
    """Prefer drafting from the Claw zone over Tree."""
    name = "favor_claw"

    def score_option(self, state, player, options, ctx):
        if ctx.source != "Domain" or ctx.intent != Intent.PICK_OPTION:
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

    def score_option(self, state, player, options, ctx):
        if ctx.source != "Domain" or ctx.intent != Intent.PICK_OPTION:
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

    def score_option(self, state, player, options, ctx):
        if ctx.intent == Intent.SACRIFICE:
            scores = []
            for o in options:
                if hasattr(o, "tags"):
                    scores.append((o, -0.5 * len(o.tags)))
            return scores
        if ctx.intent == Intent.GAIN:
            scores = []
            for o in options:
                if hasattr(o, "tags"):
                    scores.append((o, 0.5 * len(o.tags)))
            return scores
        return []

    def score_yes_no(self, state, player, ctx):
        if ctx.intent == Intent.ACCEPT_REJECT:
            if "sacrifice" in ctx.consequence.lower():
                return -1.0
            return 0.3
        return 0.0
