"""Game observers — pluggable analytics that hook into the engine."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import GameState, Player, Card


class GameObserver(ABC):
    """Base class for game observers. Override the hooks you care about."""

    def on_game_start(self, state: GameState, strategies: dict | None = None):
        pass

    def on_turn_end(self, state: GameState, player: Player, action=None):
        pass

    def on_card_received(self, state: GameState, player: Player, card: Card):
        pass

    def on_order(self, state: GameState, player: Player, card: Card):
        pass

    def on_event_fired(self, state: GameState, event: str, active_player: Player,
                       cancelled: bool, responder_count: int = 0, scope=None):
        pass

    def on_game_end(self, state: GameState, depleted: str | None, winner: str | None):
        pass

    @abstractmethod
    def report(self) -> str:
        """Return a formatted report string."""
        ...


class CardWinCorrelation(GameObserver):
    """Tracks which cards in domain correlate with winning."""

    def __init__(self):
        self.card_in_winner: dict[str, int] = {}
        self.card_in_loser: dict[str, int] = {}
        self.card_in_any: dict[str, int] = {}
        self.card_by_condition: dict[tuple[str, str], tuple[int, int]] = {}
        self.total_winners = 0
        self.total_losers = 0

    def on_game_end(self, state, depleted, winner):
        if not winner or winner.startswith("Tie"):
            return
        d = depleted or "none"
        for p in state.players:
            is_winner = (p.name == winner)
            seen = set()
            for card in p.domain:
                if card.name in seen:
                    continue
                seen.add(card.name)
                self.card_in_any[card.name] = self.card_in_any.get(card.name, 0) + 1
                if is_winner:
                    self.card_in_winner[card.name] = self.card_in_winner.get(card.name, 0) + 1
                else:
                    self.card_in_loser[card.name] = self.card_in_loser.get(card.name, 0) + 1
                key = (card.name, d)
                prev = self.card_by_condition.get(key, (0, 0))
                if is_winner:
                    self.card_by_condition[key] = (prev[0] + 1, prev[1])
                else:
                    self.card_by_condition[key] = (prev[0], prev[1] + 1)
            if is_winner:
                self.total_winners += 1
            else:
                self.total_losers += 1

    def report(self) -> str:
        if self.total_winners == 0:
            return "No decisive games recorded."
        lines = []
        base_rate = self.total_winners / (self.total_winners + self.total_losers)
        lines.append(f"{'='*70}")
        lines.append(f"CARD-WIN CORRELATION ({self.total_winners} decisive games, ties excluded)")
        lines.append(f"{'='*70}")
        lines.append(f"\n{'Card':<25} {'WinRate':>8} {'InWin':>6} {'InLose':>6} {'Lift':>7} {'Games':>6}")
        lines.append(f"{'-'*25} {'-'*8} {'-'*6} {'-'*6} {'-'*7} {'-'*6}")

        rows = []
        for card_name in self.card_in_any:
            in_win = self.card_in_winner.get(card_name, 0)
            in_lose = self.card_in_loser.get(card_name, 0)
            total = self.card_in_any[card_name]
            win_rate = in_win / total if total > 0 else 0
            lift = win_rate - base_rate
            rows.append((card_name, win_rate, in_win, in_lose, lift, total))

        rows.sort(key=lambda r: r[4], reverse=True)
        for name, wr, iw, il, lift, total in rows:
            lines.append(f"{name:<25} {wr:>7.1%} {iw:>6} {il:>6} {lift:>+7.1%} {total:>6}")

        # Per win-condition breakdown
        conditions = sorted(set(d for _, d in self.card_by_condition if d != "none"))
        for cond in conditions:
            cond_rows = []
            for (cn, d), (wc, lc) in self.card_by_condition.items():
                if d != cond:
                    continue
                total = wc + lc
                if total >= 5:
                    cond_rows.append((cn, wc / total, wc, total))
            cond_rows.sort(key=lambda r: r[1], reverse=True)
            lines.append(f"\n  Top cards when {cond} depletes:")
            for name, wr, wc, total in cond_rows[:8]:
                lines.append(f"    {name:<25} {wr:>6.1%} win ({wc}/{total})")

        return "\n".join(lines)


class OrderStats(GameObserver):
    """Tracks how often each card gets Ordered."""

    def __init__(self):
        self.orders: dict[str, int] = {}
        self.orders_in_wins: dict[str, int] = {}
        self.total_games = 0
        self.total_decisive = 0
        self._game_orders: dict[str, dict[str, int]] = {}  # player → card → count
        self._current_players: list[str] = []

    def on_game_start(self, state, strategies=None):
        self.total_games += 1
        self._game_orders = {p.name: {} for p in state.players}
        self._current_players = [p.name for p in state.players]

    def on_event_fired(self, state, event, active_player, cancelled, responder_count=0, scope=None):
        if event != "Order" or cancelled:
            return
        from state import Card
        card_name = scope.name if isinstance(scope, Card) else str(scope)
        self.orders[card_name] = self.orders.get(card_name, 0) + 1
        pa = self._game_orders.get(active_player.name, {})
        pa[card_name] = pa.get(card_name, 0) + 1
        self._game_orders[active_player.name] = pa

    def on_game_end(self, state, depleted, winner):
        if not winner or winner.startswith("Tie"):
            return
        self.total_decisive += 1
        winner_orders = self._game_orders.get(winner, {})
        for card_name, count in winner_orders.items():
            self.orders_in_wins[card_name] = self.orders_in_wins.get(card_name, 0) + count

    def report(self) -> str:
        if not self.orders:
            return "No orders recorded."
        lines = []
        lines.append(f"{'='*70}")
        lines.append(f"ORDER STATS ({self.total_games} games)")
        lines.append(f"{'='*70}")
        lines.append(f"\n{'Card':<25} {'Total':>7} {'PerGame':>8} {'InWins':>7} {'WinShare':>9}")
        lines.append(f"{'-'*25} {'-'*7} {'-'*8} {'-'*7} {'-'*9}")

        rows = []
        for card_name, count in self.orders.items():
            per_game = count / self.total_games
            in_wins = self.orders_in_wins.get(card_name, 0)
            win_share = in_wins / count if count > 0 else 0
            rows.append((card_name, count, per_game, in_wins, win_share))

        rows.sort(key=lambda r: r[1], reverse=True)
        for name, count, pg, iw, ws in rows:
            lines.append(f"{name:<25} {count:>7} {pg:>8.2f} {iw:>7} {ws:>8.1%}")

        # Never ordered
        from cards import _BEHAVIOR_MAP
        all_cards = set(_BEHAVIOR_MAP.keys())
        never = all_cards - set(self.orders.keys())
        if never:
            lines.append(f"\n  Never ordered: {', '.join(sorted(never))}")

        return "\n".join(lines)


class StrategyWinRate(GameObserver):
    """Tracks win rates per strategy type."""

    def __init__(self):
        self.wins: dict[str, int] = {}     # strategy_label → wins
        self.losses: dict[str, int] = {}   # strategy_label → losses
        self.ties: dict[str, int] = {}     # strategy_label → ties
        self.games: dict[str, int] = {}    # strategy_label → total games
        self._player_labels: dict[str, str] = {}
        self.total_games = 0
        # Per win-condition breakdown: (label, depleted_pile) → wins
        self.wins_by_condition: dict[tuple[str, str], int] = {}
        self.games_by_condition: dict[tuple[str, str], int] = {}

    @staticmethod
    def _label(strategy) -> str:
        return getattr(strategy, "name", type(strategy).__name__)

    def on_game_start(self, state, strategies=None):
        self.total_games += 1
        self._player_labels = {}
        if strategies:
            for name, strat in strategies.items():
                self._player_labels[name] = self._label(strat)

    def on_game_end(self, state, depleted, winner):
        is_tie = winner is None or winner.startswith("Tie")
        d = depleted or "none"
        for name, label in self._player_labels.items():
            self.games[label] = self.games.get(label, 0) + 1
            key = (label, d)
            self.games_by_condition[key] = self.games_by_condition.get(key, 0) + 1
            if is_tie:
                self.ties[label] = self.ties.get(label, 0) + 1
            elif name == winner:
                self.wins[label] = self.wins.get(label, 0) + 1
                self.wins_by_condition[key] = self.wins_by_condition.get(key, 0) + 1
            else:
                self.losses[label] = self.losses.get(label, 0) + 1

    def report(self) -> str:
        if not self.games:
            return "No heuristic data recorded."
        lines = []
        lines.append(f"{'='*70}")
        lines.append(f"STRATEGY WIN RATES ({self.total_games} games)")
        lines.append(f"{'='*70}")
        lines.append(f"\n{'Strategy':<30} {'Wins':>6} {'Losses':>7} {'Ties':>6} "
                     f"{'WinRate':>8} {'Decisive':>9}")
        lines.append(f"{'-'*30} {'-'*6} {'-'*7} {'-'*6} {'-'*8} {'-'*9}")

        rows = []
        for label in sorted(self.games):
            w = self.wins.get(label, 0)
            l = self.losses.get(label, 0)
            t = self.ties.get(label, 0)
            decisive = w + l
            wr = w / decisive if decisive > 0 else 0
            rows.append((label, w, l, t, wr, decisive))

        rows.sort(key=lambda r: r[4], reverse=True)
        for label, w, l, t, wr, decisive in rows:
            lines.append(f"{label:<30} {w:>6} {l:>7} {t:>6} {wr:>7.1%} {decisive:>9}")

        # Expected win rate for reference
        n_players = len(self._player_labels)
        if n_players > 0:
            expected = 1.0 / n_players
            lines.append(f"\n  Expected (random baseline): {expected:.1%}")

        # Per win-condition breakdown
        conditions = sorted(set(d for _, d in self.games_by_condition if d != "none"))
        if conditions:
            labels = sorted(set(l for l, _ in self.games_by_condition))
            lines.append(f"\n  {'Win condition':<15}", )
            for cond in conditions:
                lines.append(f"  {cond + ' depletes':<15} ", )
                for label in labels:
                    key = (label, cond)
                    w = self.wins_by_condition.get(key, 0)
                    g = self.games_by_condition.get(key, 0)
                    if g > 0:
                        wr = w / g
                        lines.append(f"    {label:<28} {w:>5}/{g:<5} ({wr:>5.1%})")

        return "\n".join(lines)


class EventFrequency(GameObserver):
    """Tracks event frequency, cancellations, and responder counts."""

    def __init__(self):
        self.event_count: dict[str, int] = {}
        self.event_cancelled: dict[str, int] = {}
        self.event_responders: dict[str, int] = {}  # total responder count per event
        self.total_games = 0
        self._game_events: dict[str, int] = {}

    def on_game_start(self, state, strategies=None):
        self.total_games += 1
        self._game_events = {}

    def on_event_fired(self, state, event, triggerer, cancelled,
                       responder_count=0, scope=None):
        self.event_count[event] = self.event_count.get(event, 0) + 1
        if cancelled:
            self.event_cancelled[event] = self.event_cancelled.get(event, 0) + 1
        self.event_responders[event] = self.event_responders.get(event, 0) + responder_count
        self._game_events[event] = self._game_events.get(event, 0) + 1

    def report(self) -> str:
        if not self.event_count:
            return "No events recorded."
        lines = []
        lines.append(f"{'='*70}")
        lines.append(f"EVENT FREQUENCY ({self.total_games} games)")
        lines.append(f"{'='*70}")
        lines.append(f"\n{'Event':<15} {'Total':>7} {'PerGame':>8} {'Cancelled':>10} "
                     f"{'CancelRate':>11} {'AvgResp':>8}")
        lines.append(f"{'-'*15} {'-'*7} {'-'*8} {'-'*10} {'-'*11} {'-'*8}")

        for event in sorted(self.event_count, key=lambda e: self.event_count[e], reverse=True):
            count = self.event_count[event]
            per_game = count / self.total_games
            cancelled = self.event_cancelled.get(event, 0)
            cancel_rate = cancelled / count if count > 0 else 0
            total_resp = self.event_responders.get(event, 0)
            avg_resp = total_resp / count if count > 0 else 0
            lines.append(f"{event:<15} {count:>7} {per_game:>8.1f} {cancelled:>10} "
                         f"{cancel_rate:>10.1%} {avg_resp:>8.2f}")

        return "\n".join(lines)


class GameLength(GameObserver):
    """Tracks game length distribution (turns and wall-clock time) by win condition."""

    def __init__(self):
        self.total_games = 0
        self.lengths: list[int] = []
        self.durations: list[float] = []
        self.lengths_by_pile: dict[str, list[int]] = {}
        self.durations_by_pile: dict[str, list[float]] = {}
        self.timeouts = 0
        self._game_start: float = 0

    def on_game_start(self, state, strategies=None):
        import time
        self._game_start = time.perf_counter()

    def on_game_end(self, state, depleted, winner):
        import time
        elapsed = time.perf_counter() - self._game_start
        self.total_games += 1
        turns = state.turn_num
        self.lengths.append(turns)
        self.durations.append(elapsed)
        pile = depleted or "timeout"
        if pile == "timeout":
            self.timeouts += 1
        self.lengths_by_pile.setdefault(pile, []).append(turns)
        self.durations_by_pile.setdefault(pile, []).append(elapsed)

    def _fmt_time(self, secs):
        if secs < 0.001:
            return f"{secs*1_000_000:.0f}µs"
        if secs < 1:
            return f"{secs*1000:.1f}ms"
        return f"{secs:.2f}s"

    def report(self) -> str:
        if not self.lengths:
            return "No games recorded."
        lines = [
            "=" * 70,
            f"GAME LENGTH ({self.total_games} games)",
            "=" * 70,
            "",
        ]
        avg = sum(self.lengths) / len(self.lengths)
        mn, mx = min(self.lengths), max(self.lengths)
        s = sorted(self.lengths)
        med = s[len(s) // 2]
        p25 = s[len(s) // 4]
        p75 = s[3 * len(s) // 4]
        avg_t = sum(self.durations) / len(self.durations)
        total_t = sum(self.durations)
        lines.append(f"Turns:  avg {avg:.1f} | median {med} | "
                     f"p25 {p25} | p75 {p75} | min {mn} | max {mx}")
        lines.append(f"Time:   avg {self._fmt_time(avg_t)} | "
                     f"total {self._fmt_time(total_t)}")
        if self.timeouts:
            lines.append(f"Timeouts: {self.timeouts} ({100*self.timeouts/self.total_games:.1f}%)")
        lines.append("")
        lines.append(f"{'Pile':<15} {'Games':>5} {'AvgT':>6} {'Med':>5} {'Min':>5} {'Max':>5} {'AvgTime':>9}")
        lines.append("-" * 58)
        for pile in sorted(self.lengths_by_pile, key=lambda p: -len(self.lengths_by_pile[p])):
            ls = self.lengths_by_pile[pile]
            ds = self.durations_by_pile[pile]
            a = sum(ls) / len(ls)
            sl = sorted(ls)
            m = sl[len(sl) // 2]
            at = sum(ds) / len(ds)
            lines.append(f"{pile:<15} {len(ls):>5} {a:>6.1f} {m:>5} {min(ls):>5} {max(ls):>5} {self._fmt_time(at):>9}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        result = {
            "total_games": self.total_games,
            "avg_turns": round(sum(self.lengths) / len(self.lengths), 1) if self.lengths else 0,
            "median_turns": sorted(self.lengths)[len(self.lengths) // 2] if self.lengths else 0,
            "min_turns": min(self.lengths) if self.lengths else 0,
            "max_turns": max(self.lengths) if self.lengths else 0,
            "avg_time": round(sum(self.durations) / len(self.durations), 4) if self.durations else 0,
            "total_time": round(sum(self.durations), 3) if self.durations else 0,
            "timeouts": self.timeouts,
            "by_pile": {},
        }
        for pile, ls in self.lengths_by_pile.items():
            sl = sorted(ls)
            ds = self.durations_by_pile[pile]
            result["by_pile"][pile] = {
                "games": len(ls),
                "avg_turns": round(sum(ls) / len(ls), 1),
                "median_turns": sl[len(sl) // 2],
                "min_turns": min(ls),
                "max_turns": max(ls),
                "avg_time": round(sum(ds) / len(ds), 4),
            }
        return result
