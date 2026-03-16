"""Kingdoms — Python Simulation CLI.

Usage:
    python sim.py                     # Single game, 3 players, random strategy
    python sim.py -n 100              # 100 games, print summary stats
    python sim.py --players 4 --seed 42
    python sim.py -n 50 --turns 200 --out logs/batch.md
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
from observers import CardWinCorrelation, ActivationStats, EventFrequency


def run_single_game(players: int, max_turns: int, seed: int | None,
                    verbose: bool = True, observers: list | None = None) -> dict:
    """Run one game. Returns result dict."""
    names = ["Alice", "Bob", "Charlie", "Dave", "Eve"][:players]
    state = GameState(names, seed=seed)
    state.load_decks(Path(__file__).parent / "decks.json")
    state.setup_zones()

    rng_strategy = state.rng  # share RNG for reproducibility
    strategies = {name: RandomStrategy(rng_strategy) for name in names}
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
    args = parser.parse_args()

    if args.games == 1:
        result = run_single_game(args.players, args.turns, args.seed, verbose=not args.quiet)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(result["log"], encoding="utf-8")
            print(f"\nLog written to {args.out}", file=sys.stderr)
        if args.quiet:
            print(f"Result: {result['depleted']} depleted, {result['turns']} turns, "
                  f"winner: {result['winner']}, {result['elapsed']:.3f}s")
    else:
        # Batch mode with observers
        observers = [CardWinCorrelation(), ActivationStats(), EventFrequency()]
        stats = {"wins": {}, "depleted": {}, "turns": [], "elapsed": []}

        for i in range(args.games):
            seed = (args.seed + i) if args.seed is not None else None
            result = run_single_game(args.players, args.turns, seed,
                                     verbose=False, observers=observers)
            stats["turns"].append(result["turns"])
            stats["elapsed"].append(result["elapsed"])
            d = result["depleted"] or "none"
            stats["depleted"][d] = stats["depleted"].get(d, 0) + 1
            w = result["winner"] or "none"
            stats["wins"][w] = stats["wins"].get(w, 0) + 1
            if not args.quiet and (i + 1) % 10 == 0:
                print(f"  {i+1}/{args.games} games...", file=sys.stderr)

        # Print summary
        print(f"\n{'='*50}")
        print(f"BATCH RESULTS: {args.games} games, {args.players} players, max {args.turns} turns")
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
