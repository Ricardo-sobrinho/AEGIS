import unittest

from src.core.event_bus import EventBus
from src.execution.events import (
    TRADE_EXECUTED,
    TRADE_REJECTED,
)
from src.models.signal import Signal
from src.portfolio.events import PORTFOLIO_UPDATED
from src.services.portfolio_engine import PortfolioEngine
from src.trading.trade_event import TradeEvent


class ExecutionArchitectureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.event_bus = EventBus()

        self.executed_trades: list[TradeEvent] = []
        self.rejected_events: list[object] = []
        self.portfolio_updates: list[object] = []

        self.event_bus.subscribe(
            TRADE_EXECUTED,
            self._capture_executed_trade,
        )

        self.event_bus.subscribe(
            TRADE_REJECTED,
            self._capture_rejected_trade,
        )

        self.event_bus.subscribe(
            PORTFOLIO_UPDATED,
            self._capture_portfolio_update,
        )

    def _capture_executed_trade(
        self,
        trade: TradeEvent,
    ) -> None:
        self.executed_trades.append(trade)

    def _capture_rejected_trade(
        self,
        event: object,
    ) -> None:
        self.rejected_events.append(event)

    def _capture_portfolio_update(
        self,
        event: object,
    ) -> None:
        self.portfolio_updates.append(event)

    def test_buy_is_executed_when_balance_is_sufficient(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=64000.0,
            quantity=1.0,
        )

        portfolio_engine.handle(trade)

        portfolio = portfolio_engine.portfolio

        self.assertIn(
            "BTCUSDT",
            portfolio.positions,
        )

        position = portfolio.positions["BTCUSDT"]

        self.assertEqual(
            position.quantity,
            1.0,
        )

        self.assertEqual(
            position.average_price,
            64000.0,
        )

        self.assertEqual(
            portfolio.cash,
            36000.0,
        )

        self.assertEqual(
            len(self.executed_trades),
            1,
        )

        self.assertEqual(
            len(self.rejected_events),
            0,
        )

        self.assertEqual(
            len(self.portfolio_updates),
            1,
        )

    def test_buy_is_rejected_when_balance_is_insufficient(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100.0,
        )

        trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=64000.0,
            quantity=1.0,
        )

        portfolio_engine.handle(trade)

        portfolio = portfolio_engine.portfolio

        self.assertNotIn(
            "BTCUSDT",
            portfolio.positions,
        )

        self.assertEqual(
            portfolio.cash,
            100.0,
        )

        self.assertEqual(
            len(self.executed_trades),
            0,
        )

        self.assertEqual(
            len(self.rejected_events),
            1,
        )

        self.assertEqual(
            len(self.portfolio_updates),
            0,
        )

        rejected_event = self.rejected_events[0]

        self.assertEqual(
            rejected_event.trade.symbol,
            "BTCUSDT",
        )

        self.assertEqual(
            rejected_event.reason,
            "Saldo insuficiente para realizar a compra",
        )

    def test_second_buy_is_rejected_when_position_exists(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=200000.0,
        )

        first_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=64000.0,
            quantity=1.0,
        )

        second_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=64100.0,
            quantity=1.0,
        )

        portfolio_engine.handle(first_trade)
        portfolio_engine.handle(second_trade)

        portfolio = portfolio_engine.portfolio
        position = portfolio.positions["BTCUSDT"]

        self.assertEqual(
            position.quantity,
            1.0,
        )

        self.assertEqual(
            position.average_price,
            64000.0,
        )

        self.assertEqual(
            portfolio.cash,
            136000.0,
        )

        self.assertEqual(
            len(self.executed_trades),
            1,
        )

        self.assertEqual(
            len(self.rejected_events),
            1,
        )

        rejected_event = self.rejected_events[0]

        self.assertEqual(
            rejected_event.reason,
            "Já existe uma posição aberta para este ativo",
        )

    def test_sell_closes_existing_position(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        buy_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=64000.0,
            quantity=1.0,
        )

        sell_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=65000.0,
            quantity=1.0,
        )

        portfolio_engine.handle(buy_trade)
        portfolio_engine.handle(sell_trade)

        portfolio = portfolio_engine.portfolio

        self.assertNotIn(
            "BTCUSDT",
            portfolio.positions,
        )

        self.assertEqual(
            portfolio.cash,
            101000.0,
        )

        self.assertEqual(
            len(self.executed_trades),
            2,
        )

        self.assertEqual(
            len(self.rejected_events),
            0,
        )

        self.assertEqual(
            len(self.portfolio_updates),
            2,
        )


if __name__ == "__main__":
    unittest.main()