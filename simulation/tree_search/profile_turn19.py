"""Profile tree build at turn 19."""
import sys, time, random, copy
sys.path.insert(0, ".")
from state import GameState
from engine import GameEngine
from strategy import RandomStrategy
from tree_search.tree import TreeSearchStrategy, build_tree

names = ["Alice", "Bob", "Charlie"]
s = GameState(names, seed=42)
s.load_decks("decks.json")
s.setup_zones()
rng = s.rng
strats_game = {n: RandomStrategy(rng) for n in names}
strats_game["Alice"] = TreeSearchStrategy(rng)
eng = GameEngine(s, strats_game, observers=[])
for t in range(1, 19):
    s.turn_num = t
    p_idx = (t - 1) % 3
    player = s.players[p_idx]
    if p_idx == 0:
        s.round_num += 1
    eng.resolve_turn(player)

alice = s.players[0]
print(f"Alice domain: {len(alice.domain)} cards, turn {s.turn_num}")
strats_tree = {p.name: RandomStrategy(random.Random(42)) for p in s.players}
t0 = time.perf_counter()
root, stats = build_tree(s, alice, GameEngine, strats_tree)
dt = time.perf_counter() - t0
leaves = max(stats["leaves"], 1)
print(f"Stats: {stats}")
print(f"Time: {dt:.1f}s")
print(f"ms per leaf: {dt*1000/leaves:.1f}")
