"""Test naive decision tree building."""
import sys
sys.path.insert(0, ".")

import random
import time
from state import GameState, Card
from engine import GameEngine
from strategy import RandomStrategy
from tree_search.tree import build_tree, print_tree


def _card(name, tags, deck):
    return Card(name=name, tags=tags, deck=deck)


def test_tree_size():
    """Build a tree for turn 1 and a mid-game state, print the sizes."""
    s = GameState(["A", "B", "C"], seed=42)
    s.load_decks("decks.json")
    s.setup_zones()

    player = s.players[0]
    print(f"=== Turn 1: {player.name} ===")
    print(f"Domain: {[c.name for c in player.domain]}")

    opponent_strat = RandomStrategy(random.Random(42))
    strategies = {p.name: opponent_strat for p in s.players}

    root, stats = build_tree(s, player, GameEngine, strategies)
    print(f"Tree stats: {stats}")
    print()
    print_tree(root)


def test_mean_case():
    """Worst-case: cascading events, multiple dawn listeners, lots of decisions."""
    s = GameState(["A", "B", "C"], seed=42)
    s.load_decks("decks.json")
    s.setup_zones()

    player = s.players[0]
    opponent = s.players[1]

    # Clear domain (keep Presence)
    player.domain = [player.domain_card]

    # Dawn listeners: Uprising (self-brawl), Chiefdom (move mobs), Culling (discard)
    player.domain.append(_card("Uprising", ["Discontent"], "claw"))
    player.domain.append(_card("Chiefdom", ["Mob"], "claw"))
    player.domain.append(_card("Culling", ["Mob"], "claw"))

    # Orderable cards that cascade heavily
    player.domain.append(_card("Warband", ["Mob"], "claw"))        # order → brawl
    player.domain.append(_card("Blood Offering", [], "claw"))      # order → sacrifice → rite
    player.domain.append(_card("Racketeering", [], "claw"))        # order → target → steal or brawl
    player.domain.append(_card("Sacred Grove", ["Nature", "Knowledge"], "tree"))  # order → rite or scry
    player.domain.append(_card("Swindle", ["Craftsmanship"], "coin"))  # order → give wares → brawl
    player.domain.append(_card("Forage", [], "tree"))              # order → feast

    # Brawl responders (fire when warband/racketeering/swindle trigger brawl)
    player.domain.append(_card("Zealot", ["Religion"], "candle"))
    player.domain.append(_card("Enforcers", ["Mob"], "claw"))
    player.domain.append(_card("Eldership", ["Knowledge"], "tree"))

    # Rite responders (fire when blood offering/sacred grove trigger rite)
    player.domain.append(_card("Worship of the Relic", ["Spiritual", "Religion"], "candle"))
    player.domain.append(_card("Worship of the Rain", ["Spiritual", "Nature"], "tree"))
    player.domain.append(_card("Worship of Fertility", ["Spiritual", "Nature"], "tree"))

    # Feast responders (fire when forage triggers feast)
    player.domain.append(_card("Hunger", ["Discontent"], "claw"))
    player.domain.append(_card("Tavern", ["Amenity"], "wheat"))
    player.domain.append(_card("Alms", ["Religion", "Spiritual"], "candle"))

    # Stuff in discard for Hunger/Veil Tear
    player.discard.append(_card("Raid", ["Trophy"], "claw"))
    player.discard.append(_card("Harvest", ["Amenity"], "wheat"))

    # Give opponent some cards so brawl/racketeering have targets
    opponent.domain.append(_card("Sowing", ["Nature"], "tree"))
    opponent.domain.append(_card("Kinship", ["Nature", "Knowledge"], "tree"))
    opponent.domain.append(_card("Smuggler", ["Craftsmanship", "Wealth"], "coin"))

    print(f"=== MEAN CASE: {player.name} ===")
    print(f"Domain ({len(player.domain)}): {[c.name for c in player.domain]}")
    print(f"Discard ({len(player.discard)}): {[c.name for c in player.discard]}")
    print(f"Opponent domain: {[c.name for c in opponent.domain]}")
    print()

    opponent_strat = RandomStrategy(random.Random(99))
    strategies = {p.name: opponent_strat for p in s.players}

    t0 = time.perf_counter()
    root, stats = build_tree(s, player, GameEngine, strategies)
    elapsed = time.perf_counter() - t0

    print(f"Tree stats: {stats}")
    print(f"Build time: {elapsed*1000:.1f}ms")
    print()
    # Only print top 2 levels to avoid wall of text
    print_tree(root)


if __name__ == "__main__":
    test_tree_size()
    print("\n" + "=" * 70 + "\n")
    test_mean_case()
