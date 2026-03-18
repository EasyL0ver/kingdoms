"""Candle deck card behaviors."""
from cards import CardBehavior, CardContext, _register
from strategy import Intent, DecisionContext


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
        s = ctx.state
        # First, claim Revelation via candle zone
        ctx.engine.order_zone(ctx.player, "candle")
        # Then peek deeper — N = players with Religion tags
        faithful_count = sum(1 for p in s.players
                            if any(c.has_tag("Religion") for c in p.domain))
        peek_n = min(faithful_count, s.pile_remaining("candle"))
        if peek_n <= 0:
            return
        peeked = []
        for _ in range(peek_n):
            card = s.draw_from_pile("candle")
            if card:
                peeked.append(card)
        if not peeked:
            return
        s.log(f"  → Clergy peeks {len(peeked)} from candle pile ({faithful_count} faithful)")
        if len(peeked) == 1:
            choice = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, ["keep", "revelation"],
                DecisionContext(event="Order", source="Clergy", intent=Intent.OPTION))
            if choice == "keep":
                ctx.player.add_to_domain(peeked[0], s)
                s.log(f"  → keeps {peeked[0].name}")
            else:
                s.revelation.append(peeked[0])
                s.log(f"  → sets {peeked[0].name} as Revelation")
        else:
            keep = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, peeked,
                DecisionContext(event="Order", source="Clergy", intent=Intent.GAIN))
            peeked.remove(keep)
            ctx.player.add_to_domain(keep, s)
            s.log(f"  → keeps {keep.name}")
            if peeked:
                new_rev = ctx.engine.strat(ctx.player).resolve(
                    s, ctx.player, peeked,
                    DecisionContext(event="Order", source="Clergy", intent=Intent.OPTION))
                peeked.remove(new_rev)
                s.revelation.append(new_rev)
                s.log(f"  → sets {new_rev.name} as Revelation")
            for card in peeked:
                s.log(f"  → exiles {card.name}")


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
        ctx.engine.resolve_event("Brawl", ctx.player, scope=ctx.player, uprising=True)
        return True


@_register
class Penance(CardBehavior):
    name = 'Penance'
    tags = ['Spiritual', 'Religion']
    deck = 'candle'
    def on_dawn(self, ctx):
        s = ctx.state
        # Discard 2 cards
        discardable = [c for c in ctx.player.domain if c is not ctx.card]
        count = min(2, len(discardable))
        if count > 0:
            victims = ctx.engine.strat(ctx.player).resolve_n(
                s, ctx.player, discardable,
                count, count,
                DecisionContext(event="Dawn", source="Penance", intent=Intent.DISCARD))
            for v in victims:
                ctx.player.discard_from_domain(v)
            names = ", ".join(v.name for v in victims)
            s.log(f"  → Penance: {ctx.player.name} discards {names}")
        # Optionally sacrifice Penance
        if ctx.card in ctx.player.domain and ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, [True, False],
                DecisionContext(event="Dawn", source="Penance", intent=Intent.OPTION)):
            ctx.player.discard_from_domain(ctx.card)
            s.log(f"  → Penance sacrificed")


@_register
class Zealot(CardBehavior):
    name = 'Zealot'
    tags = ['Spiritual', 'Religion', 'Mob']
    deck = 'candle'
    def on_brawl(self, ctx):
        # Defensive: cancel brawl if domain has Religion
        if any(c.has_tag("Religion") for c in ctx.player.domain if c is not ctx.card):
            ctx.state.log(f"  → Zealot defends {ctx.player.name}'s domain — Brawl cancelled!")
            ctx.engine.cancel_event()
            return True
        # Offensive: destroy a card from this domain
        destroyable = [c for c in ctx.player.domain if c is not ctx.card]
        if not destroyable:
            return False
        victim = ctx.engine.strat(ctx.player).resolve(
            ctx.state, ctx.player, destroyable,
            DecisionContext(event="Brawl", source="Zealot", intent=Intent.DISCARD))
        ctx.player.discard_from_domain(victim)
        ctx.state.log(f"  → Zealot: discards {victim.name} from {ctx.player.name}")
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
        # Refill Opportunities from coin pile
        coin_zone = ctx.engine.behavior(ctx.state.zone_cards["coin"])
        coin_zone.refill(ctx.state, 3)
        # Choose: trigger 2 Rumours or stay silent
        if ctx.engine.strat(ctx.player).resolve(
                ctx.state, ctx.player, [True, False],
                DecisionContext(event="Order", source="Benefaction", intent=Intent.OPTION)):
            ctx.state.log(f"  → Benefaction: spectacle! Two Rumours spread")
            ctx.engine.resolve_event("Rumour", ctx.player, scope=ctx.state.other_players(ctx.player))
            ctx.engine.resolve_event("Rumour", ctx.player, scope=ctx.state.other_players(ctx.player))
        else:
            ctx.state.log(f"  → Benefaction: silence — no Rumour")


def _global_spiritual_count(state):
    """Count Spiritual tags across ALL players' domains."""
    return sum(1 for p in state.players for c in p.domain if c.has_tag("Spiritual"))


