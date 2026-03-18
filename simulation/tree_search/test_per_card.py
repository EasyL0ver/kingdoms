"""Per-card tree size test.

For each orderable card, put Presence + that card in domain,
build the tree, report nodes/leaves/time.
"""
import sys, time, random
sys.path.insert(0, ".")

from state import GameState, Card
from engine import GameEngine
from strategy import RandomStrategy
from tree_search.tree import build_tree

ORDERABLE = [
    ("Warband", ["Discontent"], "claw"),
    ("Blood Offering", [], "claw"),
    ("Poach", ["Unit", "Mob", "Hunt", "Discontent"], "claw"),
    ("Racketeering", ["Discontent"], "claw"),
    ("Tyranny", ["Trophy", "Discontent"], "claw"),
    ("Outriders", [], "claw"),
    ("Land Grab", ["Discontent"], "claw"),
    ("Ransack", [], "claw"),
    ("Ivory", ["Trophy", "Wealth"], "claw"),
    ("Martial Excellence", ["Trophy", "Chivalry"], "claw"),
    ("Dusk Rite", ["Spiritual", "Discontent"], "claw"),
    ("Sky Dance", ["Spiritual"], "tree"),
    ("Sacred Grove", ["Nature", "Spiritual"], "tree"),
    ("Floods", ["Nature"], "tree"),
    ("Forage", [], "tree"),
    ("Sowing", ["Knowledge"], "tree"),
    ("Withered Crop", [], "tree"),
    ("Remembrance", ["Knowledge"], "tree"),
    ("Pilgrimage", ["Spiritual"], "tree"),
    ("Plough", ["Labour"], "wheat"),
    ("Granary", ["Labour"], "wheat"),
    ("Mill", ["Labour"], "wheat"),
    ("Animal Husbandry", ["Labour"], "wheat"),
    ("Apprenticeship", ["Labour"], "wheat"),
    ("Militia", ["Unit"], "wheat"),
    ("Well", ["Amenity"], "wheat"),
    ("Orchard", ["Nature", "Land"], "wheat"),
    ("Market", [], "coin"),
    ("Swindle", [], "coin"),
    ("Efficiency", [], "coin"),
    ("Spice Market", ["Wealth"], "coin"),
    ("Mine", ["Labour"], "coin"),
    ("Ornament", ["Religion"], "candle"),
    ("Clergy", ["Religion"], "candle"),
    ("Evangelism", ["Religion"], "candle"),
    ("Purity", ["Religion"], "candle"),
    ("Benefaction", ["Religion"], "candle"),
    ("Royal Hunt", ["Unit", "Trophy", "Hunt"], "sword"),
]


def test_card(name, tags, deck):
    s = GameState(["A", "B", "C"], seed=42)
    s.load_decks("decks.json")
    s.setup_zones()

    player = s.players[0]
    # Presence + one card
    player.domain = [player.domain_card, Card(name=name, tags=tags, deck=deck)]

    # Give opponents some cards so brawl/target have targets
    opp = s.players[1]
    opp.domain.append(Card(name="Sowing", tags=["Knowledge"], deck="tree"))
    opp.domain.append(Card(name="Kinship", tags=["Nature", "Knowledge"], deck="tree"))

    # Put something in discard for cards that care
    player.discard.append(Card(name="Raid", tags=["Trophy"], deck="claw"))

    strats = {p.name: RandomStrategy(random.Random(42)) for p in s.players}
    t0 = time.perf_counter()
    root, stats = build_tree(s, player, GameEngine, strats)
    dt = time.perf_counter() - t0
    return stats, dt


print(f"{'Card':<25s} {'Nodes':>5s} {'Leaves':>6s} {'Depth':>5s} {'Time':>8s}")
print("-" * 55)
results = []
for name, tags, deck in ORDERABLE:
    stats, dt = test_card(name, tags, deck)
    results.append((name, stats, dt))
    print(f"{name:<25s} {stats['nodes']:>5d} {stats['leaves']:>6d} {stats['max_depth']:>5d} {dt*1000:>7.0f}ms")

print("\n--- Sorted by leaves (descending) ---\n")
results.sort(key=lambda x: -x[1]["leaves"])
for name, stats, dt in results:
    print(f"{name:<25s} {stats['nodes']:>5d} {stats['leaves']:>6d} {stats['max_depth']:>5d} {dt*1000:>7.0f}ms")
