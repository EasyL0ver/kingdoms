"""Kingdoms — Python Simulation CLI.

Usage:
    python sim.py                     # Single game, 3 players, random strategy
    python sim.py -n 100              # 100 games, print summary stats
    python sim.py --players 4 --seed 42
    python sim.py -n 10 --strategy tree_search:2
    python sim.py -n 10 --strategy tree_search:3 --evaluator tag_value+pile_proximity
    python sim.py --list-strategies   # Show available strategies
    python sim.py --list-evaluators   # Show available evaluators
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Allow running from simulation/ directory
sys.path.insert(0, str(Path(__file__).parent))

from state import GameState
from engine import GameEngine
from strategy import RandomStrategy
from tree_search import TreeSearchStrategy, get_evaluator, list_evaluators
from observers import CardWinCorrelation, OrderStats, EventFrequency, StrategyWinRate, GameLength

STRATEGIES = {
    "random": ("Uniformly random choices", lambda rng, evals: RandomStrategy(rng)),
    "tree_search": ("Naive decision tree — plays best path each Dawn",
                    lambda rng, evals: TreeSearchStrategy(rng)),
}


def _build_strategies(names: list[str], strategy_specs: list[str] | None,
                      rng, evaluator_names: list[str] | None = None) -> dict:
    """Build per-player strategy dict from --strategy specs.

    Each spec is 'name:count', e.g. 'tree_search:2' means 2 players get it.
    Players are assigned in order; remaining get RandomStrategy.
    """
    evaluators = None
    if evaluator_names:
        evaluators = [get_evaluator(n) for n in evaluator_names]

    if not strategy_specs:
        return {n: RandomStrategy(rng) for n in names}

    assignments: list[tuple[str, int]] = []
    for spec in strategy_specs:
        if ":" in spec:
            sname, count_str = spec.rsplit(":", 1)
            assignments.append((sname.strip(), int(count_str)))
        else:
            assignments.append((spec.strip(), 1))

    strategies: dict = {}
    idx = 0
    for sname, count in assignments:
        if sname not in STRATEGIES:
            raise ValueError(f"Unknown strategy '{sname}'. Available: {list(STRATEGIES)}")
        factory = STRATEGIES[sname][1]
        for _ in range(count):
            if idx >= len(names):
                break
            strategies[names[idx]] = factory(rng, evaluators)
            idx += 1

    for i in range(idx, len(names)):
        strategies[names[i]] = RandomStrategy(rng)

    return strategies


def run_single_game(players: int, max_turns: int, seed: int | None,
                    verbose: bool = True, observers: list | None = None,
                    strategy_specs: list[str] | None = None,
                    evaluator_names: list[str] | None = None) -> dict:
    """Run one game. Returns result dict."""
    names = ["Alice", "Bob", "Charlie", "Dave", "Eve"][:players]
    state = GameState(names, seed=seed)
    state.load_decks(Path(__file__).parent / "decks.json")
    state.setup_zones()

    rng_strategy = state.rng
    strategies = _build_strategies(names, strategy_specs, rng_strategy, evaluator_names)
    engine = GameEngine(state, strategies, observers=observers)

    t0 = time.perf_counter()
    depleted = engine.run_game(max_turns)
    elapsed = time.perf_counter() - t0

    winner = engine._compute_winner()

    result = {
        "depleted": depleted,
        "turns": state.turn_num,
        "winner": winner,
        "elapsed": elapsed,
        "log": state.get_log(),
    }

    if verbose:
        print(state.get_log())

    return result


def _collect_benchmark(args, stats, observers, eval_names) -> dict:
    """Collect structured benchmark data from a batch run."""
    card_obs = next((o for o in observers if isinstance(o, CardWinCorrelation)), None)
    order_obs = next((o for o in observers if isinstance(o, OrderStats)), None)
    strat_obs = next((o for o in observers if isinstance(o, StrategyWinRate)), None)
    event_obs = next((o for o in observers if isinstance(o, EventFrequency)), None)

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "games": args.games,
            "players": args.players,
            "max_turns": args.turns,
            "seed": args.seed,
            "strategies": args.strategies or [],
            "evaluators": eval_names,
        },
        "summary": {
            "avg_turns": sum(stats["turns"]) / len(stats["turns"]),
            "avg_time": sum(stats["elapsed"]) / len(stats["elapsed"]),
            "total_time": sum(stats["elapsed"]),
            "pile_depletion": stats["depleted"],
            "winners": stats["wins"],
        },
    }

    if card_obs and card_obs.total_winners > 0:
        base_rate = card_obs.total_winners / (card_obs.total_winners + card_obs.total_losers)
        cards = {}
        for name in card_obs.card_in_any:
            iw = card_obs.card_in_winner.get(name, 0)
            il = card_obs.card_in_loser.get(name, 0)
            total = card_obs.card_in_any[name]
            wr = iw / total if total > 0 else 0
            cards[name] = {"win_rate": round(wr, 3), "in_win": iw, "in_lose": il,
                           "lift": round(wr - base_rate, 3), "games": total}
        data["card_winrates"] = cards

    if order_obs:
        orders = {}
        for name, count in order_obs.orders.items():
            iw = order_obs.orders_in_wins.get(name, 0)
            orders[name] = {"total": count,
                            "per_game": round(count / order_obs.total_games, 2),
                            "in_wins": iw,
                            "win_share": round(iw / count, 3) if count else 0}
        data["order_stats"] = orders

    if strat_obs:
        strats = {}
        for label in strat_obs.games:
            w = strat_obs.wins.get(label, 0)
            l = strat_obs.losses.get(label, 0)
            t = strat_obs.ties.get(label, 0)
            decisive = w + l
            strats[label] = {"wins": w, "losses": l, "ties": t,
                             "win_rate": round(w / decisive, 3) if decisive else 0,
                             "decisive": decisive}
        # Per win-condition breakdown
        by_condition = {}
        for (label, cond), g in strat_obs.games_by_condition.items():
            if cond == "none":
                continue
            w = strat_obs.wins_by_condition.get((label, cond), 0)
            by_condition.setdefault(cond, {})[label] = {
                "wins": w, "games": g,
                "win_rate": round(w / g, 3) if g else 0}
        strats["by_win_condition"] = by_condition
        data["strategy_winrates"] = strats

    if event_obs:
        events = {}
        for event, count in event_obs.event_count.items():
            cancelled = event_obs.event_cancelled.get(event, 0)
            resp = event_obs.event_responders.get(event, 0)
            events[event] = {"total": count,
                             "per_game": round(count / event_obs.total_games, 1),
                             "cancelled": cancelled,
                             "cancel_rate": round(cancelled / count, 3) if count else 0,
                             "avg_responders": round(resp / count, 2) if count else 0}
        data["events"] = events

    length_obs = next((o for o in observers if isinstance(o, GameLength)), None)
    if length_obs:
        data["game_length"] = length_obs.to_dict()

    return data


def _save_benchmark(data: dict, bench_dir: str | None):
    """Save benchmark data to a JSON file in the benchmarks directory."""
    d = Path(bench_dir) if bench_dir else Path(__file__).parent / "benchmarks"
    d.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    strats = "_".join(data["config"]["strategies"]) if data["config"]["strategies"] else "random"
    strats = strats.replace(":", "")
    filename = f"{ts}_{data['config']['games']}g_{strats}.json"
    path = d / filename
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"\nBenchmark saved to {path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Kingdoms simulation")
    parser.add_argument("-n", "--games", type=int, default=1, help="Number of games to run")
    parser.add_argument("--players", type=int, default=3, help="Number of players (2-5)")
    parser.add_argument("--turns", type=int, default=200, help="Max turns per game")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed (for reproducibility)")
    parser.add_argument("--out", type=str, default=None, help="Output file for log (single game only)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress per-game output")
    parser.add_argument("--strategy", action="append", dest="strategies",
                        metavar="NAME:COUNT",
                        help="Assign strategy to N players (e.g. tree_search:2). Repeatable.")
    parser.add_argument("--evaluator", type=str, dest="evaluators", default=None,
                        metavar="NAME+NAME",
                        help="Evaluators for tree_search (e.g. tag_value+pile_proximity). Default: all.")
    parser.add_argument("--list-strategies", action="store_true",
                        help="Show available strategies and exit")
    parser.add_argument("--list-evaluators", action="store_true",
                        help="Show available evaluators and exit")
    parser.add_argument("--bench-dir", type=str, default=None,
                        metavar="DIR",
                        help="Save benchmark output to timestamped file in DIR (default: simulation/benchmarks)")
    args = parser.parse_args()

    if args.list_strategies:
        print("Available strategies:")
        for name, (desc, _) in STRATEGIES.items():
            print(f"  {name:20s} — {desc}")
        return

    if args.list_evaluators:
        print("Available evaluators:")
        for name in list_evaluators():
            e = get_evaluator(name)
            doc = e.__class__.__doc__ or ""
            print(f"  {name:20s} — {doc.strip().splitlines()[0]}")
        return

    eval_names = args.evaluators.split("+") if args.evaluators else None

    if args.games == 1:
        result = run_single_game(args.players, args.turns, args.seed,
                                  verbose=not args.quiet,
                                  strategy_specs=args.strategies,
                                  evaluator_names=eval_names)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(result["log"], encoding="utf-8")
            print(f"\nLog written to {args.out}", file=sys.stderr)
        if args.quiet:
            print(f"Result: {result['depleted']} depleted, {result['turns']} turns, "
                  f"winner: {result['winner']}, {result['elapsed']:.3f}s")
    else:
        # Batch mode with observers
        observers = [CardWinCorrelation(), OrderStats(), EventFrequency(),
                     StrategyWinRate(), GameLength()]
        stats = {"wins": {}, "depleted": {}, "turns": [], "elapsed": []}

        for i in range(args.games):
            seed = (args.seed + i) if args.seed is not None else None
            result = run_single_game(args.players, args.turns, seed,
                                     verbose=False, observers=observers,
                                     strategy_specs=args.strategies,
                                     evaluator_names=eval_names)
            stats["turns"].append(result["turns"])
            stats["elapsed"].append(result["elapsed"])
            d = result["depleted"] or "none"
            stats["depleted"][d] = stats["depleted"].get(d, 0) + 1
            w = result["winner"] or "none"
            stats["wins"][w] = stats["wins"].get(w, 0) + 1
            if (i + 1) % 100 == 0 or (i + 1) == args.games:
                print(f"\r  {i+1}/{args.games} games...", end="", file=sys.stderr, flush=True)
        print("", file=sys.stderr)

        # Print summary
        print(f"\n{'='*50}")
        print(f"BATCH RESULTS: {args.games} games, {args.players} players, max {args.turns} turns")
        if args.strategies:
            print(f"Strategies: {', '.join(args.strategies)}")
            names = ["Alice", "Bob", "Charlie", "Dave", "Eve"][:args.players]
            sample_strats = _build_strategies(names, args.strategies, None, eval_names)
            for name in names:
                s = sample_strats[name]
                print(f"  {name}: {getattr(s, 'name', 'unknown')}")
        print(f"{'='*50}")
        print(f"\nPile depletion frequency:")
        for pile, count in sorted(stats["depleted"].items(), key=lambda x: -x[1]):
            print(f"  {pile}: {count} ({100*count/args.games:.1f}%)")
        print(f"\nWinner frequency:")
        for name, count in sorted(stats["wins"].items(), key=lambda x: -x[1]):
            print(f"  {name}: {count} ({100*count/args.games:.1f}%)")
        avg_turns = sum(stats["turns"]) / len(stats["turns"])
        avg_time = sum(stats["elapsed"]) / len(stats["elapsed"])
        print(f"\nAvg turns: {avg_turns:.1f} | Avg time: {avg_time:.3f}s | "
              f"Total: {sum(stats['elapsed']):.1f}s")

        # Observer reports
        for obs in observers:
            print(f"\n{obs.report()}")

        # Save benchmark data
        bench = _collect_benchmark(args, stats, observers, eval_names)
        _save_benchmark(bench, args.bench_dir)


if __name__ == "__main__":
    main()