def _worship_power(ctx):
    """Worship scaling: N = global Spiritual count if owner has Clergy, else 1."""
    n = _global_spiritual_count(ctx.state)
    if not ctx.player.has_card("Clergy"):
        return min(1, n)
    return n


@_register
class WorshipOfTheScripture(CardBehavior):
    name = 'Worship of the Scripture'
    tags = ['Spiritual', 'Religion']
    deck = 'candle'
    def on_rite(self, ctx):
        n = _worship_power(ctx)
        if n <= 0 or ctx.state.pile_remaining("candle") <= 0:
            return False
        peek_n = min(n, ctx.state.pile_remaining("candle"))
        peeked = []
        for _ in range(peek_n):
            card = ctx.state.draw_from_pile("candle")
            if card:
                peeked.append(card)
        if not peeked:
            return False
        ctx.state.log(f"  → Worship of the Scripture: {ctx.active_player.name} peeks {len(peeked)} ({n} Spiritual)")
        # Triggerer picks 1 to keep, rest go back
        keep = ctx.engine.strat(ctx.active_player).resolve(
            ctx.state, ctx.active_player, peeked,
            DecisionContext(event="Rite", source="Worship of the Scripture", intent=Intent.GAIN))
        peeked.remove(keep)
        ctx.active_player.add_to_domain(keep, ctx.state)
        ctx.state.log(f"  → keeps {keep.name}")
        # Exile the rest (removed from game)
        for card in peeked:
            ctx.state.log(f"  → exiles {card.name}")
        return True


@_register
class WorshipOfTheRelic(CardBehavior):
    name = 'Worship of the Relic'
    tags = ['Spiritual', 'Religion']
    deck = 'candle'
    def on_rite(self, ctx):
        n = _worship_power(ctx)
        if n <= 0:
            return False
        s = ctx.state
        piles = [d for d in ("claw", "tree", "wheat", "coin", "candle")
                 if s.pile_remaining(d) > 0]
        if not piles:
            return False
        pile = ctx.engine.strat(ctx.player).resolve(
            s, ctx.player, piles,
            DecisionContext(event="Rite", source="Worship of the Relic", intent=Intent.OPTION))
        peek_n = min(n, s.pile_remaining(pile))
        peeked = []
        for _ in range(peek_n):
            card = s.draw_from_pile(pile)
            if card:
                peeked.append(card)
        if not peeked:
            return False
        names = ", ".join(c.name for c in peeked)
        s.log(f"  → Worship of the Relic: {ctx.player.name} peeks {len(peeked)} from {pile}: {names}")
        # May replace Revelation with one of the peeked cards
        if s.revelation:
            replacements = list(peeked)
            chosen = ctx.engine.strat(ctx.player).resolve(
                s, ctx.player, replacements + ["keep current"],
                DecisionContext(event="Rite", source="Worship of the Relic", intent=Intent.OPTION))
            if chosen != "keep current":
                # Exile current Revelation, set chosen as new Revelation
                old_rev = s.revelation.pop(0)
                s.log(f"  → exiles Revelation: {old_rev.name}")
                peeked.remove(chosen)
                s.revelation.append(chosen)
                s.log(f"  → sets {chosen.name} as new Revelation")
        # Return remaining peeked cards to top of pile (reverse order)
        for card in reversed(peeked):
            s.return_to_pile(pile, card)
        return True


@_register
class WorshipOfTheMartyr(CardBehavior):
    name = 'Worship of the Martyr'
    tags = ['Spiritual', 'Religion']
    deck = 'candle'
    def on_rite(self, ctx):
        n = _worship_power(ctx)
        s = ctx.state
        # Triggerer discards up to N of their own cards
        own_discardable = [c for c in ctx.active_player.domain if c is not ctx.card]
        if own_discardable:
            own_count = min(n, len(own_discardable))
            victims = ctx.engine.strat(ctx.active_player).resolve_n(
                s, ctx.active_player, own_discardable,
                0, own_count,
                DecisionContext(event="Rite", source="Worship of the Martyr", intent=Intent.DISCARD))
            for v in victims:
                ctx.active_player.discard_from_domain(v)
            if victims:
                names = ", ".join(v.name for v in victims)
                s.log(f"  → Worship of the Martyr: {ctx.active_player.name} sacrifices {names}")
        # Everyone else discards exactly N (their choice of which)
        for p in s.play_order_from(ctx.active_player):
            if p is ctx.active_player:
                continue
            their_discardable = list(p.domain)
            discard_count = min(n, len(their_discardable))
            if discard_count > 0:
                victims = ctx.engine.strat(p).resolve_n(
                    s, p, their_discardable,
                    discard_count, discard_count,
                    DecisionContext(event="Rite", source="Worship of the Martyr", intent=Intent.DISCARD))
                for v in victims:
                    p.discard_from_domain(v)
                names = ", ".join(v.name for v in victims)
                s.log(f"  → Worship of the Martyr: {p.name} discards {names}")
        return True


@_register
class ProtectTheMeek(CardBehavior):
    name = 'Protect the Meek'
    tags = ['Chivalry']
    deck = 'candle'
    def on_brawl(self, ctx):
        ctx.state.log(f"  → Protect the Meek: the church calls for knights!")
        ctx.engine.order_zone(ctx.player, "sword")
        return True
