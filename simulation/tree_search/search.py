"""Tree search strategy — simulate actions, evaluate outcomes, pick the best."""
from __future__ import annotations
import copy
import random
from state import GameState, Player, Card
from strategy import Strategy, Intent, DecisionContext
from tree_search.evaluators import Evaluator, evaluate


def _obj_key(obj):
    """Return a stable identity key for any option object."""
    if hasattr(obj, "id"):
        return ("card", obj.id)
    if hasattr(obj, "name") and hasattr(obj, "domain"):
        return ("player", obj.name)
    return ("val", obj)


# ── Smart opponent strategy for simulation ───────────────────────────

class _OpponentStrategy(Strategy):
    """Evaluator-aware strategy for opponents during simulation.

    Makes realistic choices: discard worst card, gain best card, target leader.
    No branching/deepcopy — just inline evaluation.
    """

    name = "opponent"

    def __init__(self, evaluators: list[Evaluator] | None = None):
        self.evaluators = evaluators

    def resolve(self, state, player, options, ctx):
        if not options:
            return None
        if len(options) == 1:
            return options[0]

        match ctx.intent:
            case Intent.GAIN:
                if hasattr(options[0], "tags"):
                    best, best_s = options[0], float("-inf")
                    for card in options:
                        player.domain.append(card)
                        s = evaluate(state, player, self.evaluators)
                        player.domain.pop()
                        if s > best_s:
                            best_s = s
                            best = card
                    return best
            case Intent.DISCARD | Intent.GIVE_AWAY:
                if hasattr(options[0], "tags"):
                    best, best_s = options[0], float("-inf")
                    for card in options:
                        if card in player.domain:
                            player.domain.remove(card)
                            s = evaluate(state, player, self.evaluators)
                            player.domain.append(card)
                        else:
                            s = evaluate(state, player, self.evaluators)
                        if s > best_s:
                            best_s = s
                            best = card
                    return best
            case Intent.TARGET:
                if hasattr(options[0], "domain"):
                    return max(options, key=lambda p: evaluate(state, p, self.evaluators))
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
        picked = []
        remaining = list(options)
        for _ in range(n):
            if not remaining:
                break
            choice = self.resolve(state, player, remaining, ctx)
            picked.append(choice)
            remaining.remove(choice)
        return picked


# ── Scripted strategy for replay ──────────────────────────────────────

class ScriptedStrategy(Strategy):
    """Returns predetermined choices in sequence. Records chosen IDs for replay."""

    name = "scripted"

    def __init__(self, choices: list):
        self._choices = list(choices)
        self._idx = 0
        self.chosen_keys: list = []

    def resolve(self, state, player, options, ctx):
        if not options:
            return None
        if len(options) == 1:
            result = options[0]
            self.chosen_keys.append(_obj_key(result))
            return result
        if self._idx < len(self._choices):
            pick = self._choices[self._idx]
            self._idx += 1
            if isinstance(pick, int) and pick < len(options):
                result = options[pick]
                self.chosen_keys.append(_obj_key(result))
                return result
            if pick in options:
                self.chosen_keys.append(_obj_key(pick))
                return pick
        result = options[0]
        self.chosen_keys.append(_obj_key(result))
        return result

    def sequence(self, state, player, items, ctx):
        return list(items)

    def resolve_n(self, state, player, options, min_n, max_n, ctx):
        n = min(max_n, len(options))
        if n <= min_n:
            return list(options[:n])
        picked = []
        remaining = list(options)
        for _ in range(n):
            if not remaining:
                break
            choice = self.resolve(state, player, remaining, ctx)
            picked.append(choice)
            remaining.remove(choice)
        return picked


# ── Recording strategy for discovery ─────────────────────────────────

