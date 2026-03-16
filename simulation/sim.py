"""Kingdoms — Python Simulation CLI.

Usage:
    python sim.py                     # Single game, 3 players, random strategy
    python sim.py -n 100              # 100 games, print summary stats
    python sim.py --players 4 --seed 42
    python sim.py -n 50 --turns 200 --out logs/batch.md
    python sim.py -n 1000 --heuristic prefer_trophies:2 --heuristic aggressive:1
    python sim.py --list-heuristics   # Show available heuristics
"""
import argparse
import sys
import time
from pathlib import Path

# Allow running from simulation/ directory
sys.path.insert(0, str(Path(__file__).parent))

from state import GameState
from engine import GameEngine
from strategy import RandomStrategy
from observers import CardWinCorrelation, ActivationStats, EventFrequency, HeuristicWinRate
from heuristics import HeuristicStrategy, get_heuristic, list_heuristics


def _build_strategies(names: list[str], heuristic_specs: list[str] | None,
                      rng) -> dict:
    """Build per-player strategy dict from --heuristic specs.

    Each spec is 'name:count', e.g. 'aggressive:2' means 2 players get it.
    Players are assigned in order; remaining get pure RandomStrategy.
    """
    if not heuristic_specs:
        return {n: RandomStrategy(rng) for n in names}

    # Parse specs: [("aggressive", 2), ("prefer_trophies", 1), ...]
    assignments: list[tuple[str, int]] = []
    for spec in heuristic_specs:
        if ":" in spec:
            hname, count_str = spec.rsplit(":", 1)
            assignments.append((hname.strip(), int(count_str)))
        else:
            assignments.append((spec.strip(), 1))

    # Assign heuristics to players in order
    strategies: dict = {}
    name_idx = 0
    for hname, count in assignments:
        heuristic = get_heuristic(hname)
        for _ in range(count):
            if name_idx >= len(names):
                break
            player_name = names[name_idx]
            # Check if player already has a strategy (multiple heuristics)
            if player_name in strategies:
                existing = strategies[player_name]
                existing.heuristics.append(get_heuristic(hname))
            else:
                strategies[player_name] = HeuristicStrategy(
                    [get_heuristic(hname)], rng)
            name_idx += 1

    # Remaining players get pure random
    for i in range(name_idx, len(names)):
        strategies[names[i]] = RandomStrategy(rng)

    return strategies


def run_single_game(players: int, max_turns: int, seed: int | None,
                    verbose: bool = True, observers: list | None = None,
                    heuristic_specs: list[str] | None = None) -> dict:
    """Run one game. Returns result dict."""
    names = ["Alice", "Bob", "Charlie", "Dave", "Eve"][:players]
    state = GameState(names, seed=seed)
    state.load_decks(Path(__file__).parent / "decks.json")
    state.setup_zones()

    rng_strategy = state.rng  # share RNG for reproducibility
    strategies = _build_strategies(names, heuristic_specs, rng_strategy)
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


def main():
    parser = argparse.ArgumentParser(description="Kingdoms simulation (no AI)")
    parser.add_argument("-n", "--games", type=int, default=1, help="Number of games to run")
    parser.add_argument("--players", type=int, default=3, help="Number of players (2-5)")
    parser.add_argument("--turns", type=int, default=200, help="Max turns per game")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed (for reproducibility)")
    parser.add_argument("--out", type=str, default=None, help="Output file for log (single game only)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress per-game output")
    parser.add_argument("--heuristic", action="append", dest="heuristics",
                        metavar="NAME:COUNT",
                        help="Assign heuristic to N players (e.g. aggressive:2). Repeatable.")
    parser.add_argument("--list-heuristics", action="store_true",
                        help="Show available heuristics and exit")
    args = parser.parse_args()

    if args.list_heuristics:
        print("Available heuristics:")
        for name in list_heuristics():
            h = get_heuristic(name)
            doc = h.__class__.__doc__ or ""
            print(f"  {name:20s} — {doc.strip().splitlines()[0]}")
        return

    if args.games == 1:
        result = run_single_game(args.players, args.turns, args.seed,
                                  verbose=not args.quiet,
                                  heuristic_specs=args.heuristics)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(result["log"], encoding="utf-8")
            print(f"\nLog written to {args.out}", file=sys.stderr)
        if args.quiet:
            print(f"Result: {result['depleted']} depleted, {result['turns']} turns, "
                  f"winner: {result['winner']}, {result['elapsed']:.3f}s")
    else:
        # Batch mode with observers
        observers = [CardWinCorrelation(), ActivationStats(), EventFrequency(),
                     HeuristicWinRate()]
        stats = {"wins": {}, "depleted": {}, "turns": [], "elapsed": []}

        for i in range(args.games):
            seed = (args.seed + i) if args.seed is not None else None
            result = run_single_game(args.players, args.turns, seed,
                                     verbose=False, observers=observers,
                                     heuristic_specs=args.heuristics)
            stats["turns"].append(result["turns"])
            stats["elapsed"].append(result["elapsed"])
            d = result["depleted"] or "none"
            stats["depleted"][d] = stats["depleted"].get(d, 0) + 1
            w = result["winner"] or "none"
            stats["wins"][w] = stats["wins"].get(w, 0) + 1
            if (i + 1) % 1000 == 0 or (i + 1) == args.games:
                print(f"\r  {i+1}/{args.games} games...", end="", file=sys.stderr, flush=True)
        print("", file=sys.stderr)  # newline after progress

        # Print summary
        print(f"\n{'='*50}")
        print(f"BATCH RESULTS: {args.games} games, {args.players} players, max {args.turns} turns")
        if args.heuristics:
            print(f"Heuristics: {', '.join(args.heuristics)}")
            # Show per-player assignments
            names = ["Alice", "Bob", "Charlie", "Dave", "Eve"][:args.players]
            sample_strats = _build_strategies(names, args.heuristics, None)
            for name in names:
                s = sample_strats[name]
                if isinstance(s, HeuristicStrategy):
                    h_names = [h.name for h in s.heuristics]
                    print(f"  {name}: {', '.join(h_names)}")
                else:
                    print(f"  {name}: random")
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


if __name__ == "__main__":
    main()
