from src.core.event_bus import EventBus
from src.execution.event_data import TradeRejectedEvent
from src.execution.events import (
    TRADE_EXECUTED,
    TRADE_REJECTED,
)
from src.models.signal import Signal
from src.portfolio.event_data import PortfolioUpdatedEvent
from src.portfolio.events import PORTFOLIO_UPDATED
from src.portfolio.portfolio import Portfolio, Position
from src.trading.trade_event import TradeEvent


class PortfolioEngine:
    def __init__(
        self,
        event_bus: EventBus,
        initial_balance: float = 100000.0,
    ) -> None:
        self.event_bus = event_bus

        self.portfolio = Portfolio(
            cash=initial_balance,
        )

    def handle(
        self,
        trade: TradeEvent,
    ) -> None:
        if trade.signal == Signal.BUY:
            executed, reason = self._handle_buy(trade)

        elif trade.signal == Signal.SELL:
            executed, reason = self._handle_sell(trade)

        else:
            executed = False
            reason = "Sinal de operação desconhecido"

        if not executed:
            self._reject_trade(
                trade=trade,
                reason=reason,
            )
            return

        self._show_portfolio()

        self.event_bus.publish(
            TRADE_EXECUTED,
            trade,
        )

        self.event_bus.publish(
            PORTFOLIO_UPDATED,
            PortfolioUpdatedEvent(
                portfolio=self.portfolio,
            ),
        )

    def _handle_buy(
        self,
        trade: TradeEvent,
    ) -> tuple[bool, str]:
        if trade.quantity <= 0:
            return (
                False,
                "A quantidade da compra deve ser maior que zero",
            )

        if trade.price <= 0:
            return (
                False,
                "O preço da compra deve ser maior que zero",
            )

        total_cost = trade.quantity * trade.price

        if total_cost > self.portfolio.cash:
            return (
                False,
                "Saldo insuficiente para realizar a compra",
            )

        existing_position = self.portfolio.positions.get(
            trade.symbol
        )

        if existing_position is not None:
            return (
                False,
                "Já existe uma posição aberta para este ativo",
            )

        self.portfolio.positions[trade.symbol] = Position(
            symbol=trade.symbol,
            quantity=trade.quantity,
            average_price=trade.price,
        )

        self.portfolio.cash -= total_cost

        return (
            True,
            "Compra executada com sucesso",
        )

    def _handle_sell(
        self,
        trade: TradeEvent,
    ) -> tuple[bool, str]:
        if trade.quantity <= 0:
            return (
                False,
                "A quantidade da venda deve ser maior que zero",
            )

        if trade.price <= 0:
            return (
                False,
                "O preço da venda deve ser maior que zero",
            )

        existing_position = self.portfolio.positions.get(
            trade.symbol
        )

        if existing_position is None:
            return (
                False,
                "Não existe posição aberta para venda",
            )

        if trade.quantity > existing_position.quantity:
            return (
                False,
                "Quantidade de venda maior que a posição atual",
            )

        sale_value = trade.quantity * trade.price

        existing_position.quantity -= trade.quantity
        self.portfolio.cash += sale_value

        if existing_position.quantity <= 0:
            del self.portfolio.positions[trade.symbol]

        return (
            True,
            "Venda executada com sucesso",
        )

    def _reject_trade(
        self,
        trade: TradeEvent,
        reason: str,
    ) -> None:
        print()
        print("❌ Ordem rejeitada")
        print("----------------------------")
        print(f"Ativo...........: {trade.symbol}")
        print(f"Operação........: {trade.signal.value}")
        print(f"Motivo..........: {reason}")

        self.event_bus.publish(
            TRADE_REJECTED,
            TradeRejectedEvent(
                trade=trade,
                reason=reason,
            ),
        )

    def _show_portfolio(self) -> None:
        print()
        print("💰 Portfolio")
        print("----------------------------")
        print(
            f"Saldo disponível: "
            f"{self.portfolio.cash:.2f}"
        )

        if not self.portfolio.positions:
            print("Posições abertas: nenhuma")
            return

        print("Posições abertas:")

        for position in self.portfolio.positions.values():
            print(
                f"- {position.symbol} | "
                f"Quantidade: {position.quantity} | "
                f"Preço médio: "
                f"{position.average_price:.2f}"
            )