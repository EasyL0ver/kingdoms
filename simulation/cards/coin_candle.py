"""Coin and Candle deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


@_register
class Treasure(CardBehavior):
    name = 'Treasure'
    tags = ['Trophy', 'Amenity', 'Wealth']
    deck = 'coin'


@_register
class Market(CardBehavior):
    name = 'Market'
    tags = []
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        ctx.engine.order_zone(ctx.player, "coin")

    def on_rumour(self, ctx):
        if not ctx.player.domain or not ctx.state.wares:
            return False
        if not ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Rumour", source="Market", intent=Intent.OPTION)):
            return False
        to_trade = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.player.domain),
            DecisionContext(event="Rumour", source="Market", intent=Intent.DISCARD))
        ctx.player.remove_from_domain(to_trade)
        ctx.state.wares.append(to_trade)
        pick = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.state.wares),
            DecisionContext(event="Rumour", source="Market", intent=Intent.GAIN))
        ctx.state.wares.remove(pick)
        ctx.player.add_to_domain(pick, ctx.state)
        ctx.state.log(f"  → Market: {ctx.player.name} trades {to_trade.name} for {pick.name}")
        return True


@_register
class Smuggler(CardBehavior):
    name = 'Smuggler'
    tags = ['Mob']
    deck = 'coin'
    def on_brawl(self, ctx):
        if ctx.target is None:
            return False
        defender = ctx.target
        moveable = [c for c in defender.domain if c is not ctx.card]
        if not moveable:
            return False
        victim = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, moveable,
            DecisionContext(event="Brawl", source="Smuggler", intent=Intent.DISCARD))
        defender.remove_from_domain(victim)
        ctx.state.wares.append(victim)
        ctx.state.log(f"  → Smuggler: {victim.name} from {defender.name} goes to Wares")
        return True

    def on_rumour(self, ctx):
        if ctx.active_player is None or ctx.active_player is ctx.player:
            return False
        ctx.player.remove_from_domain(ctx.card)
        ctx.active_player.add_to_domain(ctx.card, ctx.state)
        ctx.state.log(f"  → Smuggler: moves to {ctx.active_player.name}")
        return True


@_register
class Sellsword(CardBehavior):
    name = 'Sellsword'
    tags = ['Unit']
    deck = 'coin'
    def on_brawl(self, ctx):
        if ctx.target is not ctx.player:
            return False
        if not ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Brawl", source="Sellsword", intent=Intent.OPTION)):
            return False
        ctx.player.remove_from_domain(ctx.card)
        ctx.state.wares.append(ctx.card)
        ctx.state.log(f"  → Sellsword cancels Brawl (goes to Wares)")
        ctx.engine.cancel_event()
        return True


@_register
class Swindle(CardBehavior):
    name = 'Swindle'
    tags = []
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain" or not ctx.state.wares:
            return
        target = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, list(ctx.state.players),
            DecisionContext(event="Order", source="Swindle", intent=Intent.OPTION))
        # Target takes ALL wares
        taken = list(ctx.state.wares)
        for card in taken:
            ctx.state.wares.remove(card)
            target.add_to_domain(card, ctx.state)
        names = ", ".join(c.name for c in taken)
        ctx.state.log(f"  → Swindle: {target.name} takes all Wares ({len(taken)}): {names}")
        # Brawl in their domain
        ctx.state.log(f"  → Swindle: Brawl erupts in {target.name}'s domain!")
        ctx.engine.resolve_event("Brawl", ctx.player, target=target)
        # Self-discard
        ctx.player.discard_from_domain(ctx.card)
        ctx.state.log(f"  → Swindle discarded")


@_register
class Prosperity(CardBehavior):
    name = 'Prosperity'
    tags = ['Wealth']
    deck = 'coin'
    def on_dawn(self, ctx):
        if not ctx.state.wares or ctx.state.pile_remaining("coin") <= 0:
            return
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → Prosperity: {ctx.player.name} draws {drawn[0].name}")


@_register
class Embassy(CardBehavior):
    name = 'Embassy'
    tags = ['Wealth']
    deck = 'coin'
    def on_dawn(self, ctx):
        if not ctx.state.wares:
            return
        for other in ctx.state.other_players(ctx.player):
            if ctx.player.shares_culture(other) and ctx.state.wares:
                # Owner picks from wares
                if ctx.state.wares:
                    pick = ctx.engine.strat(ctx.player).resolve(
                        ctx.state, ctx.player, list(ctx.state.wares),
                        DecisionContext(event="Dawn", source="Embassy", intent=Intent.GAIN))
                    ctx.state.wares.remove(pick)
                    ctx.player.add_to_domain(pick, ctx.state)
                    ctx.state.log(f"  → Embassy: {ctx.player.name} takes {pick.name} from Wares")
                # Ally picks from wares
                if ctx.state.wares:
                    ally_pick = ctx.engine.strat(other).resolve(
                        ctx.state, other, list(ctx.state.wares),
                        DecisionContext(event="Dawn", source="Embassy", intent=Intent.GAIN))
                    ctx.state.wares.remove(ally_pick)
                    other.add_to_domain(ally_pick, ctx.state)
                    ctx.state.log(f"  → Embassy: {other.name} takes {ally_pick.name} from Wares")
                break  # Only one culture ally needed


@_register
class Efficiency(CardBehavior):
    name = 'Efficiency'
    tags = []
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        orderable = [c for c in ctx.player.domain
                     if c is not ctx.card and ctx.engine._has_on_order(c)]
        if not orderable:
            ctx.player.discard_from_domain(ctx.card)
            ctx.state.log(f"  → Efficiency: nothing to order, discarded")
            return
        max_orders = min(4, len(orderable))
        to_order = ctx.engine.strat(ctx.player).resolve_n(
            ctx.state, ctx.player, orderable,
            0, max_orders,
            DecisionContext(event="Order", source="Efficiency", intent=Intent.OPTION))
        for card in to_order:
            if card not in ctx.player.domain:
                continue
            beh = ctx.engine.behavior(card)
            sub_ctx = ctx.engine.make_ctx(ctx.player, card, active_player=ctx.player)
            ctx.state.log(f"  → Efficiency orders {card.name}")
            beh.on_order(sub_ctx)
        ctx.player.discard_from_domain(ctx.card)
        ctx.state.log(f"  → Efficiency discarded")


@_register
class SpiceMarket(CardBehavior):
    name = 'Spice Market'
    tags = ['Wealth']
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        unique_tags = set()
        for c in ctx.player.domain:
            for tag in c.tags:
                unique_tags.add(tag)
        draw_count = min(len(unique_tags), ctx.state.pile_remaining("coin"))
        if draw_count <= 0:
            ctx.state.log(f"  → Spice Market: {len(unique_tags)} unique tags but no coin left")
            return
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin", draw_count)
        names = ", ".join(c.name for c in drawn)
        ctx.state.log(f"  → Spice Market: {len(unique_tags)} unique tags → draws {len(drawn)}: {names}")


@_register
class Commodities(CardBehavior):
    name = 'Commodities'
    tags = []
    deck = 'coin'
    def on_rumour(self, ctx):
        piles = [d for d in ("tree", "claw", "wheat", "coin")
                 if ctx.state.pile_remaining(d) > 0]
        if not piles:
            return False
        pile = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, piles,
            DecisionContext(event="Rumour", source="Commodities", intent=Intent.OPTION))
        card = ctx.state.draw_from_pile(pile)
        if card:
            ctx.state.wares.append(card)
            ctx.state.log(f"  → Commodities: {ctx.player.name} adds {card.name} from {pile} to Wares")
            return True
        return False


@_register
class Mine(CardBehavior):
    name = 'Mine'
    tags = ['Labour']
    deck = 'coin'
    def on_order(self, ctx):
        if ctx.location != "domain" or ctx.state.pile_remaining("coin") <= 0:
            return
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → Mine draws {drawn[0].name} from Coin")

    def on_dawn(self, ctx):
        if not ctx.player.has_card("Crags"):
            ctx.state.log(f"  → Dawn: no Crags → Mine to discard")
            ctx.player.discard.append(ctx.card)


@_register
class Provisions(CardBehavior):
    name = 'Provisions'
    tags = ['Amenity']
    deck = 'coin'
    def on_feast(self, ctx):
        if ctx.state.pile_remaining("coin") <= 0:
            return False
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → Provisions: {ctx.player.name} draws {drawn[0].name} from Coin")
            return True
        return False


@_register
class WorshipOfGold(CardBehavior):
    name = 'Worship of Gold'
    tags = ['Spiritual']
    deck = 'coin'
    def on_rite(self, ctx):
        if not ctx.state.wares:
            return False
        pick = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, list(ctx.state.wares),
            DecisionContext(event="Rite", source="Worship of Gold", intent=Intent.GAIN))
        ctx.state.wares.remove(pick)
        ctx.active_player.add_to_domain(pick, ctx.state)
        ctx.state.log(f"  → Worship of Gold: {ctx.active_player.name} takes {pick.name} from Wares")
        return True


@_register
class Ornament(CardBehavior):
    name = 'Ornament'
    tags = ['Religion']
    deck = 'candle'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        s = ctx.state
        if not s.revelation:
            s.log(f"  → Ornament: no Revelation to sell")
            return
        rev_card = s.revelation.pop(0)
        s.wares.append(rev_card)
        s.log(f"  → Ornament: {rev_card.name} moved from Revelation to Wares")
        # Flip next Revelation
        candle_zone = ctx.engine.behavior(s.zone_cards["candle"])
        candle_zone.refill(s)
        if s.revelation:
            s.log(f"  → New Revelation: {s.revelation[0].name}")


@_register
class Clergy(CardBehavior):
    name = 'Clergy'
    tags = ['Religion']
    deck = 'candle'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        ctx.engine.order_zone(ctx.player, "candle")


@_register
class Sabbath(CardBehavior):
    name = 'Sabbath'
    tags = ['Religion']
    deck = 'candle'
    def on_dawn(self, ctx):
        ctx.state.log(f"  → Sabbath: {ctx.player.name} triggers Rite")
        ctx.engine.resolve_event("Rite", ctx.player)


@_register
class Evangelism(CardBehavior):
    name = 'Evangelism'
    tags = ['Religion']
    deck = 'candle'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        s = ctx.state
        candle_zone = ctx.engine.behavior(s.zone_cards["candle"])
        # Each player in turn order claims the current Revelation, then next flips
        for p in s.play_order_from(ctx.player):
            if not s.revelation:
                candle_zone.refill(s)
            if not s.revelation:
                break  # pile exhausted
            rev_card = s.revelation.pop(0)
            p.add_to_domain(rev_card, s)
            s.log(f"  → Evangelism: {p.name} receives {rev_card.name}")
            candle_zone.refill(s)


@_register
class Purity(CardBehavior):
    name = 'Purity'
    tags = ['Religion']
    deck = 'candle'
    def on_order(self, ctx):
        if ctx.location != "domain":
            return
        s = ctx.state
        if not s.revelation:
            return
        # Optionally exile the current Revelation
        if not ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, [True, False],
                DecisionContext(event="Order", source="Purity", intent=Intent.OPTION)):
            return
        exiled = s.revelation.pop(0)
        s.log(f"  → Purity: exiles {exiled.name} from Revelation")
        # Flip new Revelation
        candle_zone = ctx.engine.behavior(s.zone_cards["candle"])
        candle_zone.refill(s)
        if s.revelation:
            s.log(f"  → New Revelation: {s.revelation[0].name}")
        # Trigger Rite
        s.log(f"  → Purity: {ctx.player.name} triggers Rite")
        ctx.engine.resolve_event("Rite", ctx.player)


@_register
class Flagellation(CardBehavior):
    name = 'Flagellation'
    tags = ['Religion']
    deck = 'candle'
    def on_rite(self, ctx):
        ctx.state.log(f"  → Flagellation: {ctx.player.name} brawls themselves!")
        ctx.engine.resolve_event("Brawl", ctx.player, target=ctx.player, uprising=True)
        return True


@_register
class Zealot(CardBehavior):
    name = 'Zealot'
    tags = ['Spiritual', 'Religion', 'Mob']
    deck = 'candle'
    def on_brawl(self, ctx):
        if ctx.target is None:
            return False
        # Defensive: if Zealot's owner is the target and has Religion, cancel brawl
        if ctx.target is ctx.player and any(c.has_tag("Religion") for c in ctx.player.domain if c is not ctx.card):
            ctx.state.log(f"  → Zealot defends {ctx.player.name}'s domain — Brawl cancelled!")
            ctx.engine.cancel_event()
            return True
        # Offensive: destroy a card from the defender's domain
        defender = ctx.target
        destroyable = [c for c in defender.domain if c is not ctx.card]
        if not destroyable:
            return False
        victim = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, destroyable,
            DecisionContext(event="Brawl", source="Zealot", intent=Intent.DISCARD))
        defender.discard_from_domain(victim)
        ctx.state.log(f"  → Zealot: discards {victim.name} from {defender.name}")
        return True

    def on_rite(self, ctx):
        if ctx.active_player is None or ctx.active_player is ctx.player:
            return False
        # Rite triggerer optionally chooses where Zealot moves
        if not ctx.engine.strat(ctx.active_player).resolve(
                ctx.state, ctx.active_player, [True, False],
                DecisionContext(event="Rite", source="Zealot", intent=Intent.OPTION)):
            return False
        targets = [p for p in ctx.state.players if p is not ctx.player]
        if not targets:
            return False
        dest = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, targets,
            DecisionContext(event="Rite", source="Zealot", intent=Intent.OPTION))
        ctx.player.remove_from_domain(ctx.card)
        dest.add_to_domain(ctx.card, ctx.state)
        ctx.state.log(f"  → Zealot: {ctx.active_player.name} sends Zealot to {dest.name}")
        return True


@_register
class Alms(CardBehavior):
    name = 'Alms'
    tags = ['Religion']
    deck = 'candle'
    def on_feast(self, ctx):
        acted = False
        s = ctx.state
        # Refill 1 Field
        zone = s.zone_cards["wheat"]
        old_count = len(s.fields)
        wheat_zone = ctx.engine.behavior(zone)
        wheat_zone.refill(s, old_count + 1)
        if len(s.fields) > old_count:
            s.log(f"  → Alms: refills 1 Field ({s.fields[-1].name})")
            acted = True
        # Return 1 Discontent to claw pile
        discontent = ctx.player.cards_with_tag("Discontent")
        if discontent:
            victim = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, discontent,
                DecisionContext(event="Feast", source="Alms", intent=Intent.DISCARD))
            ctx.player.remove_from_domain(victim)
            s.return_to_pile("claw", victim)
            s.log(f"  → Alms: returns {victim.name} to claw pile")
            acted = True
        return acted


@_register
class Benefaction(CardBehavior):
    name = 'Benefaction'
    tags = ['Religion']
    deck = 'candle'
    def on_order(self, ctx):
        if ctx.location != "domain" or ctx.state.pile_remaining("coin") <= 0:
            return
        drawn = ctx.engine.draw_and_receive(ctx.player, "coin")
        if drawn:
            ctx.state.log(f"  → Benefaction: {ctx.player.name} draws {drawn[0].name} from Coin")
        # Refill wares from coin pile
        from cards.zones import CoinZone
        coin_zone = ctx.engine.behavior(ctx.state.zone_cards["coin"])
        coin_zone.refill(ctx.state)
        # Choose: trigger 2 Rumours or stay silent
        if ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Order", source="Benefaction", intent=Intent.OPTION)):
            ctx.state.log(f"  → Benefaction: spectacle! Two Rumours spread")
            ctx.engine.resolve_event("Rumour", ctx.player, exclude_active=True)
            ctx.engine.resolve_event("Rumour", ctx.player, exclude_active=True)
        else:
            ctx.state.log(f"  → Benefaction: silence — no Rumour")


@_register
class WorshipOfTheFlame(CardBehavior):
    name = 'Worship of the Flame'
    tags = ['Spiritual']
    deck = 'candle'
    def on_rite(self, ctx):
        return True
