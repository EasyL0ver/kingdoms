"""Experiment: Does event_payoff heuristic reduce wasted turns?

After removing can_order, all cards with on_order appear in the action list
regardless of whether preconditions are met. Random play wastes turns on
fizzle actions. The event_payoff heuristic now scores Order actions by their
card hints — cards with known effects score high, unknowns get penalised.

This experiment compares turn counts and win rates across:
  1. Pure random (baseline)
  2. event_payoff only
  3. event_payoff + synergy
  4. event_payoff + play_to_win
  5. All heuristics combined
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sim import run_single_game
from observers import CardWinCorrelation, OrderStats, EventFrequency, HeuristicWinRate

GAMES = 1000
SEED = 42
PLAYERS = 3

CONFIGS = [
    ("random", None),
    ("event_payoff", ["event_payoff:3"]),
    ("event_payoff+synergy", ["event_payoff+synergy:3"]),
    ("event_payoff+play_to_win", ["event_payoff+play_to_win:3"]),
    ("all_combined", ["event_payoff+synergy+play_to_win+aggressive:3"]),
]


def run_config(label, heuristic_specs):
    stats = {"turns": [], "elapsed": [], "depleted": {}, "wins": {}}
    for i in range(GAMES):
        seed = SEED + i
        result = run_single_game(PLAYERS, 200, seed,
                                  verbose=False,
                                  heuristic_specs=heuristic_specs)
        stats["turns"].append(result["turns"])
        stats["elapsed"].append(result["elapsed"])
        d = result["depleted"] or "none"
        stats["depleted"][d] = stats["depleted"].get(d, 0) + 1
        w = result["winner"] or "none"
        stats["wins"][w] = stats["wins"].get(w, 0) + 1
    return stats


def main():
    print(f"{'Config':<30} {'AvgTurns':>9} {'Claw%':>7} {'Tree%':>7} "
          f"{'Time/game':>10} {'MaxTurns':>9}")
    print("-" * 80)

    for label, specs in CONFIGS:
        print(f"  Running {label}...", end="", flush=True, file=sys.stderr)
        stats = run_config(label, specs)
        avg_turns = sum(stats["turns"]) / len(stats["turns"])
        max_turns = max(stats["turns"])
        avg_time = sum(stats["elapsed"]) / len(stats["elapsed"])
        claw_pct = 100 * stats["depleted"].get("claw", 0) / GAMES
        tree_pct = 100 * stats["depleted"].get("tree", 0) / GAMES
        print(f"\r{label:<30} {avg_turns:>9.1f} {claw_pct:>6.1f}% {tree_pct:>6.1f}% "
              f"{avg_time:>9.4f}s {max_turns:>9}")

    print("\nDone.")


if __name__ == "__main__":
    main()
