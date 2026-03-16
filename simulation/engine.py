"""Game engine: loop, action resolution, event chains, all card effects."""
from __future__ import annotations
from state import GameState, Player, Card, Action
from strategy import Strategy, Intent, DecisionContext


# Cards that have only Drafted text (no Activate)
DRAFTED_ONLY = {
    "Incite", "Harvest", "Gathering", "Uprising", "Culling",
    "Feed the Commoners", "Regrowth", "Solstice", "Famine",
    "Rumour", "Ingenuity", "Spoils of War",
}

# Cards that have standalone Activate text (not zone gateways or On-Event-only)
ACTIVATABLE = {
    "Warband", "Blood Offering", "Poach", "Chiefdom", "Racketeering",
    "Tyranny", "Outriders", "Land Grab", "Ransack", "Dusk Rite",
    "Sky Dance", "Sacred Grove", "Oral Tradition", "Herbalism",
    "Forage", "Remembrance", "Crags",
    "Granary", "Mill", "Animal Husbandry", "Militia", "Mine",
    # Note: Sowing, Withered Crop, Apprenticeship are zone gateways — handled via
    # activate_wheat / activate_coin actions. Plough has no standalone Activate.
    # Armament needs Sword deck (not in game yet).
}

# On-event responder sets (used for player-ordered resolution)
BRAWL_RESPONDERS = {"Raid", "Scavenge", "Spoils of War", "Rite of Passage", "Eldership", "Militia", "Crags"}
FEAST_RESPONDERS = {"Tavern", "Share the Spoils", "Marauders"}
HARVEST_RESPONDERS = {"Plough", "Solstice"}
RITE_RESPONDERS = {"Worship of the Hunt", "Worship of War", "Worship of the Rain", "Worship of Fertility", "Worship of the Flame"}
RUMOUR_RESPONDERS = {"Village Gossip"}

# Cards activatable from discard
ACTIVATE_FROM_DISCARD = {"Highlander", "Nomad"}


