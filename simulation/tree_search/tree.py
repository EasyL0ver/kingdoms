"""Naive decision tree — builds the full tree of all player decisions for one Dawn."""
from __future__ import annotations
import copy
import random
import time as _time
from dataclasses import dataclass, field
from strategy import Strategy, DecisionContext, RandomStrategy


@dataclass
class TreeNode:
    """A branch in the decision tree."""
    source: str             # which card/event caused this decision
    event: str              # event context
    options: list[str]      # human-readable labels
    children: dict = field(default_factory=dict)  # option_index -> TreeNode | LeafNode
    depth: int = 0


@dataclass
class LeafNode:
    """Terminal — Dawn resolved with no more decisions."""
    depth: int = 0
    score: float = 0.0


class _CapturedException(Exception):
    """Raised to interrupt Dawn when we capture a decision point."""
    def __init__(self, options, ctx):
        self.options = options
        self.ctx = ctx


class _CaptureStrategy(Strategy):
    """Captures the Nth multi-option decision by raising an exception.
    Decisions before N are answered with the prescribed choices."""

    name = "capture"

    def __init__(self, prior_choices: list[int]):
        self._prior = list(prior_choices)
        self._decision_idx = 0

    def sequence(self, state, player, items, ctx):
        return list(items)

    def resolve(self, state, player, options, ctx):
        if not options:
            return None
        if len(options) == 1:
            return options[0]
        idx = self._decision_idx
        self._decision_idx += 1
        if idx < len(self._prior):
            # Replay a prior choice
            pick = min(self._prior[idx], len(options) - 1)
            return options[pick]
        # This is the new decision — capture it
        raise _CapturedException(options, ctx)

    def resolve_n(self, state, player, options, min_n, max_n, ctx):
        n = min(max_n, len(options))
        if n <= min_n:
            return list(options[:n])
        return list(options[:n])


def _label(opt) -> str:
    if hasattr(opt, "name"):
        return opt.name
    return str(opt)


# Heuristic priority for branch ordering (lower = explored first).
# Tier 0: Zone orders (guaranteed draws)
_ZONE_NAMES = {"Presence", "Claw Zone", "Tree Zone", "Wheat Zone", "Coin Zone",
               "Candle Zone", "Sword Zone"}
# Tier 1: Cards whose on_order cascades into secondary events
_CASCADE_EVENT = {
    "Warband": "Brawl", "Racketeering": "Brawl", "Tyranny": "Brawl",
    "Swindle": "Brawl",                                                # → Brawl
    "Blood Offering": "Rite", "Veil Tear": "Rite",
    "Sacred Grove": "Rite", "Purity": "Rite",                          # → Rite
    "Poach": "Feast", "Forage": "Feast", "Granary": "Feast",
    "Animal Husbandry": "Feast", "Royal Hunt": "Feast",                # → Feast
    "Benefaction": "Rumour",                                            # → Rumour
    "Sowing": "Order", "Compost": "Order",
    "Pawn Shop": "Order", "Stockpile": "Order", "Market": "Order",
    "Forgery": "Order", "Usurer": "Order",
    "Ivory": "Order", "Martial Excellence": "Order",
    "Efficiency": "Order", "Clergy": "Order",                           # → zone Order
}


def _count_responders(player, event: str) -> int:
    """Count how many cards in player's domain respond to an event."""
    from cards import CardBehavior, get_behavior
    handler_name = f"on_{event.lower()}"
    base = getattr(CardBehavior, handler_name)
    count = 0
    for card in player.domain:
        beh = get_behavior(card.name)
        if getattr(type(beh), handler_name) is not base:
            count += 1
    return count


def _branch_priority(label: str, player=None) -> tuple[int, int]:
    """Returns (tier, -responder_count) for sorting. Lower = explored first."""
    if label in _ZONE_NAMES:
        return (0, 0)
    event = _CASCADE_EVENT.get(label)
    if event:
        # Cascading card — rank by how many responders we have for its event
        listeners = _count_responders(player, event) if player else 0
        return (1, -listeners)
    return (2, 0)


def evaluate(state, player_name: str) -> float:
    """Score board from player's perspective using all registered evaluators."""
    from tree_search.evaluators import evaluate as _eval
    p = state.player_by_name(player_name)
    return _eval(state, p)


class _TimeBudgetExceeded(Exception):
    """Raised when the time budget for tree building is exhausted."""


