from src.core.event_bus import EventBus
from src.market.event_data import CandlesReceivedEvent
from src.performance.event_data import PerformanceUpdatedEvent
from src.performance.events import PERFORMANCE_UPDATED
from src.performance.performance import Performance
from src.portfolio.event_data import PortfolioUpdatedEvent
from src.portfolio.portfolio import Portfolio


class PerformanceEngine:
    def __init__(
        self,
        event_bus: EventBus,
        initial_equity: float = 100000.0,
    ) -> None:
        self.event_bus = event_bus
        self.initial_equity = initial_equity

        self.current_prices: dict[str, float] = {}
        self.portfolio: Portfolio | None = None

    def handle_market_update(
        self,
        event: CandlesReceivedEvent,
    ) -> None:
        if not event.candles:
            return

        latest_candle = event.candles[-1]

        self.current_prices[event.symbol] = float(
            latest_candle.close_price
        )

        if self.portfolio is not None:
            self._calculate_performance()

    def handle_portfolio_update(
        self,
        event: PortfolioUpdatedEvent,
    ) -> None:
        self.portfolio = event.portfolio

        self._calculate_performance()

    def _calculate_performance(self) -> None:
        if self.portfolio is None:
            return

        market_value = 0.0
        unrealized_pnl = 0.0

        for position in self.portfolio.positions.values():
            current_price = self.current_prices.get(
                position.symbol,
                position.average_price,
            )

            position_market_value = (
                position.quantity * current_price
            )

            position_cost = (
                position.quantity
                * position.average_price
            )

            position_pnl = (
                position_market_value
                - position_cost
            )

            market_value += position_market_value
            unrealized_pnl += position_pnl

        equity = self.portfolio.cash + market_value

        total_pnl = equity - self.initial_equity

        roi = (
            total_pnl / self.initial_equity * 100
            if self.initial_equity > 0
            else 0.0
        )

        performance = Performance(
            equity=equity,
            unrealized_pnl=unrealized_pnl,
            roi=roi,
        )

        self._show_performance(
            performance=performance,
            total_pnl=total_pnl,
            market_value=market_value,
        )

        self.event_bus.publish(
            PERFORMANCE_UPDATED,
            PerformanceUpdatedEvent(
                performance=performance,
            ),
        )

    def _show_performance(
        self,
        performance: Performance,
        total_pnl: float,
        market_value: float,
    ) -> None:
        print()
        print("📊 Performance")
        print("----------------------------")
        print(
            f"Valor de mercado: "
            f"{market_value:.2f}"
        )
        print(
            f"Patrimônio......: "
            f"{performance.equity:.2f}"
        )
        print(
            f"PnL não realizado: "
            f"{performance.unrealized_pnl:.2f}"
        )
        print(
            f"PnL total.......: "
            f"{total_pnl:.2f}"
        )
        print(
            f"ROI.............: "
            f"{performance.roi:.4f}%"
        )

        if self.portfolio is None:
            return

        if not self.portfolio.positions:
            print("Posições........: nenhuma")
            return

        print("Posições:")

        for position in self.portfolio.positions.values():
            current_price = self.current_prices.get(
                position.symbol,
                position.average_price,
            )

            position_pnl = (
                current_price
                - position.average_price
            ) * position.quantity

            print(
                f"- {position.symbol} | "
                f"Preço médio: {position.average_price:.2f} | "
                f"Preço atual: {current_price:.2f} | "
                f"PnL: {position_pnl:.2f}"
            )