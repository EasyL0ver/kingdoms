"""Quick smoke test: 1 game, tree_search for Alice, random for others."""
import sys, time
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from state import GameState
from engine import GameEngine
from strategy import RandomStrategy
from tree_search.tree import TreeSearchStrategy
from pathlib import Path

seed = 42
names = ["Alice", "Bob", "Charlie"]
state = GameState(names, seed=seed)
state.load_decks(Path(__file__).parent.parent / "decks.json")
state.setup_zones()

rng = state.rng
strategies = {
    "Alice": TreeSearchStrategy(rng, time_budget=2.0),
    "Bob": RandomStrategy(rng),
    "Charlie": RandomStrategy(rng),
}
engine = GameEngine(state, strategies, observers=[])

# Manual game loop with per-turn timing
max_turns = 200
t0_total = time.perf_counter()
for t in range(1, max_turns + 1):
    if state.game_over:
        break
    state.turn_num = t
    p_idx = (t - 1) % len(state.players)
    player = state.players[p_idx]
    if p_idx == 0:
        state.round_num += 1

    t0 = time.perf_counter()
    engine.resolve_turn(player)
    dt = time.perf_counter() - t0

    who = "TREE" if player.name == "Alice" else "rand"
    domain_sizes = ", ".join(f"{p.name}:{len(p.domain)}" for p in state.players)
    print(f"T{t:3d} [{who}] {player.name:8s} {dt:6.2f}s  domains: {domain_sizes}", flush=True)

    depleted = state.check_game_end()
    if depleted:
        state.game_over = True
        state.depleted_pile = depleted
        print(f"\n=== GAME OVER: {depleted} depleted at turn {t} ===")
        break

elapsed = time.perf_counter() - t0_total
winner = engine._compute_winner()
print(f"\nWinner: {winner}  Turns: {state.turn_num}  Total: {elapsed:.1f}s")