def build_tree(state, player, engine_cls, strategies: dict,
               time_budget: float | None = None,
               rng: random.Random | None = None) -> tuple[TreeNode | LeafNode, dict]:
    """Build the decision tree for one Dawn.

    time_budget: max seconds to spend building. None = unlimited.
    rng: shuffles within priority tiers for variety.
    Branches ordered: zones first, cascading cards second, rest last.
    """
    node_count = 0
    leaf_count = 0
    max_depth = 0
    deadline = _time.perf_counter() + time_budget if time_budget else None

    def _explore(prior_choices: list[int], depth: int) -> TreeNode | LeafNode:
        nonlocal node_count, leaf_count, max_depth

        if deadline and _time.perf_counter() >= deadline:
            raise _TimeBudgetExceeded

        sim = copy.deepcopy(state)
        sim.log = lambda msg: None
        sim_player = sim.player_by_name(player.name)

        capture = _CaptureStrategy(prior_choices)
        strats = dict(strategies)
        strats[player.name] = capture

        eng = engine_cls(sim, strats, observers=[])

        try:
            eng.resolve_event("Dawn", sim_player, scope=sim_player)
        except _CapturedException as e:
            # Found a decision point — branch
            options, ctx = e.options, e.ctx
            labels = [_label(o) for o in options]

            # Prune: deduplicate options with same label
            seen: dict[str, int] = {}
            unique_indices: list[int] = []
            for i, lbl in enumerate(labels):
                if lbl not in seen:
                    seen[lbl] = i
                    unique_indices.append(i)

            # Order branches: zones first, cascades ranked by listener count
            if rng:
                rng.shuffle(unique_indices)
            unique_indices.sort(key=lambda i: _branch_priority(labels[i], player))

            node = TreeNode(
                source=ctx.source,
                event=ctx.event,
                options=[labels[i] for i in unique_indices],
                depth=depth,
            )
            node_count += 1

            for j, i in enumerate(unique_indices):
                try:
                    node.children[j] = _explore(prior_choices + [i], depth + 1)
                except _TimeBudgetExceeded:
                    break  # keep partially-built node with whatever children we got

            return node
        except Exception:
            pass

        # Dawn completed without hitting a new decision — leaf
        score = evaluate(sim, player.name)
        leaf_count += 1
        max_depth = max(max_depth, depth)
        return LeafNode(depth=depth, score=score)

    try:
        root = _explore([], 0)
    except _TimeBudgetExceeded:
        root = LeafNode(depth=0, score=evaluate(state, player.name))
        leaf_count += 1
    stats = {"nodes": node_count, "leaves": leaf_count, "max_depth": max_depth}
    return root, stats


def best_path(node) -> tuple[float, list[int]]:
    """Find the leaf with highest score. Returns (score, list_of_choice_indices).
    Handles partial trees (nodes with missing children from time budget)."""
    if isinstance(node, LeafNode):
        return node.score, []
    if not node.children:
        return -float('inf'), []
    best_score = -float('inf')
    best_choices: list[int] = []
    for i in sorted(node.children):
        score, path = best_path(node.children[i])
        if score > best_score:
            best_score = score
            best_choices = [i] + path
    return best_score, best_choices


class TreeSearchStrategy(Strategy):
    """Builds a time-budgeted decision tree each Dawn and plays the best path."""

    name = "tree_search"

    def __init__(self, rng=None, time_budget: float = 4.0):
        self.rng = rng or random.Random()
        self.time_budget = time_budget
        self._choices: list[int] = []
        self._decision_idx = 0
        self._last_turn = -1

    def _plan(self, state, player):
        if state.turn_num == self._last_turn:
            return
        from engine import GameEngine
        opponent_strats = {p.name: RandomStrategy(self.rng) for p in state.players}
        root, stats = build_tree(state, player, GameEngine, opponent_strats,
                                 time_budget=self.time_budget, rng=self.rng)
        _, self._choices = best_path(root)
        self._decision_idx = 0
        self._last_turn = state.turn_num

    def sequence(self, state, player, items, ctx):
        # Deterministic order — must match _CaptureStrategy so tree path is valid
        return list(items)

    def resolve(self, state, player, options, ctx):
        if not options:
            return None
        if len(options) == 1:
            return options[0]
        self._plan(state, player)
        if self._decision_idx < len(self._choices):
            idx = self._decision_idx
            self._decision_idx += 1
            pick = min(self._choices[idx], len(options) - 1)
            return options[pick]
        return self.rng.choice(options)

    def resolve_n(self, state, player, options, min_n, max_n, ctx):
        # Match _CaptureStrategy: pick first n, no branching
        n = min(max_n, len(options))
        return list(options[:n])


def print_tree(node, indent=0):
    """Pretty-print a decision tree."""
    prefix = "  " * indent
    if isinstance(node, LeafNode):
        print(f"{prefix}🍂 score={node.score:.0f} (depth={node.depth})")
        return
    print(f"{prefix}🔀 {node.event}/{node.source}: {len(node.options)} options")
    for i, label in enumerate(node.options):
        print(f"{prefix}  [{i}] {label}")
        if i in node.children:
            print_tree(node.children[i], indent + 2)
        else:
            print(f"{prefix}    (unexplored)")