class RecordingStrategy(Strategy):
    """Records all decision points and their options during a simulation run."""

    name = "recording"

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.decisions: list[tuple[list, int]] = []
        self.chosen_keys: list = []

    def resolve(self, state, player, options, ctx):
        if not options:
            return None
        if len(options) == 1:
            result = options[0]
            self.chosen_keys.append(_obj_key(result))
            return result
        chosen = 0
        self.decisions.append((list(range(len(options))), chosen))
        result = options[chosen]
        self.chosen_keys.append(_obj_key(result))
        return result

    def sequence(self, state, player, items, ctx):
        return list(items)

    def resolve_n(self, state, player, options, min_n, max_n, ctx):
        n = min(max_n, len(options))
        if n <= min_n:
            return list(options[:n])
        picked = []
        remaining = list(options)
        for _ in range(n):
            if not remaining:
                break
            choice = self.resolve(state, player, remaining, ctx)
            picked.append(choice)
            remaining.remove(choice)
        return picked


# ── Tree search strategy ─────────────────────────────────────────────

class TreeSearchStrategy(Strategy):
    """Full decision tree search: branch on every sub-decision, evaluate at leaves.

    For each top-level action:
    1. Discovery run: execute on a copy with RecordingStrategy to find decision points
    2. For each combination of choices at those decision points, replay with
       ScriptedStrategy and evaluate the resulting leaf state
    3. Pick the action + choice combo with the best leaf score

    Caps branching: max 3 options per decision, max 2 decision points explored.
    Further sub-decisions use first-option fallback.
    """

    name = "tree_search"

    MAX_OPTIONS_PER_DECISION = 3
    MAX_DECISIONS = 2

    def __init__(self, rng: random.Random | None = None,
                 evaluators: list[Evaluator] | None = None):
        self.rng = rng or random.Random()
        self.evaluators = evaluators
        self._best_keys: list = []
        self._replay_idx = 0

    def resolve(self, state, player, options, ctx):
        if ctx.event == "Turn" and ctx.source == "Presence":
            return self._search(state, player, options)
        if not options:
            return None
        if len(options) == 1:
            return options[0]
        return self._replay_pick(options)

    def _replay_pick(self, options):
        """Pick the option matching the next best key from tree search."""
        if self._replay_idx < len(self._best_keys):
            target_key = self._best_keys[self._replay_idx]
            self._replay_idx += 1
            for opt in options:
                if _obj_key(opt) == target_key:
                    return opt
        return options[0]

    def sequence(self, state, player, items, ctx):
        # Cancellers first on Brawl, info cards first on Rumour
        PRIORITY = {
            "Brawl": {"Militia": 0, "Sellsword": 0, "Zealot": 0, "Eldership": 1},
            "Rumour": {"Village Gossip": 0, "Market": 1},
            "Rite": {"Worship of the Relic": 0, "Worship of the Scripture": 1, "Worship of the Martyr": 2},
        }
        priorities = PRIORITY.get(ctx.event, {})
        if not priorities:
            return list(items)
        default = len(priorities)
        return sorted(items, key=lambda c: priorities.get(c.name, default))

    def resolve_n(self, state, player, options, min_n, max_n, ctx):
        n = min(max_n, len(options))
        if n <= min_n:
            return list(options[:n])
        picked = []
        remaining = list(options)
        for _ in range(n):
            if not remaining:
                break
            choice = self.resolve(state, player, remaining, ctx)
            picked.append(choice)
            remaining.remove(choice)
        return picked

    @staticmethod
    def _hide_pile_order(sim_state: GameState):
        """Shuffle undrawn portion of every pile so the sim can't see draw order."""
        for zone in sim_state.zone_cards.values():
            ptr = zone.pile_ptr
            if ptr < len(zone.pile) - 1:
                undrawn = zone.pile[ptr:]
                random.shuffle(undrawn)
                zone.pile[ptr:] = undrawn

    # ── Core search ──

    def _search(self, state: GameState, player: Player, options: list[Card]) -> Card:
        best_card = None
        best_score = float("-inf")
        best_keys: list = []

        for card in options:
            score, chosen_keys = self._evaluate_card(state, player, card)
            if score > best_score:
                best_score = score
                best_card = card
                best_keys = chosen_keys

        self._best_keys = best_keys
        self._replay_idx = 0
        return best_card or options[0]

    def _evaluate_card(self, state: GameState, player: Player,
                       card: Card) -> tuple[float, list]:
        """Evaluate ordering a card by branching on sub-decisions."""
        decision_points, discovery_score, discovery_keys = self._discover_decisions(state, player, card)

        if decision_points is None:
            return float("-inf"), []

        if not decision_points:
            return discovery_score, discovery_keys

        combos = self._generate_combos(decision_points)

        best_score = discovery_score
        best_keys = discovery_keys

        for combo in combos[1:]:
            score, chosen_keys = self._run_with_choices(state, player, card, combo)
            if score > best_score:
                best_score = score
                best_keys = chosen_keys

        return best_score, best_keys

    def _discover_decisions(self, state: GameState, player: Player,
                            card: Card) -> tuple[list[int] | None, float, list]:
        """Run Order on card with RecordingStrategy to discover decision points."""
        sim_state = copy.deepcopy(state)
        self._hide_pile_order(sim_state)
        sim_player = sim_state.player_by_name(player.name)
        sim_card = self._find_card_in_state(sim_state, sim_player, card)
        if not sim_card:
            return None, float("-inf"), []

        sim_state.log = lambda msg: None
        recorder = RecordingStrategy()
        strats = {p.name: _OpponentStrategy(self.evaluators) for p in sim_state.players}
        strats[sim_player.name] = recorder

        from engine import GameEngine
        sim_engine = GameEngine(sim_state, strats, observers=[])

        try:
            sim_engine.resolve_event("Order", sim_player, scope=sim_card)
        except Exception:
            return None, float("-inf"), []

        leaf_score = evaluate(sim_state, sim_player, self.evaluators)

        if not recorder.decisions:
            return [], leaf_score, recorder.chosen_keys

        points = [
            min(len(opts), self.MAX_OPTIONS_PER_DECISION)
            for opts, _ in recorder.decisions[:self.MAX_DECISIONS]
        ]
        return points, leaf_score, recorder.chosen_keys


    def _generate_combos(self, decision_points: list[int]) -> list[list[int]]:
        """Generate all index combinations across decision points."""
        if not decision_points:
            return [[]]
        combos = [[]]
        for n_opts in decision_points:
            combos = [c + [i] for c in combos for i in range(n_opts)]
        return combos

    def _run_with_choices(self, state: GameState, player: Player,
                          card: Card, choices: list[int]) -> tuple[float, list[int | None]]:
        """Run Order on card with predetermined choices, return (leaf_score, chosen_ids)."""
        sim_state = copy.deepcopy(state)
        self._hide_pile_order(sim_state)
        sim_player = sim_state.player_by_name(player.name)
        sim_card = self._find_card_in_state(sim_state, sim_player, card)
        if not sim_card:
            return float("-inf"), []

        sim_state.log = lambda msg: None
        scripted = ScriptedStrategy(choices)
        strats = {p.name: _OpponentStrategy(self.evaluators) for p in sim_state.players}
        strats[sim_player.name] = scripted

        from engine import GameEngine
        sim_engine = GameEngine(sim_state, strats, observers=[])

        try:
            sim_engine.resolve_event("Order", sim_player, scope=sim_card)
        except Exception:
            return float("-inf"), []

        return evaluate(sim_state, sim_player, self.evaluators), scripted.chosen_keys

    @staticmethod
    def _find_card_in_state(sim_state: GameState, sim_player: Player, original: Card) -> Card | None:
        """Find the deepcopy equivalent of original card in the simulated state."""
        if original.name == "Presence":
            return sim_player.domain_card

        # Check domain
        for c in sim_player.domain:
            if c.id == original.id:
                return c

        # Check discard
        for c in sim_player.discard:
            if c.id == original.id:
                return c

        # Check other players' domains (Wells)
        for p in sim_state.players:
            if p is sim_player:
                continue
            for c in p.domain:
                if c.id == original.id:
                    return c

        return None
