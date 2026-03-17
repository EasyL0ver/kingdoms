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


# ── Simulation sub-decision strategy ─────────────────────────────────

class SimStrategy(Strategy):
    """Evaluator-aware strategy for sub-decisions during simulation.

    At each decision point, temporarily applies each option to the state,
    evaluates using the full evaluator suite, and picks the best.
    This gives real branching at every sub-decision without nested deepcopy.
    """

    name = "sim"

    def __init__(self, rng: random.Random | None = None,
                 evaluators: list[Evaluator] | None = None):
        self.rng = rng or random.Random()
        self.evaluators = evaluators

    def resolve(self, state, player, options, ctx):
        if not options:
            return None
        if len(options) == 1:
            return options[0]

        match ctx.intent:
            case Intent.GAIN:
                if hasattr(options[0], "tags"):
                    return self._best_card_to_gain(state, player, options)
            case Intent.DISCARD:
                if hasattr(options[0], "tags"):
                    return self._best_card_to_discard(state, player, options)
            case Intent.GIVE_AWAY:
                if hasattr(options[0], "tags"):
                    return self._best_card_to_give(state, player, options)
            case Intent.TARGET:
                if hasattr(options[0], "domain"):
                    return self._best_target(state, player, options)
            case Intent.OPTION:
                if options == [True, False]:
                    return True
        return options[0]

    def _best_card_to_gain(self, state, player, cards):
        """Try adding each card, evaluate, pick best."""
        best, best_score = cards[0], float("-inf")
        for card in cards:
            player.domain.append(card)
            score = evaluate(state, player, self.evaluators)
            player.domain.pop()
            if score > best_score:
                best_score = score
                best = card
        return best

    def _best_card_to_discard(self, state, player, cards):
        """Try removing each card, evaluate, keep best remaining state."""
        best, best_score = cards[0], float("-inf")
        for card in cards:
            if card in player.domain:
                player.domain.remove(card)
                player.discard.append(card)
                score = evaluate(state, player, self.evaluators)
                player.discard.pop()
                player.domain.append(card)
            else:
                score = evaluate(state, player, self.evaluators)
            if score > best_score:
                best_score = score
                best = card
        return best

    def _best_card_to_give(self, state, player, cards):
        """Give away the card whose absence hurts least."""
        return self._best_card_to_discard(state, player, cards)

    def _best_target(self, state, player, targets):
        """Target the opponent with the strongest position (disrupt the leader)."""
        return max(targets, key=lambda p: evaluate(state, p, self.evaluators))

    def sequence(self, state, player, items, ctx):
        return list(items)

    def resolve_n(self, state, player, options, min_n, max_n, ctx):
        """Pick N items one at a time using evaluate."""
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
    """Depth-1 lookahead: simulate each Order action, pick the best outcome.

    Top-level Order selection uses tree search.
    All sub-decisions (during both simulation and real execution) use greedy.
    Evaluators are composable — pass a list to control what the AI values.
    """

    name = "tree_search"

    def __init__(self, rng: random.Random | None = None,
                 evaluators: list[Evaluator] | None = None):
        self.rng = rng or random.Random()
        self._sim_strategy = SimStrategy(self.rng, evaluators)
        self.evaluators = evaluators

    def resolve(self, state, player, options, ctx):
        if ctx.event == "Dawn" and ctx.source == "Presence":
            return self._search(state, player, options)
        return self._sim_strategy.resolve(state, player, options, ctx)

    def sequence(self, state, player, items, ctx):
        return self._sim_strategy.sequence(state, player, items, ctx)

    def resolve_n(self, state, player, options, min_n, max_n, ctx):
        return self._sim_strategy.resolve_n(state, player, options, min_n, max_n, ctx)

    # ── Core search ──

    def _search(self, state: GameState, player: Player, actions: list[Action]) -> Action:
        best_action = None
        best_score = float("-inf")

        for action in actions:
            score = self._simulate(state, player, action)
            if score > best_score:
                best_score = score
                best_action = action

        # If best is no better than current, pick randomly to avoid loops
        baseline = evaluate(state, player, self.evaluators)
        if best_score <= baseline:
            return self.rng.choice(actions)

        return best_action or actions[0]

    def _simulate(self, state: GameState, player: Player, action: Action) -> float:
        if action.type == "pass":
            return evaluate(state, player, self.evaluators)

        sim_state = copy.deepcopy(state)
        sim_player = sim_state.player_by_name(player.name)
        sim_card = self._find_card(sim_state, sim_player, action)

        if not sim_card:
            return float("-inf")

        # Silence logging
        sim_state.log = lambda msg: None

        sim_strats = {p.name: SimStrategy(random.Random(42), self.evaluators)
                      for p in sim_state.players}

        from engine import GameEngine
        sim_engine = GameEngine(sim_state, sim_strats, observers=[])

        try:
            beh = sim_engine.behavior(sim_card)
            ctx = sim_engine.make_ctx(sim_player, sim_card)
            beh.on_order(ctx)
        except Exception:
            return float("-inf")

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
