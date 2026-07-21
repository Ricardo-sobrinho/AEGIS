from math import isfinite

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
    """
    Application service responsible for portfolio state transitions.

    PortfolioEngine is the only component authorized to create, update,
    or remove positions and to modify the portfolio cash balance and
    realized profit and loss.
    """

    def __init__(
        self,
        event_bus: EventBus,
        initial_balance: float = 100000.0,
    ) -> None:
        if not isfinite(initial_balance):
            raise ValueError(
                "O saldo inicial deve ser um número finito"
            )

        if initial_balance < 0:
            raise ValueError(
                "O saldo inicial não pode ser negativo"
            )

        self.event_bus = event_bus
        self.portfolio = Portfolio(
            cash=initial_balance,
        )

    def handle(
        self,
        trade: TradeEvent,
    ) -> None:
        """
        Process a trade and publish the corresponding events.

        Successful operations publish TRADE_EXECUTED followed by
        PORTFOLIO_UPDATED. Rejected operations publish only
        TRADE_REJECTED.
        """
        normalized_symbol = self._normalize_symbol(
            trade.symbol
        )

        if normalized_symbol is None:
            self._reject_trade(
                trade=trade,
                reason="O símbolo do ativo não pode estar vazio",
            )
            return

        if trade.signal == Signal.BUY:
            executed, reason = self._handle_buy(
                trade=trade,
                symbol=normalized_symbol,
            )

        elif trade.signal == Signal.SELL:
            executed, reason = self._handle_sell(
                trade=trade,
                symbol=normalized_symbol,
            )

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
        symbol: str,
    ) -> tuple[bool, str]:
        validation_error = self._validate_trade_values(
            trade=trade,
            operation_name="compra",
        )

        if validation_error is not None:
            return False, validation_error

        total_cost = trade.quantity * trade.price

        if total_cost > self.portfolio.cash:
            return (
                False,
                "Saldo insuficiente para realizar a compra",
            )

        existing_position = self.portfolio.positions.get(
            symbol
        )

        if existing_position is None:
            self._open_position(
                trade=trade,
                symbol=symbol,
            )
        else:
            self._increase_position(
                position=existing_position,
                trade=trade,
            )

        self.portfolio.cash -= total_cost

        return (
            True,
            "Compra executada com sucesso",
        )

    def _handle_sell(
        self,
        trade: TradeEvent,
        symbol: str,
    ) -> tuple[bool, str]:
        validation_error = self._validate_trade_values(
            trade=trade,
            operation_name="venda",
        )

        if validation_error is not None:
            return False, validation_error

        existing_position = self.portfolio.positions.get(
            symbol
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

        self._reduce_position(
            position=existing_position,
            trade=trade,
            symbol=symbol,
        )

        return (
            True,
            "Venda executada com sucesso",
        )

    def _open_position(
        self,
        trade: TradeEvent,
        symbol: str,
    ) -> None:
        self.portfolio.positions[symbol] = Position(
            symbol=symbol,
            quantity=trade.quantity,
            average_price=trade.price,
            last_price=trade.price,
        )

    def _increase_position(
        self,
        position: Position,
        trade: TradeEvent,
    ) -> None:
        current_invested_value = (
            position.quantity * position.average_price
        )
        additional_invested_value = (
            trade.quantity * trade.price
        )
        updated_quantity = (
            position.quantity + trade.quantity
        )

        updated_average_price = (
            current_invested_value
            + additional_invested_value
        ) / updated_quantity

        position.quantity = updated_quantity
        position.average_price = updated_average_price
        position.last_price = trade.price

    def _reduce_position(
        self,
        position: Position,
        trade: TradeEvent,
        symbol: str,
    ) -> None:
        sale_value = trade.quantity * trade.price

        realized_pnl = (
            trade.price - position.average_price
        ) * trade.quantity

        remaining_quantity = (
            position.quantity - trade.quantity
        )

        self.portfolio.cash += sale_value
        self.portfolio.realized_pnl += realized_pnl

        if remaining_quantity == 0:
            del self.portfolio.positions[symbol]
            return

        position.quantity = remaining_quantity
        position.last_price = trade.price

    @staticmethod
    def _normalize_symbol(
        symbol: str,
    ) -> str | None:
        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            return None

        return normalized_symbol

    @staticmethod
    def _validate_trade_values(
        trade: TradeEvent,
        operation_name: str,
    ) -> str | None:
        if not isfinite(trade.quantity):
            return (
                f"A quantidade da {operation_name} "
                "deve ser um número finito"
            )

        if trade.quantity <= 0:
            return (
                f"A quantidade da {operation_name} "
                "deve ser maior que zero"
            )

        if not isfinite(trade.price):
            return (
                f"O preço da {operation_name} "
                "deve ser um número finito"
            )

        if trade.price <= 0:
            return (
                f"O preço da {operation_name} "
                "deve ser maior que zero"
            )

        return None

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
        print(
            f"Lucro realizado.: "
            f"{self.portfolio.realized_pnl:.2f}"
        )
        print(
            f"Valor investido.: "
            f"{self.portfolio.invested_value:.2f}"
        )
        print(
            f"Valor de mercado: "
            f"{self.portfolio.market_value:.2f}"
        )
        print(
            f"Lucro não realiz: "
            f"{self.portfolio.unrealized_pnl:.2f}"
        )
        print(
            f"Patrimônio......: "
            f"{self.portfolio.equity:.2f}"
        )

        if not self.portfolio.positions:
            print("Posições abertas: nenhuma")
            return

        print("Posições abertas:")

        for position in self.portfolio.positions.values():
            print(
                f"- {position.symbol} | "
                f"Quantidade: {position.quantity} | "
                f"Preço médio: {position.average_price:.2f} | "
                f"Último preço: {position.last_price:.2f} | "
                f"PnL não realizado: "
                f"{position.unrealized_pnl:.2f}"
            )