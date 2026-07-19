import unittest

from src.core.event_bus import EventBus
from src.execution.event_data import TradeRejectedEvent
from src.execution.events import (
    TRADE_EXECUTED,
    TRADE_REJECTED,
)
from src.models.signal import Signal
from src.portfolio.event_data import PortfolioUpdatedEvent
from src.portfolio.events import PORTFOLIO_UPDATED
from src.services.portfolio_engine import PortfolioEngine
from src.trading.trade_event import TradeEvent


class ExecutionArchitectureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.event_bus = EventBus()

        self.executed_trades: list[TradeEvent] = []
        self.rejected_events: list[TradeRejectedEvent] = []
        self.portfolio_updates: list[PortfolioUpdatedEvent] = []
        self.published_event_names: list[str] = []

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

        self.event_bus.subscribe(
            TRADE_EXECUTED,
            self._capture_trade_executed_event_name,
        )

        self.event_bus.subscribe(
            TRADE_REJECTED,
            self._capture_trade_rejected_event_name,
        )

        self.event_bus.subscribe(
            PORTFOLIO_UPDATED,
            self._capture_portfolio_updated_event_name,
        )

    def _capture_executed_trade(
        self,
        trade: TradeEvent,
    ) -> None:
        self.executed_trades.append(trade)

    def _capture_rejected_trade(
        self,
        event: TradeRejectedEvent,
    ) -> None:
        self.rejected_events.append(event)

    def _capture_portfolio_update(
        self,
        event: PortfolioUpdatedEvent,
    ) -> None:
        self.portfolio_updates.append(event)

    def _capture_trade_executed_event_name(
        self,
        _: TradeEvent,
    ) -> None:
        self.published_event_names.append(
            TRADE_EXECUTED
        )

    def _capture_trade_rejected_event_name(
        self,
        _: TradeRejectedEvent,
    ) -> None:
        self.published_event_names.append(
            TRADE_REJECTED
        )

    def _capture_portfolio_updated_event_name(
        self,
        _: PortfolioUpdatedEvent,
    ) -> None:
        self.published_event_names.append(
            PORTFOLIO_UPDATED
        )

    def test_buy_opens_position_when_balance_is_sufficient(
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
            position.symbol,
            "BTCUSDT",
        )

        self.assertEqual(
            position.quantity,
            1.0,
        )

        self.assertEqual(
            position.average_price,
            64000.0,
        )

        self.assertEqual(
            position.last_price,
            64000.0,
        )

        self.assertEqual(
            portfolio.cash,
            36000.0,
        )

        self.assertEqual(
            portfolio.realized_pnl,
            0.0,
        )

    def test_successful_buy_publishes_expected_events(
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

        self.assertIs(
            self.executed_trades[0],
            trade,
        )

        self.assertIs(
            self.portfolio_updates[0].portfolio,
            portfolio_engine.portfolio,
        )

        self.assertEqual(
            self.published_event_names,
            [
                TRADE_EXECUTED,
                PORTFOLIO_UPDATED,
            ],
        )

    def test_additional_buy_increases_position_quantity(
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
            price=66000.0,
            quantity=1.0,
        )

        portfolio_engine.handle(first_trade)
        portfolio_engine.handle(second_trade)

        portfolio = portfolio_engine.portfolio
        position = portfolio.positions["BTCUSDT"]

        self.assertEqual(
            position.quantity,
            2.0,
        )

        self.assertEqual(
            portfolio.cash,
            70000.0,
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

    def test_additional_buy_calculates_weighted_average_price(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=300000.0,
        )

        first_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=60000.0,
            quantity=1.0,
        )

        second_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=70000.0,
            quantity=2.0,
        )

        portfolio_engine.handle(first_trade)
        portfolio_engine.handle(second_trade)

        position = portfolio_engine.portfolio.positions[
            "BTCUSDT"
        ]

        expected_average_price = (
            (1.0 * 60000.0)
            + (2.0 * 70000.0)
        ) / 3.0

        self.assertEqual(
            position.quantity,
            3.0,
        )

        self.assertAlmostEqual(
            position.average_price,
            expected_average_price,
        )

        self.assertEqual(
            position.last_price,
            70000.0,
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

        self.assertIs(
            rejected_event.trade,
            trade,
        )

        self.assertEqual(
            rejected_event.reason,
            "Saldo insuficiente para realizar a compra",
        )

        self.assertEqual(
            self.published_event_names,
            [
                TRADE_REJECTED,
            ],
        )

    def test_partial_sell_reduces_position_quantity(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        buy_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=50000.0,
            quantity=2.0,
        )

        sell_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=60000.0,
            quantity=0.5,
        )

        portfolio_engine.handle(buy_trade)
        portfolio_engine.handle(sell_trade)

        portfolio = portfolio_engine.portfolio
        position = portfolio.positions["BTCUSDT"]

        self.assertEqual(
            position.quantity,
            1.5,
        )

        self.assertEqual(
            position.average_price,
            50000.0,
        )

        self.assertEqual(
            position.last_price,
            60000.0,
        )

        self.assertEqual(
            portfolio.cash,
            30000.0,
        )

    def test_partial_sell_calculates_realized_profit(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        buy_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=50000.0,
            quantity=2.0,
        )

        sell_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=60000.0,
            quantity=0.5,
        )

        portfolio_engine.handle(buy_trade)
        portfolio_engine.handle(sell_trade)

        portfolio = portfolio_engine.portfolio

        self.assertEqual(
            portfolio.realized_pnl,
            5000.0,
        )

    def test_partial_sell_calculates_realized_loss(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        buy_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=50000.0,
            quantity=2.0,
        )

        sell_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=40000.0,
            quantity=0.5,
        )

        portfolio_engine.handle(buy_trade)
        portfolio_engine.handle(sell_trade)

        portfolio = portfolio_engine.portfolio

        self.assertEqual(
            portfolio.realized_pnl,
            -5000.0,
        )

    def test_total_sell_closes_existing_position(
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
            portfolio.realized_pnl,
            1000.0,
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

    def test_multiple_sales_accumulate_realized_pnl(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        buy_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=50000.0,
            quantity=2.0,
        )

        first_sell_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=60000.0,
            quantity=0.5,
        )

        second_sell_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=55000.0,
            quantity=0.5,
        )

        portfolio_engine.handle(buy_trade)
        portfolio_engine.handle(first_sell_trade)
        portfolio_engine.handle(second_sell_trade)

        portfolio = portfolio_engine.portfolio
        position = portfolio.positions["BTCUSDT"]

        self.assertEqual(
            portfolio.realized_pnl,
            7500.0,
        )

        self.assertEqual(
            position.quantity,
            1.0,
        )

        self.assertEqual(
            position.average_price,
            50000.0,
        )

        self.assertEqual(
            position.last_price,
            55000.0,
        )

    def test_sell_is_rejected_when_position_does_not_exist(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=65000.0,
            quantity=1.0,
        )

        portfolio_engine.handle(trade)

        self.assertEqual(
            portfolio_engine.portfolio.cash,
            100000.0,
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

        self.assertEqual(
            self.rejected_events[0].reason,
            "Não existe posição aberta para venda",
        )

    def test_sell_is_rejected_when_quantity_exceeds_position(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        buy_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=50000.0,
            quantity=1.0,
        )

        invalid_sell_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=60000.0,
            quantity=2.0,
        )

        portfolio_engine.handle(buy_trade)
        portfolio_engine.handle(invalid_sell_trade)

        portfolio = portfolio_engine.portfolio
        position = portfolio.positions["BTCUSDT"]

        self.assertEqual(
            position.quantity,
            1.0,
        )

        self.assertEqual(
            position.average_price,
            50000.0,
        )

        self.assertEqual(
            position.last_price,
            50000.0,
        )

        self.assertEqual(
            portfolio.cash,
            50000.0,
        )

        self.assertEqual(
            portfolio.realized_pnl,
            0.0,
        )

        self.assertEqual(
            len(self.executed_trades),
            1,
        )

        self.assertEqual(
            len(self.rejected_events),
            1,
        )

        self.assertEqual(
            len(self.portfolio_updates),
            1,
        )

        self.assertEqual(
            self.rejected_events[0].reason,
            "Quantidade de venda maior que a posição atual",
        )

    def test_position_financial_properties_are_calculated(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        buy_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=50000.0,
            quantity=2.0,
        )

        partial_sell_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=60000.0,
            quantity=0.5,
        )

        portfolio_engine.handle(buy_trade)
        portfolio_engine.handle(partial_sell_trade)

        position = portfolio_engine.portfolio.positions[
            "BTCUSDT"
        ]

        self.assertEqual(
            position.invested_value,
            75000.0,
        )

        self.assertEqual(
            position.market_value,
            90000.0,
        )

        self.assertEqual(
            position.unrealized_pnl,
            15000.0,
        )

        self.assertEqual(
            position.return_percentage,
            20.0,
        )

    def test_portfolio_financial_properties_are_calculated(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=200000.0,
        )

        bitcoin_buy = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=50000.0,
            quantity=2.0,
        )

        ethereum_buy = TradeEvent(
            symbol="ETHUSDT",
            signal=Signal.BUY,
            price=2000.0,
            quantity=10.0,
        )

        bitcoin_partial_sell = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=60000.0,
            quantity=0.5,
        )

        ethereum_partial_sell = TradeEvent(
            symbol="ETHUSDT",
            signal=Signal.SELL,
            price=2500.0,
            quantity=2.0,
        )

        portfolio_engine.handle(bitcoin_buy)
        portfolio_engine.handle(ethereum_buy)
        portfolio_engine.handle(bitcoin_partial_sell)
        portfolio_engine.handle(ethereum_partial_sell)

        portfolio = portfolio_engine.portfolio

        self.assertEqual(
            portfolio.cash,
            115000.0,
        )

        self.assertEqual(
            portfolio.invested_value,
            91000.0,
        )

        self.assertEqual(
            portfolio.market_value,
            110000.0,
        )

        self.assertEqual(
            portfolio.unrealized_pnl,
            19000.0,
        )

        self.assertEqual(
            portfolio.realized_pnl,
            6000.0,
        )

        self.assertEqual(
            portfolio.equity,
            225000.0,
        )

    def test_zero_buy_quantity_is_rejected(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=50000.0,
            quantity=0.0,
        )

        portfolio_engine.handle(trade)

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

        self.assertEqual(
            self.rejected_events[0].reason,
            "A quantidade da compra deve ser maior que zero",
        )

    def test_zero_sell_price_is_rejected(
        self,
    ) -> None:
        portfolio_engine = PortfolioEngine(
            event_bus=self.event_bus,
            initial_balance=100000.0,
        )

        buy_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.BUY,
            price=50000.0,
            quantity=1.0,
        )

        invalid_sell_trade = TradeEvent(
            symbol="BTCUSDT",
            signal=Signal.SELL,
            price=0.0,
            quantity=0.5,
        )

        portfolio_engine.handle(buy_trade)
        portfolio_engine.handle(invalid_sell_trade)

        position = portfolio_engine.portfolio.positions[
            "BTCUSDT"
        ]

        self.assertEqual(
            position.quantity,
            1.0,
        )

        self.assertEqual(
            portfolio_engine.portfolio.cash,
            50000.0,
        )

        self.assertEqual(
            len(self.executed_trades),
            1,
        )

        self.assertEqual(
            len(self.rejected_events),
            1,
        )

        self.assertEqual(
            len(self.portfolio_updates),
            1,
        )

        self.assertEqual(
            self.rejected_events[0].reason,
            "O preço da venda deve ser maior que zero",
        )

    def test_non_finite_trade_values_are_rejected(
        self,
    ) -> None:
        invalid_trades = [
            TradeEvent(
                symbol="BTCUSDT",
                signal=Signal.BUY,
                price=float("nan"),
                quantity=1.0,
            ),
            TradeEvent(
                symbol="BTCUSDT",
                signal=Signal.BUY,
                price=float("inf"),
                quantity=1.0,
            ),
            TradeEvent(
                symbol="BTCUSDT",
                signal=Signal.BUY,
                price=50000.0,
                quantity=float("nan"),
            ),
            TradeEvent(
                symbol="BTCUSDT",
                signal=Signal.BUY,
                price=50000.0,
                quantity=float("inf"),
            ),
        ]

        for trade in invalid_trades:
            with self.subTest(
                price=trade.price,
                quantity=trade.quantity,
            ):
                event_bus = EventBus()

                rejected_events: list[
                    TradeRejectedEvent
                ] = []

                event_bus.subscribe(
                    TRADE_REJECTED,
                    rejected_events.append,
                )

                portfolio_engine = PortfolioEngine(
                    event_bus=event_bus,
                    initial_balance=100000.0,
                )

                portfolio_engine.handle(trade)

                self.assertEqual(
                    portfolio_engine.portfolio.cash,
                    100000.0,
                )

                self.assertEqual(
                    portfolio_engine.portfolio.positions,
                    {},
                )

                self.assertEqual(
                    len(rejected_events),
                    1,
                )

    def test_negative_initial_balance_raises_value_error(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "O saldo inicial não pode ser negativo",
        ):
            PortfolioEngine(
                event_bus=self.event_bus,
                initial_balance=-1.0,
            )

    def test_non_finite_initial_balance_raises_value_error(
        self,
    ) -> None:
        invalid_balances = [
            float("nan"),
            float("inf"),
            float("-inf"),
        ]

        for invalid_balance in invalid_balances:
            with self.subTest(
                initial_balance=invalid_balance,
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "O saldo inicial deve ser um número finito",
                ):
                    PortfolioEngine(
                        event_bus=self.event_bus,
                        initial_balance=invalid_balance,
                    )


if __name__ == "__main__":
    unittest.main()