class GameEngine:
    def __init__(self, state: GameState, strategies: dict[str, Strategy]):
        self.state = state
        self.strategies = strategies  # player_name -> Strategy
        self._event_depth = 0
        self._max_event_depth = 10

    def strat(self, player: Player) -> Strategy:
        return self.strategies[player.name]

    # ── Valid Actions ──

    def get_valid_actions(self, player: Player) -> list[Action]:
        actions: list[Action] = []
        s = self.state

        # Take from Season
        for card in s.season:
            actions.append(Action("take_season", card=card, label=f"Take {card.name} from Season"))

        # Draw from Claw (always available)
        if s.pile_remaining("claw") > 0:
            actions.append(Action("draw_claw", label="Draw 2 from Claw"))

        # Activate cards in Domain
        for card in player.domain:
            if card.name in ACTIVATABLE and card.name not in DRAFTED_ONLY:
                if self._can_activate(player, card):
                    actions.append(Action("activate", card=card, label=f"Activate {card.name}"))

        # Activate Wheat zone (via gateway cards — Sowing, Withered Crop, AH, Plough)
        if player.has_wheat_access() and len(s.fields) > 0:
            actions.append(Action("activate_wheat", label="Activate Wheat zone"))

        # Activate Coin zone (via Apprenticeship or AH — not Mill/Mine which draw directly)
        if self._has_coin_zone_access(player) and (len(s.wares) > 0 or s.pile_remaining("coin") > 0):
            actions.append(Action("activate_coin", label="Activate Coin zone"))

        # Activate from discard (Highlander/Nomad)
        for card in player.discard:
            if card.name in ACTIVATE_FROM_DISCARD:
                if self._can_activate_from_discard(player, card):
                    actions.append(Action("activate_from_discard", card=card,
                                          label=f"Activate {card.name} from discard"))

        # Activate Well in any player's Domain
        for p in s.players:
            if p.has_card("Well") and s.pile_remaining("tree") > 0:
                actions.append(Action("activate_well", owner=p,
                                      label=f"Activate {p.name}'s Well"))

        if not actions:
            actions.append(Action("pass", label="Pass (no valid actions)"))

        return actions

    def _can_activate(self, player: Player, card: Card) -> bool:
        """Check if a specific card can be activated."""
        match card.name:
            case "Sowing":
                return player.count_tag("Nature") >= 2 and len(self.state.fields) > 0
            case "Withered Crop":
                return player.has_discard("Harvest") and len(self.state.fields) > 0
            case "Apprenticeship":
                # Needs another player with Craftsmanship
                for p in self.state.other_players(player):
                    if p.count_tag("Craftsmanship") > 0:
                        return True
                return False
            case "Oral Tradition":
                # Needs a Coin card to discard
                return any(c.deck == "coin" for c in player.domain) and self.state.pile_remaining("candle") > 0
            case "Herbalism":
                # Needs Knowledge or Nature card to discard, and non-empty discard
                has_cost = any(c.has_tag("Knowledge") or c.has_tag("Nature") for c in player.domain if c.name != "Herbalism")
                return has_cost and len(player.discard) > 0
            case "Armament":
                # Needs Coin card to discard — skip, no Sword deck
                return False
            case "Blood Offering":
                return len(player.domain) > 1  # needs something to discard
            case "Dusk Rite":
                return len(player.discard) > 0
            case "Militia":
                # Can always activate (On Brawl cancel is passive), but active ability needs Mob
                return player.count_tag("Mob") > 0
            case "Land Grab":
                return any(c.has_tag("Land") for c in self.state.season)
            case "Ransack":
                return len(player.domain) > 1 and (self.state.pile_remaining("claw") > 0 or len(self.state.season) > 0)
            case "Chiefdom":
                # Need Mob in own domain or same-culture domain
                if player.count_tag("Mob") > 0:
                    return True
                for p in self.state.other_players(player):
                    if player.shares_culture(p) and p.count_tag("Mob") > 0:
                        return True
                return False
            case _:
                return True

    def _can_activate_from_discard(self, player: Player, card: Card) -> bool:
        match card.name:
            case "Highlander":
                return player.has_card("Crags")
            case "Nomad":
                return player.has_card("Pasture")
            case _:
                return False

    def _has_coin_zone_access(self, player: Player) -> bool:
        """Check if player can activate the Coin zone (Buy/Trade)."""
        if player.has_card("Animal Husbandry"):
            return True
        if player.has_card("Apprenticeship"):
            for p in self.state.other_players(player):
                if p.count_tag("Craftsmanship") > 0:
                    return True
        return False

    # ── Main Turn Resolution ──

    def run_game(self, max_turns: int = 200) -> str | None:
        s = self.state
        s.log(f"# Kingdoms Simulation\n")
        s.log(f"**Players:** {', '.join(p.name for p in s.players)} "
              f"({len(s.players)} players, max {max_turns} turns)\n")
        s.log("---\n")
        s.log("## Initial State\n")
        s.log(f"Season: {', '.join(c.name for c in s.season)}")
        s.log(f"Fields ({len(s.fields)}): {', '.join(c.name for c in s.fields)}")
        s.log(f"Wares ({len(s.wares)}): {', '.join(c.name for c in s.wares)}")
        piles = ", ".join(f"{d} {s.pile_remaining(d)}" for d in ("claw", "tree", "wheat", "coin", "candle") if d in s.piles)
        s.log(f"Piles: {piles}")
        s.log("\n---\n")

        for t in range(1, max_turns + 1):
            if s.game_over:
                break

            s.turn_num = t
            p_idx = (t - 1) % len(s.players)
            player = s.players[p_idx]

            # Round header
            if p_idx == 0:
                s.round_num += 1
                s.hunt_uses_this_round = 0
                end_t = min(t + len(s.players) - 1, max_turns)
                s.log(f"## Round {s.round_num} (Turns {t}–{end_t})\n")

            self.resolve_turn(player)

            # State snapshot every 10 turns
            if t % 10 == 0:
                self._log_state_snapshot(t)

            # Check game end
            depleted = s.check_game_end()
            if depleted:
                s.game_over = True
                s.depleted_pile = depleted
                s.log(f"\n### 🏁 GAME ENDS — {depleted} zone fully depleted! (Turn {t})\n")

        self._log_epilogue()
        return s.depleted_pile

    def resolve_turn(self, player: Player):
        s = self.state
        actions = self.get_valid_actions(player)
        action = self.strat(player).choose_action(
            s, player, actions,
            DecisionContext(Intent.TURN_ACTION, source="turn"))
        s.log(f"**T{s.turn_num} — {player.name}:** {action.label}")

        match action.type:
            case "take_season":
                self._do_take_season(player, action.card)
            case "draw_claw":
                self._do_draw_claw(player)
            case "activate":
                self._do_activate(player, action.card)
            case "activate_wheat":
                self._do_activate_wheat(player)
            case "activate_coin":
                self._do_activate_coin(player)
            case "activate_from_discard":
                self._do_activate_from_discard(player, action.card)
            case "activate_well":
                self._do_activate_well(player, action.owner)
            case "pass":
                s.log("  *(no valid actions)*")

        s.log("")

    # ── Core Actions ──

    def _do_take_season(self, player: Player, card: Card):
        s = self.state
        if card in s.season:
            s.season.remove(card)
            self._receive_card(player, card)
            s.refill_season()

    def _do_draw_claw(self, player: Player):
        for _ in range(2):
            card = self.state.draw_from_pile("claw")
            if card:
                self.state.log(f"  draws {card.name} from Claw")
                self._receive_card(player, card)
            if self.state.game_over:
                break

    def _do_activate(self, player: Player, card: Card):
        s = self.state
        match card.name:
            case "Warband":
                # Brawl in domain with most cards
                targets = sorted(s.other_players(player), key=lambda p: len(p.domain), reverse=True)
                if targets:
                    # If tied, strategy picks
                    max_cards = len(targets[0].domain)
                    tied = [p for p in targets if len(p.domain) == max_cards]
                    target = self.strat(player).choose_from(
                        s, player, tied,
                        DecisionContext(Intent.PICK_TARGET, source="Warband",
                                        consequence="Brawl in their Domain"))
                    s.log(f"  → triggers Brawl in {target.name}'s Domain")
                    self.resolve_brawl(player, target)

            case "Blood Offering":
                # Discard 1 card, trigger Rite
                sacrificeable = [c for c in player.domain if c is not card]
                if sacrificeable:
                    victim = self.strat(player).choose_from(
                        s, player, sacrificeable,
                        DecisionContext(Intent.SACRIFICE, source="Blood Offering",
                                        consequence="triggers Rite"))
                    player.discard_from_domain(victim)
                    s.log(f"  → discards {victim.name}, triggers Rite")
                    self.resolve_rite(player)

            case "Poach":
                hunt_limit = 1 + sum(1 for c in player.domain if c.name == "Pasture")
                if s.hunt_uses_this_round < hunt_limit:
                    s.hunt_uses_this_round += 1
                    s.log(f"  → triggers Feast in {player.name}'s Domain")
                    self.resolve_feast(player)
                else:
                    s.log(f"  → Hunt limit reached ({hunt_limit}), no effect")

            case "Chiefdom":
                # Move 1 Mob from own domain or same-culture domain to any other domain
                mob_sources: list[tuple[Player, Card]] = []
                for mob in player.cards_with_tag("Mob"):
                    mob_sources.append((player, mob))
                for p in s.other_players(player):
                    if player.shares_culture(p):
                        for mob in p.cards_with_tag("Mob"):
                            mob_sources.append((p, mob))
                if mob_sources:
                    source_player, mob = self.strat(player).choose_from(
                        s, player, mob_sources,
                        DecisionContext(Intent.PICK_TARGET, source="Chiefdom",
                                        consequence="chosen Mob moves to another Domain"))
                    targets = [p for p in s.players if p is not source_player]
                    target = self.strat(player).choose_from(
                        s, player, targets,
                        DecisionContext(Intent.PICK_TARGET, source="Chiefdom",
                                        consequence="chosen Mob moves there"))
                    source_player.remove_from_domain(mob)
                    target.add_to_domain(mob, s)
                    s.log(f"  → moves {mob.name} from {source_player.name} to {target.name}")

            case "Racketeering":
                targets = s.other_players(player)
                if targets:
                    target = self.strat(player).choose_from(
                        s, player, targets,
                        DecisionContext(Intent.PICK_TARGET, source="Racketeering",
                                        consequence="they offer a card; refusal triggers Brawl"))
                    if target.domain:
                        # Target offers a card (strategy picks for target)
                        offered = self.strat(target).choose_from(
                            s, target, list(target.domain),
                            DecisionContext(Intent.GIVE_AWAY, source="Racketeering",
                                            opponent=player,
                                            consequence="opponent may take this card"))
                        take_it = self.strat(player).choose_yes_no(
                            s, player,
                            DecisionContext(Intent.ACCEPT_REJECT, source="Racketeering",
                                            opponent=target,
                                            consequence="refuse triggers Brawl"))
                        if take_it:
                            target.remove_from_domain(offered)
                            player.add_to_domain(offered, s)
                            s.log(f"  → takes {offered.name} from {target.name}")
                        else:
                            s.log(f"  → refuses {offered.name}, triggers Brawl in {target.name}'s Domain")
                            self.resolve_brawl(player, target)
                    else:
                        s.log(f"  → {target.name} has no cards to offer")

            case "Tyranny":
                discontent_count = player.count_tag("Discontent")
                drawn = []
                for _ in range(discontent_count):
                    c = s.draw_from_pile("claw")
                    if c:
                        drawn.append(c)
                s.log(f"  → draws {len(drawn)} from Claw ({discontent_count} Discontent)")
                for c in drawn:
                    self._receive_card(player, c)
                if s.game_over:
                    return
                s.log(f"  → triggers self-Brawl (spoils discarded, not given)")
                self.resolve_brawl(player, player, uprising_rules=True)

            case "Outriders":
                drawn = []
                for _ in range(3):
                    c = s.draw_from_pile("claw")
                    if c:
                        drawn.append(c)
                if drawn:
                    s.log(f"  → draws 3 from Claw: {', '.join(c.name for c in drawn)}")
                    # Discard 1
                    if len(drawn) > 1:
                        to_discard = self.strat(player).choose_from(
                            s, player, drawn,
                            DecisionContext(Intent.SACRIFICE, source="Outriders",
                                            consequence="discard it; keep the rest"))
                        drawn.remove(to_discard)
                        player.discard.append(to_discard)
                        s.log(f"  → discards {to_discard.name}")
                    for c in drawn:
                        self._receive_card(player, c)

            case "Land Grab":
                lands = [c for c in s.season if c.has_tag("Land")]
                for land in lands:
                    s.season.remove(land)
                    player.add_to_domain(land, s)
                    s.log(f"  → takes {land.name} from Season")
                player.discard_from_domain(card)
                s.log(f"  → discards Land Grab")
                s.refill_season()

            case "Ransack":
                sacrificeable = [c for c in player.domain if c is not card]
                if sacrificeable:
                    victim = self.strat(player).choose_from(
                        s, player, sacrificeable,
                        DecisionContext(Intent.SACRIFICE, source="Ransack",
                                        consequence="activate Claw and Tree zones"))
                    player.discard_from_domain(victim)
                    s.log(f"  → discards {victim.name}")
                    # Activate Claw zone (draw 2)
                    for _ in range(2):
                        c = s.draw_from_pile("claw")
                        if c:
                            s.log(f"  → Claw: draws {c.name}")
                            self._receive_card(player, c)
                    # Activate Tree zone (take 1 from Season)
                    if s.season:
                        pick = self.strat(player).choose_from(
                            s, player, list(s.season),
                            DecisionContext(Intent.GAIN, source="Ransack",
                                            consequence="take it from Season"))
                        s.season.remove(pick)
                        s.log(f"  → Tree: takes {pick.name} from Season")
                        self._receive_card(player, pick)
                        s.refill_season()

            case "Dusk Rite":
                # Remove cards from discard, draw Claw+Tree equal to count, trigger Rite
                if player.discard:
                    to_remove = self.strat(player).choose_n(
                        s, player, list(player.discard), 1, len(player.discard),
                        DecisionContext(Intent.SACRIFICE, source="Dusk Rite",
                                        consequence="remove them permanently, then draw Claw and Tree and trigger Rite"))
                    for c in to_remove:
                        player.discard.remove(c)
                    removed_count = len(to_remove)
                    s.log(f"  → removes {removed_count} cards from discard permanently")
                    for _ in range(removed_count):
                        c = s.draw_from_pile("claw")
                        if c:
                            s.log(f"  → draws {c.name} from Claw")
                            self._receive_card(player, c)
                    for _ in range(removed_count):
                        c = s.draw_from_pile("tree")
                        if c:
                            s.log(f"  → draws {c.name} from Tree")
                            self._receive_card(player, c)
                    player.discard_from_domain(card)
                    s.log(f"  → discards Dusk Rite, triggers Rite")
                    self.resolve_rite(player)

            case "Sky Dance":
                s.log(f"  → triggers Rite")
                self.resolve_rite(player)

            case "Sacred Grove":
                options = ["rite", "scry"]
                choice = self.strat(player).choose_from(
                    s, player, options,
                    DecisionContext(Intent.PICK_OPTION, source="Sacred Grove",
                                    consequence="trigger Rite or scry Tree"))
                if choice == "rite":
                    s.log(f"  → triggers Rite")
                    self.resolve_rite(player)
                else:
                    top3 = s.peek_pile("tree", 3)
                    spiritual = [c for c in top3 if c.has_tag("Spiritual")]
                    if spiritual:
                        # Take spiritual cards
                        for sc in spiritual:
                            s.pile_ptrs["tree"] += 1  # consume from pile
                            player.add_to_domain(sc, s)
                            s.log(f"  → takes {sc.name} (Spiritual) from Tree top")
                        # Remaining go back — they're still in the pile at their positions
                        # Need to handle reordering: strategy picks order for rest
                        remaining = [c for c in top3 if c not in spiritual]
                        for c in remaining:
                            s.pile_ptrs["tree"] += 1
                        # Put remaining back on top in chosen order
                        if remaining:
                            ptr = s.pile_ptrs["tree"]
                            for i, c in enumerate(remaining):
                                s.piles["tree"].insert(ptr - len(remaining) + i, c)
                            # Adjust pointer back
                            s.pile_ptrs["tree"] -= len(remaining)
                    else:
                        # Just peek, put back in any order
                        s.log(f"  → scries top 3 Tree: {', '.join(c.name for c in top3)}. No Spiritual found.")

            case "Oral Tradition":
                coin_cards = [c for c in player.domain if c.deck == "coin"]
                if coin_cards:
                    to_discard = self.strat(player).choose_from(
                        s, player, coin_cards,
                        DecisionContext(Intent.SACRIFICE, source="Oral Tradition",
                                        consequence="draw a Candle card"))
                    player.discard_from_domain(to_discard)
                    candle = s.draw_from_pile("candle")
                    if candle:
                        s.log(f"  → discards {to_discard.name}, draws {candle.name} from Candle")
                        self._receive_card(player, candle)

            case "Herbalism":
                costs = [c for c in player.domain if (c.has_tag("Knowledge") or c.has_tag("Nature")) and c is not card]
                if costs and player.discard:
                    cost_card = self.strat(player).choose_from(
                        s, player, costs,
                        DecisionContext(Intent.SACRIFICE, source="Herbalism",
                                        consequence="recover a card from discard"))
                    player.discard_from_domain(cost_card)
                    target_card = self.strat(player).choose_from(
                        s, player, list(player.discard),
                        DecisionContext(Intent.GAIN, source="Herbalism",
                                        consequence="recover it from discard"))
                    player.discard.remove(target_card)
                    player.add_to_domain(target_card, s)
                    s.log(f"  → discards {cost_card.name}, recovers {target_card.name} from discard")

            case "Forage":
                top3 = []
                for _ in range(3):
                    c = s.draw_from_pile("tree")
                    if c:
                        top3.append(c)
                if top3:
                    s.log(f"  → reveals: {', '.join(c.name for c in top3)}")
                    # All go to discard first
                    for c in top3:
                        player.discard.append(c)
                    # May discard Forage to take one to Domain
                    if self.strat(player).choose_yes_no(
                        s, player,
                        DecisionContext(Intent.ACCEPT_REJECT, source="Forage",
                                        consequence="discard Forage to take one revealed card")):
                        pick = self.strat(player).choose_from(
                            s, player, top3,
                            DecisionContext(Intent.GAIN, source="Forage",
                                            consequence="take it from the revealed cards"))
                        player.discard.remove(pick)
                        player.add_to_domain(pick, s)
                        player.discard_from_domain(card)
                        s.log(f"  → takes {pick.name}, discards Forage")
                    else:
                        s.log(f"  → keeps Forage, all to discard")

            case "Remembrance":
                knowledge_count = player.count_tag("Knowledge")
                if player.discard and knowledge_count > 0:
                    to_recover = self.strat(player).choose_n(
                        s, player, list(player.discard),
                        1, min(knowledge_count, len(player.discard)),
                        DecisionContext(Intent.GAIN, source="Remembrance",
                                        consequence="recover them from discard"))
                    for c in to_recover:
                        player.discard.remove(c)
                        player.add_to_domain(c, s)
                        s.log(f"  → recovers {c.name} from discard")

            case "Granary":
                player.discard_from_domain(card)
                s.log(f"  → discards Granary, triggers Feast")
                self.resolve_feast(player)

            case "Mill":
                player.discard_from_domain(card)
                coin = s.draw_from_pile("coin")
                if coin:
                    s.log(f"  → discards Mill, draws {coin.name} from Coin")
                    self._receive_card(player, coin)

            case "Animal Husbandry":
                options = ["wheat", "coin", "feast"]
                choice = self.strat(player).choose_from(
                    s, player, options,
                    DecisionContext(Intent.PICK_OPTION, source="Animal Husbandry",
                                    consequence="activate Wheat, draw Coin, or trigger Feast"))
                if choice == "wheat" and len(s.fields) > 0:
                    s.log(f"  → activates Wheat zone via AH")
                    self._do_activate_wheat(player)
                elif choice == "coin":
                    coin = s.draw_from_pile("coin")
                    if coin:
                        s.log(f"  → draws {coin.name} from Coin via AH")
                        self._receive_card(player, coin)
                else:
                    s.log(f"  → triggers Feast via AH")
                    self.resolve_feast(player)

            case "Militia":
                mobs = player.cards_with_tag("Mob")
                if mobs:
                    mob = self.strat(player).choose_from(
                        s, player, mobs,
                        DecisionContext(Intent.SACRIFICE, source="Militia",
                                        consequence="draw cards from Claw"))
                    player.discard_from_domain(mob)
                    s.log(f"  → Militia discards {mob.name}")

            case "Mine":
                coin = s.draw_from_pile("coin")
                if coin:
                    s.log(f"  → Mine draws {coin.name} from Coin")
                    self._receive_card(player, coin)

            case "Crags":
                top3 = s.peek_pile("claw", 3)
                if top3:
                    s.log(f"  → scouts Claw top 3: {', '.join(c.name for c in top3)}")
                    if self.strat(player).choose_yes_no(
                        s, player,
                        DecisionContext(Intent.ACCEPT_REJECT, source="Crags",
                                        consequence="put one scouted card in discard")):
                        pick = self.strat(player).choose_from(
                            s, player, top3,
                            DecisionContext(Intent.PICK_TARGET, source="Crags",
                                            consequence="put it in discard"))
                        idx = s.piles["claw"].index(pick)
                        s.piles["claw"].pop(idx)
                        # Adjust pointer if we removed before current ptr
                        if idx < s.pile_ptrs["claw"]:
                            s.pile_ptrs["claw"] -= 1
                        player.discard.append(pick)
                        s.log(f"  → puts {pick.name} in discard")

            case "Plough":
                # Plough's activate is only On Harvest, not a main action
                pass

    def _do_activate_wheat(self, player: Player):
        """Take cards from Fields, draw 1 Claw tax per card taken."""
        s = self.state
        if not s.fields:
            s.log("  → Fields empty, nothing to take")
            return
        # Choose which cards to take (1 to min(3, fields count))
        max_take = min(3, len(s.fields))
        to_take = self.strat(player).choose_n(
            s, player, list(s.fields), 1, max_take,
            DecisionContext(Intent.GAIN, source="Wheat zone",
                            consequence="take them from Fields and pay Claw tax"))
        for c in to_take:
            if c in s.fields:
                s.fields.remove(c)
                self._receive_card(player, c)
                s.log(f"  → takes {c.name} from Fields")
        # Claw tax
        tax = len(to_take)
        s.log(f"  → Claw tax: draws {tax}")
        for _ in range(tax):
            claw = s.draw_from_pile("claw")
            if claw:
                s.log(f"    → tax: {claw.name}")
                self._receive_card(player, claw)

    def _do_activate_coin(self, player: Player):
        """Coin zone: Buy or Trade."""
        s = self.state
        options = []
        if s.wares:
            options.append("buy")
        if player.domain and s.pile_remaining("coin") > 0:
            options.append("trade")
        if not options:
            s.log("  → Coin zone: nothing to do")
            return
        choice = self.strat(player).choose_from(
            s, player, options,
            DecisionContext(Intent.PICK_OPTION, source="Coin zone",
                            consequence="buy from Wares or trade a card"))
        if choice == "buy" and s.wares:
            pick = self.strat(player).choose_from(
                s, player, list(s.wares),
                DecisionContext(Intent.GAIN, source="Buy",
                                consequence="buy it from Wares"))
            s.wares.remove(pick)
            player.add_to_domain(pick, s)
            s.log(f"  → buys {pick.name} from Wares")
            s.refill_wares()
        elif choice == "trade" and player.domain:
            to_trade = self.strat(player).choose_from(
                s, player, list(player.domain),
                DecisionContext(Intent.SACRIFICE, source="Trade",
                                consequence="put it in Wares and draw Coin"))
            player.remove_from_domain(to_trade)
            s.wares.append(to_trade)
            coin = s.draw_from_pile("coin")
            if coin:
                s.log(f"  → trades {to_trade.name} into Wares, draws {coin.name} from Coin")
                self._receive_card(player, coin)

    def _do_activate_from_discard(self, player: Player, card: Card):
        """Highlander/Nomad: move from discard to Domain."""
        player.discard.remove(card)
        player.add_to_domain(card, self.state)
        self.state.log(f"  → moves {card.name} from discard to Domain")

    def _do_activate_well(self, player: Player, well_owner: Player):
        """Well: activate Tree zone twice (take 2 from Season)."""
        s = self.state
        s.log(f"  → activates {well_owner.name}'s Well (Tree zone ×2)")
        for i in range(2):
            if s.season:
                pick = self.strat(player).choose_from(
                    s, player, list(s.season),
                    DecisionContext(Intent.GAIN, source="Well",
                                    consequence="take it from Season"))
                s.season.remove(pick)
                s.log(f"  → takes {pick.name} from Season")
                self._receive_card(player, pick)
                s.refill_season()

    # ── Card Receiving (Drafted resolution) ──

    def _receive_card(self, player: Player, card: Card):
        """Handle a card being received — resolve Drafted effects."""
        s = self.state
        match card.name:
            case "Incite":
                mobs = player.cards_with_tag("Mob")
                if mobs:
                    targets = s.other_players(player)
                    if targets:
                        to_move = self.strat(player).choose_n(
                            s, player, mobs, 0, min(3, len(mobs)),
                            DecisionContext(Intent.GIVE_AWAY, source="Incite",
                                            consequence="move them to another Domain"))
                        for mob in to_move:
                            target = self.strat(player).choose_from(
                                s, player, targets,
                                DecisionContext(Intent.PICK_TARGET, source="Incite",
                                                consequence="chosen Mob moves there"))
                            player.remove_from_domain(mob)
                            target.add_to_domain(mob, s)
                            s.log(f"  → Incite: moves {mob.name} to {target.name}")
                player.discard.append(card)
                s.log(f"  → Incite discarded")

            case "Harvest":
                s.log(f"  → Drafted: Harvest triggers!")
                player.discard.append(card)
                self.resolve_harvest(player)

            case "Gathering":
                options = ["brawl", "rite"]  # Rumour has no responders
                choice = self.strat(player).choose_from(
                    s, player, options,
                    DecisionContext(Intent.PICK_OPTION, source="Gathering",
                                    consequence="trigger Brawl or Rite"))
                player.discard.append(card)
                if choice == "brawl":
                    s.log(f"  → Gathering: Brawl in {player.name}'s Domain")
                    self.resolve_brawl(player, player)
                    # Same culture players also trigger
                    for p in s.other_players(player):
                        if player.shares_culture(p):
                            s.log(f"  → Gathering: Brawl also in {p.name}'s Domain (shared culture)")
                            self.resolve_brawl(player, p)
                else:
                    s.log(f"  → Gathering: Rite in {player.name}'s Domain")
                    self.resolve_rite(player)

            case "Uprising":
                s.log(f"  → Drafted: Uprising — self-Brawl (no benefits)")
                player.add_to_domain(card, s)
                self.resolve_brawl(player, player, uprising_rules=True)

            case "Culling":
                # Player with most cards discards 2
                all_players = sorted(s.players, key=lambda p: len(p.domain), reverse=True)
                max_count = len(all_players[0].domain)
                tied = [p for p in all_players if len(p.domain) == max_count]
                target = (
                    self.strat(player).choose_from(
                        s, player, tied,
                        DecisionContext(Intent.PICK_TARGET, source="Culling",
                                        consequence="that player discards cards",
                                        tags=["forced"]))
                    if len(tied) > 1 else tied[0]
                )
                if target.domain:
                    to_discard = self.strat(target).choose_n(
                        s, target, list(target.domain), 1, min(2, len(target.domain)),
                        DecisionContext(Intent.GIVE_AWAY, source="Culling",
                                        opponent=player if target is not player else None,
                                        consequence="discard them from your Domain",
                                        tags=["forced"]))
                    for c in to_discard:
                        target.discard_from_domain(c)
                        s.log(f"  → Culling: {target.name} discards {c.name}")
                player.discard.append(card)

            case "Feed the Commoners":
                discontent = player.cards_with_tag("Discontent")
                if discontent:
                    to_discard = self.strat(player).choose_n(
                        s, player, discontent, 0, min(3, len(discontent)),
                        DecisionContext(Intent.SACRIFICE, source="Feed the Commoners",
                                        consequence="discard chosen Discontent cards"))
                    for c in to_discard:
                        player.discard_from_domain(c)
                        s.log(f"  → Feed the Commoners discards {c.name}")
                player.add_to_domain(card, s)

            case "Regrowth":
                for p in s.players:
                    pastures = [c for c in p.discard if c.name == "Pasture"]
                    for pas in pastures:
                        p.discard.remove(pas)
                        p.add_to_domain(pas, s)
                        s.log(f"  → Regrowth: returns Pasture to {p.name}")
                player.discard.append(card)

            case "Solstice":
                # On Harvest responder, not Drafted — but it IS Drafted (drafted text exists)
                # Wait: Solstice has "On Harvest" text, not Drafted text. It stays in domain.
                # Re-checking game-cards.md: Solstice is "On Harvest — choose one..."
                # It has NO drafted text, so it just goes to Domain normally.
                player.add_to_domain(card, s)

            case "Famine":
                targets = s.other_players(player)
                valid_targets = [p for p in targets if any(c.deck == "wheat" for c in p.domain)]
                if valid_targets:
                    target = self.strat(player).choose_from(
                        s, player, valid_targets,
                        DecisionContext(Intent.PICK_TARGET, source="Famine",
                                        consequence="they discard a Wheat card"))
                    wheat_cards = [c for c in target.domain if c.deck == "wheat"]
                    if wheat_cards:
                        victim = self.strat(player).choose_from(
                            s, player, wheat_cards,
                            DecisionContext(Intent.GIVE_AWAY, source="Famine",
                                            opponent=target,
                                            consequence="that card is discarded",
                                            tags=["forced"]))
                        target.discard_from_domain(victim)
                        s.log(f"  → Famine: {target.name} discards {victim.name}")
                player.discard.append(card)

            case "Rumour":
                s.log(f"  → Drafted: Rumour triggers!")
                player.discard.append(card)
                self.resolve_rumour(player)

            case "Ingenuity":
                coin = s.draw_from_pile("coin")
                if coin:
                    s.log(f"  → Ingenuity: draws {coin.name} from Coin")
                    self._receive_card(player, coin)
                player.add_to_domain(card, s)

            case "Spoils of War":
                targets = s.other_players(player)
                if targets:
                    target = self.strat(player).choose_from(
                        s, player, targets,
                        DecisionContext(Intent.PICK_TARGET, source="Spoils of War",
                                        consequence="Spoils of War enters that Domain"))
                    target.add_to_domain(card, s)
                    s.log(f"  → Spoils of War placed in {target.name}'s Domain")
                else:
                    player.add_to_domain(card, s)

            case "Highlander":
                if not player.has_card("Crags"):
                    player.discard.append(card)
                    s.log(f"  → Drafted: no Crags → Highlander to discard")
                else:
                    player.add_to_domain(card, s)

            case "Nomad":
                if not player.has_card("Pasture"):
                    player.discard.append(card)
                    s.log(f"  → Drafted: no Pasture → Nomad to discard")
                else:
                    player.add_to_domain(card, s)

            case "Plough":
                if not player.has_card("Pasture"):
                    player.discard.append(card)
                    s.log(f"  → Drafted: no Pasture → Plough to discard")
                else:
                    player.discard_from_domain(player.get_card("Pasture"))
                    player.add_to_domain(card, s)
                    s.log(f"  → Drafted: discards Pasture to keep Plough")

            case "Animal Husbandry":
                if not player.has_card("Pasture"):
                    player.discard.append(card)
                    s.log(f"  → Drafted: no Pasture → Animal Husbandry to discard")
                else:
                    player.discard_from_domain(player.get_card("Pasture"))
                    player.add_to_domain(card, s)
                    s.log(f"  → Drafted: discards Pasture to keep Animal Husbandry")

            case "Mine":
                if not player.has_card("Crags"):
                    player.discard.append(card)
                    s.log(f"  → Drafted: no Crags → Mine to discard")
                else:
                    player.discard_from_domain(player.get_card("Crags"))
                    player.add_to_domain(card, s)
                    s.log(f"  → Drafted: discards Crags to keep Mine")

            case _:
                # No special Drafted effect — just add to Domain
                player.add_to_domain(card, s)

    # ── Event Resolution ──

    def resolve_rite(self, triggerer: Player):
        """Resolve Rite event. Benefits go to the triggering player, not the card owner.
        Each domain's owner chooses resolution order of their On Rite cards."""
        if self._event_depth >= self._max_event_depth:
            self.state.log("  ⚠️ Event chain too deep, stopping")
            return
        self._event_depth += 1
        s = self.state

        # Pre-count total Spiritual On Rite responders for Worship of the Flame
        total_spiritual = 0
        for p in s.players:
            for c in p.domain:
                if c.name in RITE_RESPONDERS:
                    total_spiritual += 1

        flame_draws_done = False

        for p in s.play_order_from(triggerer):
            if s.game_over:
                break
            responders = [c for c in p.domain if c.name in RITE_RESPONDERS]
            if not responders:
                continue
            # Owner chooses resolution order of their On Rite cards
            ordered = self.strat(p).choose_order(
                s, p, responders,
                DecisionContext(Intent.ORDER, source="Rite",
                                tags=["event:Rite"]))
            for card in ordered:
                if card not in p.domain or s.game_over:
                    continue
                match card.name:
                    case "Worship of the Hunt":
                        hunts = triggerer.cards_with_tag("Hunt")
                        for h in hunts:
                            s.log(f"  → {p.name}'s Worship of the Hunt: {triggerer.name} feasts via {h.name}")
                            self.resolve_feast(triggerer)

                    case "Worship of War":
                        targets = list(s.players)
                        target = self.strat(triggerer).choose_from(
                            s, triggerer, targets,
                            DecisionContext(Intent.PICK_TARGET, source="Worship of War",
                                            consequence="Brawl in that Domain",
                                            tags=["event:Rite"]))
                        s.log(f"  → {p.name}'s Worship of War: {triggerer.name} Brawls {target.name}")
                        self.resolve_brawl(triggerer, target)

                    case "Worship of the Rain":
                        if s.season:
                            to_discard = self.strat(triggerer).choose_from(
                                s, triggerer, list(s.season),
                                DecisionContext(Intent.PICK_TARGET, source="Worship of the Rain",
                                                consequence="replace it with a Tree card",
                                                tags=["event:Rite"]))
                            s.season.remove(to_discard)
                            replacement = s.draw_from_pile("tree")
                            if replacement:
                                s.season.append(replacement)
                                s.log(f"  → {p.name}'s Worship of the Rain: swaps {to_discard.name} → {replacement.name}")
                            else:
                                s.log(f"  → {p.name}'s Worship of the Rain: removed {to_discard.name}, no replacement")

                    case "Worship of Fertility":
                        s.log(f"  → {p.name}'s Worship of Fertility: triggers Harvest for {triggerer.name}")
                        self.resolve_harvest(triggerer)

                    case "Worship of the Flame":
                        if not flame_draws_done:
                            flame_draws_done = True
                            draws = total_spiritual
                            s.log(f"  → {p.name}'s Worship of the Flame: {triggerer.name} draws {draws} ({total_spiritual} Spiritual responded)")
                            for _ in range(draws):
                                decks = [d for d in ("claw", "tree", "wheat", "coin", "candle") if s.pile_remaining(d) > 0]
                                if decks:
                                    deck = self.strat(triggerer).choose_from(
                                        s, triggerer, decks,
                                        DecisionContext(Intent.GAIN, source="Worship of the Flame",
                                                        consequence="draw a card from that pile",
                                                        tags=["event:Rite"]))
                                    drawn = s.draw_from_pile(deck)
                                    if drawn:
                                        s.log(f"    → draws {drawn.name} from {deck}")
                                        self._receive_card(triggerer, drawn)

        self._event_depth -= 1

    def resolve_brawl(self, triggerer: Player, target: Player, uprising_rules: bool = False):
        """Resolve Brawl in target's Domain. Target chooses resolution order of their
        On Brawl cards — including cancellation cards (Eldership, Militia, Crags).
        If any cancel fires, remaining cards don't resolve."""
        if self._event_depth >= self._max_event_depth:
            self.state.log("  ⚠️ Event chain too deep, stopping")
            return
        self._event_depth += 1
        s = self.state
        brawl_cancelled = False
        crags_defense_checked = False

        # Collect ALL On Brawl cards in target's domain
        responders = [c for c in target.domain if c.name in BRAWL_RESPONDERS]

        if responders:
            # Target chooses resolution order — this is strategically important
            ordered = self.strat(target).choose_order(
                s, target, responders,
                DecisionContext(Intent.ORDER, source="Brawl",
                                tags=["event:Brawl"]))
        else:
            ordered = []

        for card in ordered:
            if brawl_cancelled or s.game_over:
                break
            if card not in target.domain:
                continue  # card was removed by earlier resolution

            match card.name:
                case "Eldership":
                    if triggerer.shares_culture(target):
                        if self.strat(target).choose_yes_no(
                            s, target,
                            DecisionContext(Intent.ACCEPT_REJECT, source="Eldership",
                                            opponent=triggerer if triggerer is not target else None,
                                            consequence="Brawl cancelled",
                                            tags=["event:Brawl"])):
                            tree = s.draw_from_pile("tree")
                            if tree:
                                s.log(f"  → Eldership cancels Brawl. {triggerer.name} draws {tree.name}")
                                self._receive_card(triggerer, tree)
                            else:
                                s.log(f"  → Eldership cancels Brawl")
                            brawl_cancelled = True

                case "Militia":
                    if self.strat(target).choose_yes_no(
                        s, target,
                        DecisionContext(Intent.ACCEPT_REJECT, source="Militia",
                                        opponent=triggerer if triggerer is not target else None,
                                        consequence="Brawl cancelled",
                                        tags=["event:Brawl"])):
                        target.discard_from_domain(card)
                        s.log(f"  → Militia cancels Brawl (Militia discarded)")
                        brawl_cancelled = True

                case "Crags":
                    if not crags_defense_checked:
                        crags_defense_checked = True
                        crags_count = sum(1 for c in target.domain if c.name == "Crags")
                        if crags_count >= 2:
                            if triggerer.domain:
                                if self.strat(triggerer).choose_yes_no(
                                    s, triggerer,
                                    DecisionContext(Intent.ACCEPT_REJECT, source="Crags",
                                                    opponent=target if target is not triggerer else None,
                                                    consequence="Brawl cancelled if refused",
                                                    tags=["event:Brawl"])):
                                    victim = self.strat(triggerer).choose_from(
                                        s, triggerer, list(triggerer.domain),
                                        DecisionContext(Intent.SACRIFICE, source="Crags",
                                                        opponent=target if target is not triggerer else None,
                                                        consequence="Brawl continues",
                                                        tags=["event:Brawl"]))
                                    triggerer.discard_from_domain(victim)
                                    s.log(f"  → {triggerer.name} discards {victim.name} to overcome Crags defense")
                                else:
                                    s.log(f"  → Brawl cancelled by Crags defense")
                                    brawl_cancelled = True
                            else:
                                s.log(f"  → Brawl cancelled by Crags defense (triggerer has no cards)")
                                brawl_cancelled = True

                case "Raid":
                    giveable = [c for c in target.domain if c is not card]
                    if giveable:
                        if uprising_rules:
                            victim = self.strat(target).choose_from(
                                s, target, giveable,
                                DecisionContext(Intent.GIVE_AWAY, source="Raid",
                                                opponent=triggerer if triggerer is not target else None,
                                                consequence="discard it because of Uprising",
                                                tags=["event:Brawl", "forced", "uprising"]))
                            target.discard_from_domain(victim)
                            s.log(f"  → Raid: {target.name} discards {victim.name} (Uprising)")
                        else:
                            victim = self.strat(target).choose_from(
                                s, target, giveable,
                                DecisionContext(Intent.GIVE_AWAY, source="Raid",
                                                opponent=triggerer if triggerer is not target else None,
                                                consequence="card goes to attacker",
                                                tags=["event:Brawl"]))
                            target.remove_from_domain(victim)
                            triggerer.add_to_domain(victim, s)
                            s.log(f"  → Raid: {target.name} gives {victim.name} to {triggerer.name}")

                case "Scavenge":
                    if target.discard:
                        if uprising_rules:
                            s.log(f"  → Scavenge: no effect (Uprising)")
                        else:
                            victim = self.strat(target).choose_from(
                                s, target, list(target.discard),
                                DecisionContext(Intent.GIVE_AWAY, source="Scavenge",
                                                opponent=triggerer if triggerer is not target else None,
                                                consequence="opponent takes it from your discard",
                                                tags=["event:Brawl"]))
                            target.discard.remove(victim)
                            triggerer.add_to_domain(victim, s)
                            s.log(f"  → Scavenge: {triggerer.name} takes {victim.name} from {target.name}'s discard")

                case "Spoils of War":
                    if not uprising_rules:
                        target.remove_from_domain(card)
                        triggerer.add_to_domain(card, s)
                        trophy_count = triggerer.count_tag("Trophy")
                        s.log(f"  → Spoils of War → {triggerer.name}, draws {trophy_count} Claw + {trophy_count} Tree")
                        for _ in range(trophy_count):
                            c = s.draw_from_pile("claw")
                            if c:
                                self._receive_card(triggerer, c)
                        for _ in range(trophy_count):
                            c = s.draw_from_pile("tree")
                            if c:
                                self._receive_card(triggerer, c)
                    else:
                        s.log(f"  → Spoils of War: no effect (Uprising)")

                case "Rite of Passage":
                    tree = s.draw_from_pile("tree")
                    if tree:
                        s.log(f"  → Rite of Passage: {target.name} draws {tree.name} from Tree")
                        self._receive_card(target, tree)

        self._event_depth -= 1

    def resolve_feast(self, domain_owner: Player):
        """Resolve Feast in a specific player's Domain.
        Owner chooses resolution order of their On Feast cards."""
        if self._event_depth >= self._max_event_depth:
            self.state.log("  ⚠️ Event chain too deep, stopping")
            return
        self._event_depth += 1
        s = self.state

        responders = [c for c in domain_owner.domain if c.name in FEAST_RESPONDERS]
        if responders:
            ordered = self.strat(domain_owner).choose_order(
                s, domain_owner, responders,
                DecisionContext(Intent.ORDER, source="Feast",
                                tags=["event:Feast"]))
        else:
            ordered = []

        for card in ordered:
            if s.game_over:
                break
            if card not in domain_owner.domain:
                continue  # removed during earlier resolution

            match card.name:
                case "Tavern":
                    discontent = domain_owner.cards_with_tag("Discontent")
                    if discontent:
                        victim = self.strat(domain_owner).choose_from(
                            s, domain_owner, discontent,
                            DecisionContext(Intent.SACRIFICE, source="Tavern",
                                            consequence="discard that Discontent",
                                            tags=["event:Feast"]))
                        domain_owner.discard_from_domain(victim)
                        s.log(f"  → Tavern: discards {victim.name}")

                case "Share the Spoils":
                    claw = s.draw_from_pile("claw")
                    if claw:
                        s.log(f"  → Share the Spoils: draws {claw.name} from Claw")
                        self._receive_card(domain_owner, claw)

                case "Marauders":
                    domain_owner.discard_from_domain(card)
                    claw = s.draw_from_pile("claw")
                    if claw:
                        s.log(f"  → Marauders: self-destructs, draws {claw.name} from Claw")
                        self._receive_card(domain_owner, claw)
                    else:
                        s.log(f"  → Marauders: self-destructs")

        self._event_depth -= 1

    def resolve_harvest(self, triggerer: Player):
        """Resolve Harvest event. Refills Fields, then each player resolves
        their On Harvest cards in their chosen order."""
        if self._event_depth >= self._max_event_depth:
            self.state.log("  ⚠️ Event chain too deep, stopping")
            return
        self._event_depth += 1
        s = self.state

        # Refill Fields
        old_count = len(s.fields)
        s.refill_fields(5)
        new_count = len(s.fields)
        if new_count > old_count:
            s.log(f"  → Fields refilled: {old_count} → {new_count}")

        # On Harvest responders — each player chooses their resolution order
        for p in s.play_order_from(triggerer):
            if s.game_over:
                break
            responders = [c for c in p.domain if c.name in HARVEST_RESPONDERS]
            if not responders:
                continue
            ordered = self.strat(p).choose_order(
                s, p, responders,
                DecisionContext(Intent.ORDER, source="Harvest",
                                tags=["event:Harvest"]))
            for card in ordered:
                if card not in p.domain or s.game_over:
                    continue
                match card.name:
                    case "Plough":
                        options = ["feast", "wheat"]
                        choice = self.strat(p).choose_from(
                            s, p, options,
                            DecisionContext(Intent.PICK_OPTION, source="Plough",
                                            consequence="trigger Feast or activate Wheat",
                                            tags=["event:Harvest"]))
                        if choice == "feast":
                            s.log(f"  → {p.name}'s Plough: triggers Feast")
                            self.resolve_feast(p)
                        else:
                            if s.fields:
                                s.log(f"  → {p.name}'s Plough: activates Wheat zone")
                                self._do_activate_wheat(p)

                    case "Solstice":
                        options = ["culture_draw", "culture_place"]
                        choice = self.strat(p).choose_from(
                            s, p, options,
                            DecisionContext(Intent.PICK_OPTION, source="Solstice",
                                            consequence="culture allies draw or place a Culture",
                                            tags=["event:Harvest"]))
                        if choice == "culture_draw":
                            for ally in s.players:
                                if p.shares_culture(ally) or ally is p:
                                    tree = s.draw_from_pile("tree")
                                    if tree:
                                        s.log(f"  → Solstice: {ally.name} draws {tree.name} from Tree")
                                        self._receive_card(ally, tree)
                        else:
                            culture_cards = [c for c in p.discard if c.has_tag("Culture")]
                            if culture_cards:
                                culture = self.strat(p).choose_from(
                                    s, p, culture_cards,
                                    DecisionContext(Intent.GAIN, source="Solstice",
                                                    consequence="place it from discard into a Domain",
                                                    tags=["event:Harvest"]))
                                target = self.strat(p).choose_from(
                                    s, p, list(s.players),
                                    DecisionContext(Intent.PICK_TARGET, source="Solstice",
                                                    consequence="chosen Culture enters that Domain",
                                                    tags=["event:Harvest"]))
                                p.discard.remove(culture)
                                target.add_to_domain(culture, s)
                                s.log(f"  → Solstice: places {culture.name} in {target.name}'s Domain")

        self._event_depth -= 1

    def resolve_rumour(self, triggerer: Player):
        """Resolve Rumour event."""
        if self._event_depth >= self._max_event_depth:
            return
        self._event_depth += 1
        s = self.state

        for p in s.play_order_from(triggerer):
            for card in list(p.domain):
                if card.name == "Village Gossip":
                    decks = [d for d in s.piles if s.pile_remaining(d) > 0]
                    if decks:
                        deck = self.strat(p).choose_from(
                            s, p, decks,
                            DecisionContext(Intent.PICK_OPTION, source="Village Gossip",
                                            consequence="peek that pile's top card",
                                            tags=["event:Rumour"]))
                        top = s.peek_pile(deck, 1)
                        if top:
                            if self.strat(p).choose_yes_no(
                                s, p,
                                DecisionContext(Intent.ACCEPT_REJECT, source="Village Gossip",
                                                consequence="move the peeked card to bottom of the pile",
                                                tags=["event:Rumour"])):
                                # Remove from top, add to bottom
                                s.piles[deck].pop(s.pile_ptrs[deck])
                                s.piles[deck].append(top[0])
                                s.log(f"  → Village Gossip: {p.name} sends {top[0].name} to bottom of {deck}")
                            else:
                                s.log(f"  → Village Gossip: {p.name} peeks at {deck} top, leaves it")

        self._event_depth -= 1

    # ── Logging Helpers ──

    def _log_state_snapshot(self, turn: int):
        s = self.state
        s.log("---\n")
        s.log(f"### State after Turn {turn}\n")
        for p in s.players:
            dom = ", ".join(c.name for c in p.domain) or "*(empty)*"
            s.log(f"**{p.name}** ({len(p.domain)} cards): {dom}")
            disc = ", ".join(c.name for c in p.discard)
            if disc:
                s.log(f"  Discard: {disc}")
        s.log("")
        s.log(f"Season: {', '.join(c.name for c in s.season)}")
        s.log(f"Fields ({len(s.fields)}): {', '.join(c.name for c in s.fields)}")
        s.log(f"Wares ({len(s.wares)}): {', '.join(c.name for c in s.wares)}")
        piles = ", ".join(f"{d} {s.pile_remaining(d)}" for d in ("claw", "tree", "wheat", "coin", "candle") if d in s.piles)
        s.log(f"Piles: {piles}")
        s.log("\n---\n")

    def _log_epilogue(self):
        s = self.state
        s.log("---\n")
        s.log("## Epilogue\n")

        win_conditions = {
            "tree": ("Nature", "🌳 Tree depleted — most [Nature] wins"),
            "claw": ("Trophy", "🐾 Claw depleted — most [Trophy] wins"),
            "wheat": ("Amenity", "🌾 Wheat depleted — most [Amenity] wins"),
        }

        for p in s.players:
            dom = ", ".join(c.name for c in p.domain) or "*(empty)*"
            s.log(f"**{p.name}** — {len(p.domain)} cards")
            s.log(f"  Domain: {dom}")
            tag_counts: dict[str, int] = {}
            for c in p.domain:
                for tag in c.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            if tag_counts:
                tag_str = ", ".join(f"[{t}]×{n}" for t, n in sorted(tag_counts.items()))
                s.log(f"  Tags: {tag_str}")
            s.log("")

        if s.game_over and s.depleted_pile:
            wc = win_conditions.get(s.depleted_pile)
            if wc:
                win_tag, label = wc
                s.log(f"### Winner\n")
                s.log(f"{label}\n")
                scores = {}
                for p in s.players:
                    scores[p.name] = p.count_tag(win_tag)
                max_score = max(scores.values()) if scores else 0
                winners = [name for name, sc in scores.items() if sc == max_score]
                for p in s.players:
                    marker = " 👑" if scores[p.name] == max_score else ""
                    s.log(f"- **{p.name}**: {scores[p.name]} [{win_tag}]{marker}")
                if len(winners) > 1:
                    s.log(f"\n**Tie between {' and '.join(winners)}!**")
                else:
                    s.log(f"\n**{winners[0]} wins!**")
            else:
                s.log(f"### Game ended — {s.depleted_pile} depleted (no scoring axis defined)")

        piles = ", ".join(f"{d} {s.pile_remaining(d)}" for d in ("claw", "tree", "wheat", "coin", "candle") if d in s.piles)
        s.log(f"\n### Stats")
        s.log(f"Turns: {s.turn_num} | Piles: {piles}")
