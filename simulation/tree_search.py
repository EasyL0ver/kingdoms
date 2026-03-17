"""Tree search strategy — simulate each action, evaluate outcomes, pick the best.

Replaces the old heuristic-scoring approach with a depth-1 lookahead:
for each valid action, deep-copy the state, execute the action,
evaluate the resulting board, and pick the action with the best outcome.

Evaluators are composable modules that score a board position.
"""
from __future__ import annotations
import copy
import random
from abc import ABC, abstractmethod
from state import GameState, Player, Card, Action
from strategy import Strategy, Intent, DecisionContext


# ── Evaluator system ─────────────────────────────────────────────────

class Evaluator(ABC):
    """Scores a board position from a player's perspective."""
    name: str = ""

    @abstractmethod
    def score(self, state: GameState, player: Player) -> float:
        ...


_EVALUATOR_REGISTRY: dict[str, type[Evaluator]] = {}


def _register_evaluator(cls):
    _EVALUATOR_REGISTRY[cls.name] = cls
    return cls


def get_evaluator(name: str) -> Evaluator:
    if name not in _EVALUATOR_REGISTRY:
        available = ", ".join(sorted(_EVALUATOR_REGISTRY))
        raise ValueError(f"Unknown evaluator '{name}'. Available: {available}")
    return _EVALUATOR_REGISTRY[name]()


def list_evaluators() -> list[str]:
    return sorted(_EVALUATOR_REGISTRY.keys())


def evaluate(state: GameState, player: Player,
             evaluators: list[Evaluator] | None = None) -> float:
    """Sum scores from all evaluators."""
    if not evaluators:
        evaluators = [get_evaluator(n) for n in _EVALUATOR_REGISTRY]
    return sum(e.score(state, player) for e in evaluators)


# ── Built-in evaluators ──────────────────────────────────────────────

@_register_evaluator
class TagValue(Evaluator):
    """Score cards by their tag value."""
    name = "tag_value"

    def score(self, state, player):
        s = 0.0
        s += player.count_tag("Trophy") * 3.0
        s += player.count_tag("Nature") * 3.0
        s += player.count_tag("Amenity") * 3.0
        s += player.count_tag("Knowledge") * 1.5
        s += player.count_tag("Spiritual") * 1.0
        s += len(player.domain) * 0.5
        s -= player.count_tag("Discontent") * 3.0
        return s


@_register_evaluator
class PileProximity(Evaluator):
    """Weight win tags higher when their pile is close to depletion."""
    name = "pile_proximity"

    def score(self, state, player):
        s = 0.0
        pile_health = {}
        for deck in ("claw", "tree", "wheat"):
            remaining = state.pile_remaining(deck)
            if deck == "tree":
                remaining += len(state.season)
            elif deck == "wheat":
                remaining += len(state.fields)
            pile_health[deck] = remaining

        win_tags = {"claw": "Trophy", "tree": "Nature", "wheat": "Amenity"}
        closest = min(pile_health, key=pile_health.get)

        for deck, tag in win_tags.items():
            my_count = player.count_tag(tag)
            max_opp = max(
                (p.count_tag(tag) for p in state.players if p is not player),
                default=0,
            )
            lead = my_count - max_opp
            urgency = max(1, 30 - pile_health[deck]) / 30.0

            # Extra weight for the closest pile
            if deck == closest:
                s += my_count * 2.0
            s += lead * 3.0 * (1.0 + urgency)
        return s


@_register_evaluator
class ZoneAccess(Evaluator):
    """Reward having access to wheat/coin/candle zones."""
    name = "zone_access"

    def score(self, state, player):
        s = 0.0
        if player.has_wheat_access():
            s += 2.0
        if player.has_coin_access():
            s += 2.0
        if player.has_candle_access():
            s += 1.5
        return s


