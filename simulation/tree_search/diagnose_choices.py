"""Diagnose: what does the tree pick and how much does it explore?"""
import sys, time, random
sys.path.insert(0, ".")

from state import GameState
from engine import GameEngine
from strategy import RandomStrategy
from tree_search.tree import TreeSearchStrategy, build_tree, best_path, TreeNode, LeafNode
from pathlib import Path

seed = 42
names = ["Alice", "Bob", "Charlie"]
state = GameState(names, seed=seed)
state.load_decks(Path(__file__).parent.parent / "decks.json")
state.setup_zones()

rng = state.rng
ts = TreeSearchStrategy(rng, time_budget=4.0)
strats = {"Alice": ts, "Bob": RandomStrategy(rng), "Charlie": RandomStrategy(rng)}
eng = GameEngine(state, strats, observers=[])

for t in range(1, 40):
    if state.game_over:
        break
    state.turn_num = t
    p_idx = (t - 1) % 3
    player = state.players[p_idx]
    if p_idx == 0:
        state.round_num += 1

    if player.name == "Alice":
        opp_strats = {p.name: RandomStrategy(rng) for p in state.players}
        root, stats = build_tree(state, player, GameEngine, opp_strats,
                                 time_budget=4.0, rng=rng)
        score, path = best_path(root)

        # Show top-level options and whether they were explored
        if isinstance(root, TreeNode):
            total_options = len(root.options)
            explored = len(root.children)
            print(f"\nT{t:3d} domain={len(player.domain):2d}  "
                  f"options={total_options} explored={explored}/{total_options}  "
                  f"best_score={score:.1f}")
            for j, label in enumerate(root.options):
                if j in root.children:
                    child = root.children[j]
                    if isinstance(child, LeafNode):
                        print(f"  [{j}] {label:25s} → leaf score={child.score:.1f}")
                    else:
                        # Collect scores under this branch
                        def collect(n):
                            if isinstance(n, LeafNode): return [n.score]
                            s = []
                            for c in n.children.values(): s.extend(collect(c))
                            return s
                        scores = collect(child)
                        best_s = max(scores) if scores else 0
                        print(f"  [{j}] {label:25s} → {len(scores)} leaves, "
                              f"best={best_s:.1f} avg={sum(scores)/len(scores):.1f}")
                else:
                    marker = " ← TIME CUT" 
                    print(f"  [{j}] {label:25s} → NOT EXPLORED{marker}")
            chosen = path[0] if path else "?"
            chosen_label = root.options[chosen] if isinstance(chosen, int) and chosen < len(root.options) else "?"
            print(f"  CHOSE: [{chosen}] {chosen_label}")

    eng.resolve_turn(player)
    depleted = state.check_game_end()
    if depleted:
        state.game_over = True
        break
