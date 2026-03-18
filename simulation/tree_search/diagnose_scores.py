"""Diagnose: how much score spread does the tree see between options?"""
import sys, time, random
sys.path.insert(0, ".")

from state import GameState
from engine import GameEngine
from strategy import RandomStrategy
from tree_search.tree import TreeSearchStrategy, build_tree, best_path, print_tree
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

for t in range(1, 50):
    if state.game_over:
        break
    state.turn_num = t
    p_idx = (t - 1) % 3
    player = state.players[p_idx]
    if p_idx == 0:
        state.round_num += 1

    if player.name == "Alice":
        # Build tree and inspect scores
        opp_strats = {p.name: RandomStrategy(rng) for p in state.players}
        root, stats = build_tree(state, player, GameEngine, opp_strats,
                                 time_budget=4.0, rng=rng)
        score, path = best_path(root)

        # Collect all leaf scores
        def collect_scores(node):
            from tree_search.tree import LeafNode, TreeNode
            if isinstance(node, LeafNode):
                return [node.score]
            scores = []
            for child in node.children.values():
                scores.extend(collect_scores(child))
            return scores

        from tree_search.tree import TreeNode
        scores = collect_scores(root)
        if scores:
            spread = max(scores) - min(scores)
            print(f"T{t:3d} domain={len(player.domain):2d}  "
                  f"nodes={stats['nodes']:3d} leaves={stats['leaves']:3d}  "
                  f"best={max(scores):.1f} worst={min(scores):.1f} spread={spread:.1f}  "
                  f"avg={sum(scores)/len(scores):.1f}")

    eng.resolve_turn(player)
    depleted = state.check_game_end()
    if depleted:
        state.game_over = True
        break