@_register_evaluator
class CardSynergy(Evaluator):
    """Score cards based on whether their synergies are active in the current state."""
    name = "card_synergy"

    def score(self, state, player):
        s = 0.0
        domain_names = set(c.name for c in player.domain)
        has_mobs = player.count_tag("Mob") > 0
        has_knowledge = player.count_tag("Knowledge") > 0
        has_nature = player.count_tag("Nature")
        has_discontent = player.count_tag("Discontent")
        discard_size = len(player.discard)
        claw_remaining = state.pile_remaining("claw")
        tree_remaining = state.pile_remaining("tree")
        coin_remaining = state.pile_remaining("coin")
        candle_remaining = state.pile_remaining("candle")
        has_coin_cards = any(c.deck == "coin" or c.has_tag("Craftsmanship") for c in player.domain)
        has_fields = len(state.fields) > 0
        has_season = len(state.season) > 0

        for card in player.domain:
            match card.name:
                # ── Claw cards ──
                case "Tyranny":
                    # Draws per Discontent, then self-Brawl — good with Discontent + claw pile
                    if has_discontent > 0 and claw_remaining > 0:
                        s += 2.0 + has_discontent * 1.0
                case "Chiefdom":
                    # Needs Mobs to move
                    if has_mobs:
                        s += 2.5
                case "Outriders":
                    # Draws 3 from claw, keeps best
                    if claw_remaining >= 3:
                        s += 2.0
                    elif claw_remaining > 0:
                        s += 0.5
                case "Ransack":
                    # Sacrifice + draw 2 claw + pick season — needs both
                    if len(player.domain) > 1 and (claw_remaining > 0 or has_season):
                        s += 1.5
                case "Blood Offering":
                    # Sacrifice to trigger Rite — good with Spiritual responders
                    spiritual = player.count_tag("Spiritual")
                    if len(player.domain) > 1:
                        s += 0.5 + spiritual * 0.5
                case "Warband":
                    # Brawl — good with Mob responders
                    mob_count = player.count_tag("Mob")
                    s += mob_count * 0.5
                case "Racketeering":
                    others = state.other_players(player)
                    if any(len(p.domain) > 0 for p in others):
                        s += 1.0

                # ── Tree cards ──
                case "Remembrance":
                    if has_knowledge and discard_size > 0:
                        knowledge_count = player.count_tag("Knowledge")
                        recoverable = min(knowledge_count, discard_size)
                        s += recoverable * 1.5
                case "Herbalism":
                    cost_cards = player.count_tag("Knowledge") + has_nature
                    if cost_cards > 1 and discard_size > 0:  # >1 because Herbalism itself is Nature
                        s += 1.5
                case "Forage":
                    if tree_remaining >= 3:
                        s += 1.5
                    elif tree_remaining > 0:
                        s += 0.5
                case "Oral Tradition":
                    if has_coin_cards and candle_remaining > 0:
                        s += 2.0
                case "Sacred Grove":
                    # Rite or Scry — always somewhat useful, better with Spiritual
                    s += 1.0 + player.count_tag("Spiritual") * 0.3
                case "Crags":
                    crags_count = sum(1 for c in player.domain if c.name == "Crags")
                    if claw_remaining > 0:
                        s += 1.0
                    if crags_count >= 2:
                        s += 1.5  # Brawl defense active
                case "Well":
                    if has_season:
                        s += 2.0

                # ── Wheat cards ──
                case "Sowing":
                    if has_nature >= 2 and has_fields:
                        s += 2.0
                case "Withered Crop":
                    has_harvest_discard = any(c.name == "Harvest" for c in player.discard)
                    if has_harvest_discard and has_fields:
                        s += 2.0
                case "Animal Husbandry":
                    s += 1.5  # always flexible (wheat/coin/feast)
                case "Militia":
                    if has_mobs:
                        s += 1.0  # can discard Mobs + Brawl defense
                case "Granary":
                    # Feast trigger — better with Discontent to clear
                    if has_discontent > 0:
                        s += 1.5
                    else:
                        s += 0.5

                # ── Discard-orderable cards ──
                case "Highlander":
                    pass  # handled below
                case "Nomad":
                    pass  # handled below
                case "Dusk Rite":
                    if discard_size > 0 and (claw_remaining > 0 or tree_remaining > 0):
                        s += discard_size * 0.3

        # Discard synergies — cards that can self-rescue
        for card in player.discard:
            if card.name == "Highlander" and "Crags" in domain_names:
                s += 1.5
            elif card.name == "Nomad" and "Pasture" in domain_names:
                s += 1.5

        return s


# ── Scripted strategy for replay ──────────────────────────────────────

class ScriptedStrategy(Strategy):
    """Returns predetermined choices in sequence. Used for replaying branches."""

    name = "scripted"

    def __init__(self, choices: list):
        self._choices = list(choices)
        self._idx = 0

    def resolve(self, state, player, options, ctx):
        if not options:
            return None
        if len(options) == 1:
            return options[0]
        if self._idx < len(self._choices):
            pick = self._choices[self._idx]
            self._idx += 1
            # Find the matching option — pick can be an index or the object itself
            if isinstance(pick, int) and pick < len(options):
                return options[pick]
            if pick in options:
                return pick
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


# ── Recording strategy for discovery ─────────────────────────────────

