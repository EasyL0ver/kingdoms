"""Tree search strategy — simulate each action, evaluate outcomes, pick the best.

Replaces the old heuristic-scoring approach with a depth-1 lookahead:
for each valid action, deep-copy the state, execute the action,
evaluate the resulting board, and pick the action with the best outcome.
"""
from __future__ import annotations
import copy
import random
from state import GameState, Player, Card, Action
from strategy import Strategy, Intent, DecisionContext


def evaluate(state: GameState, player: Player) -> float:
    """Score a board position from player's perspective."""
    score = 0.0

    score += player.count_tag("Trophy") * 3.0
    score += player.count_tag("Nature") * 3.0
    score += player.count_tag("Amenity") * 3.0
    score += player.count_tag("Knowledge") * 1.5
    score += player.count_tag("Spiritual") * 1.0
    score += len(player.domain) * 0.5
    score -= player.count_tag("Discontent") * 2.0

    # Bonus for winning tags relative to opponents
    win_tags = {"claw": "Trophy", "tree": "Nature", "wheat": "Amenity"}
    for deck, tag in win_tags.items():
        my_count = player.count_tag(tag)
        max_opp = max(
            (p.count_tag(tag) for p in state.players if p is not player),
            default=0,
        )
        score += (my_count - max_opp) * 2.0

    return score


# ── Greedy sub-decision strategy ──────────────────────────────────────

class GreedyStrategy(Strategy):
    """Simple greedy resolver for sub-decisions during simulation."""

    name = "greedy"

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    @staticmethod
    def _card_value(card: Card) -> float:
        value = 0.0
        for tag in card.tags:
            if tag in ("Trophy", "Nature", "Amenity"):
                value += 3.0
            elif tag in ("Knowledge", "Spiritual"):
                value += 1.5
            elif tag == "Discontent":
                value -= 2.0
            else:
                value += 0.5
        return value

    def resolve(self, state, player, options, ctx):
        if not options:
            return None
        if len(options) == 1:
            return options[0]

        match ctx.intent:
            case Intent.GAIN:
                if hasattr(options[0], "tags"):
                    return max(options, key=self._card_value)
            case Intent.DISCARD | Intent.GIVE_AWAY:
                if hasattr(options[0], "tags"):
                    return min(options, key=self._card_value)
            case Intent.TARGET:
                if hasattr(options[0], "domain"):
                    return max(options, key=lambda p: len(p.domain))
            case Intent.OPTION:
                if options == [True, False]:
                    return True
        return options[0]

    def sequence(self, state, player, items, ctx):
        return list(items)

    def resolve_n(self, state, player, options, min_n, max_n, ctx):
        n = min(max_n, len(options))
        if n <= min_n:
            return list(options[:n])
        if ctx.intent == Intent.GAIN and options and hasattr(options[0], "tags"):
            return sorted(options, key=self._card_value, reverse=True)[:n]
        if ctx.intent in (Intent.DISCARD, Intent.GIVE_AWAY) and options and hasattr(options[0], "tags"):
            return sorted(options, key=self._card_value)[:n]
        return list(options[:n])


# ── Tree search strategy ─────────────────────────────────────────────

class TreeSearchStrategy(Strategy):
    """Depth-1 lookahead: simulate each Order action, pick the best outcome.

    Top-level Order selection uses tree search.
    All sub-decisions (during both simulation and real execution) use greedy.
    """

    name = "tree_search"

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self._greedy = GreedyStrategy(self.rng)

    def resolve(self, state, player, options, ctx):
        if ctx.event == "Dawn" and ctx.source == "Presence":
            return self._search(state, player, options)
        return self._greedy.resolve(state, player, options, ctx)

    def sequence(self, state, player, items, ctx):
        return self._greedy.sequence(state, player, items, ctx)

    def resolve_n(self, state, player, options, min_n, max_n, ctx):
        return self._greedy.resolve_n(state, player, options, min_n, max_n, ctx)

    # ── Core search ──

    def _search(self, state: GameState, player: Player, actions: list[Action]) -> Action:
        baseline = evaluate(state, player)
        scored: list[tuple[Action, float]] = []

        for action in actions:
            score = self._simulate(state, player, action)
            scored.append((action, score - baseline))

        # If any action improves the position, pick the best
        positive = [(a, d) for a, d in scored if d > 0]
        if positive:
            return max(positive, key=lambda x: x[1])[0]

        # All actions are neutral or bad — pick randomly to avoid loops
        return self.rng.choice(actions)

    def _simulate(self, state: GameState, player: Player, action: Action) -> float:
        if action.type == "pass":
            return evaluate(state, player)

        sim_state = copy.deepcopy(state)
        sim_player = sim_state.player_by_name(player.name)
        sim_card = self._find_card(sim_state, sim_player, action)

        if not sim_card:
            return float("-inf")

        # Silence logging
        sim_state.log = lambda msg: None

        greedy_strats = {p.name: GreedyStrategy(random.Random(42)) for p in sim_state.players}

        from engine import GameEngine
        sim_engine = GameEngine(sim_state, greedy_strats, observers=[])

        try:
            beh = sim_engine.behavior(sim_card)
            ctx = sim_engine.make_ctx(sim_player, sim_card)
            beh.on_order(ctx)
        except Exception:
            return float("-inf")

        return evaluate(sim_state, sim_player)

    @staticmethod
    def _find_card(sim_state: GameState, sim_player: Player, action: Action) -> Card | None:
        card_name = action.card.name

        if card_name == "Presence":
            return sim_player.domain_card

        if action.type == "order_well":
            owner_name = action.owner.name
            for p in sim_state.players:
                if p.name == owner_name:
                    return p.get_card("Well")
            return None

        if "from discard" in action.label:
            return sim_player.get_discard_card(card_name)

        return sim_player.get_card(card_name)