class RecordingStrategy(Strategy):
    """Records all decision points and their options during a simulation run."""

    name = "recording"

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.decisions: list[tuple[list, int]] = []  # (options, chosen_index)

    def resolve(self, state, player, options, ctx):
        if not options:
            return None
        if len(options) == 1:
            return options[0]
        # Default: pick first option, record the decision
        chosen = 0
        self.decisions.append((list(range(len(options))), chosen))
        return options[chosen]

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

    def resolve(self, state, player, options, ctx):
        if ctx.event == "Dawn" and ctx.source == "Presence":
            return self._search(state, player, options)
        # Sub-decisions during real execution: evaluate each option
        if not options:
            return None
        if len(options) == 1:
            return options[0]
        return self._eval_pick(state, player, options, ctx)

    def _eval_pick(self, state, player, options, ctx):
        """Pick the option that leads to the best evaluated state."""
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

    # ── Core search ──

    def _search(self, state: GameState, player: Player, actions: list[Action]) -> Action:
        best_action = None
        best_score = float("-inf")

        for action in actions:
            score, _ = self._evaluate_action(state, player, action)
            if score > best_score:
                best_score = score
                best_action = action

        baseline = evaluate(state, player, self.evaluators)
        if best_score <= baseline:
            return self.rng.choice(actions)

        return best_action or actions[0]

    def _evaluate_action(self, state: GameState, player: Player,
                         action: Action) -> tuple[float, list]:
        """Evaluate an action by branching on sub-decisions.

        Returns (best_leaf_score, list_of_choice_indices).
        """
        if action.type == "pass":
            return evaluate(state, player, self.evaluators), []

        # Discovery run — find decision points and get baseline leaf score
        decision_points, discovery_score = self._discover_decisions(state, player, action)

        if decision_points is None:
            # Action couldn't run at all
            return float("-inf"), []

        if not decision_points:
            # No sub-decisions — discovery score IS the leaf score
            return discovery_score, []

        # Generate all combinations of choices (capped)
        combos = self._generate_combos(decision_points)

        # Start with discovery run's score (combo [0,0,...] = first option each time)
        best_score = discovery_score
        best_combo = [0] * len(decision_points)

        # Try remaining combos (skip [0,0,...] since discovery already covered it)
        for combo in combos[1:]:
            score = self._run_with_choices(state, player, action, combo)
            if score > best_score:
                best_score = score
                best_combo = combo

        return best_score, best_combo

    def _discover_decisions(self, state: GameState, player: Player,
                            action: Action) -> tuple[list[int] | None, float]:
        """Run action once with RecordingStrategy to discover decision points.

        Returns (decision_point_counts, leaf_score).
        decision_point_counts is None if the action can't execute.
        The leaf score is always the evaluated result of this run — even if
        nothing changed (the current state might still be the best play).
        """
        sim_state = copy.deepcopy(state)
        sim_player = sim_state.player_by_name(player.name)
        sim_card = self._find_card(sim_state, sim_player, action)
        if not sim_card:
            return None, float("-inf")

        sim_state.log = lambda msg: None
        recorder = RecordingStrategy()
        strats = {p.name: RecordingStrategy() for p in sim_state.players}
        strats[sim_player.name] = recorder

        from engine import GameEngine
        sim_engine = GameEngine(sim_state, strats, observers=[])

        try:
            beh = sim_engine.behavior(sim_card)
            ctx = sim_engine.make_ctx(sim_player, sim_card)
            beh.on_order(ctx)
        except Exception:
            return None, float("-inf")

        leaf_score = evaluate(sim_state, sim_player, self.evaluators)

        # No branching needed if no multi-option decisions were made
        if not recorder.decisions:
            return [], leaf_score

        # Return option counts, capped
        points = [
            min(len(opts), self.MAX_OPTIONS_PER_DECISION)
            for opts, _ in recorder.decisions[:self.MAX_DECISIONS]
        ]
        return points, leaf_score



    def _generate_combos(self, decision_points: list[int]) -> list[list[int]]:
        """Generate all index combinations across decision points."""
        if not decision_points:
            return [[]]
        combos = [[]]
        for n_opts in decision_points:
            combos = [c + [i] for c in combos for i in range(n_opts)]
        return combos

    def _run_with_choices(self, state: GameState, player: Player,
                          action: Action, choices: list[int]) -> float:
        """Run action on a deepcopy with predetermined choices, return leaf score."""
        sim_state = copy.deepcopy(state)
        sim_player = sim_state.player_by_name(player.name)
        sim_card = self._find_card(sim_state, sim_player, action)
        if not sim_card:
            return float("-inf")

        sim_state.log = lambda msg: None
        # Active player uses scripted choices; others use default (first option)
        strats = {p.name: ScriptedStrategy([]) for p in sim_state.players}
        strats[sim_player.name] = ScriptedStrategy(choices)

        from engine import GameEngine
        sim_engine = GameEngine(sim_state, strats, observers=[])

        snap = (len(sim_player.domain), len(sim_player.discard))

        try:
            beh = sim_engine.behavior(sim_card)
            ctx = sim_engine.make_ctx(sim_player, sim_card)
            beh.on_order(ctx)
        except Exception:
            return float("-inf")

        # No-op: penalize slightly
        if (len(sim_player.domain), len(sim_player.discard)) == snap:
            return evaluate(sim_state, sim_player, self.evaluators) - 0.5

        return evaluate(sim_state, sim_player, self.evaluators)

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
