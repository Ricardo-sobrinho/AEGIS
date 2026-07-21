"""
AEGIS - Fixed-Time Contract Domain Entity

Define a entidade central responsável pelo ciclo de vida de um
contrato de tempo fixo.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from src.fixed_time.enums import (
    ContractResult,
    ContractStatus,
    FixedTimeDirection,
    OperationalMode,
)
from src.fixed_time.exceptions import (
    ContractAlreadySettledError,
    ContractNotReadyForSettlementError,
    InvalidContractDirectionError,
    InvalidContractDurationError,
    InvalidContractPriceError,
    InvalidContractTimestampError,
    InvalidOperationalModeError,
    InvalidPayoutError,
    InvalidStakeError,
)
from src.fixed_time.settlement import FixedTimeSettlementCalculator
from src.fixed_time.state_machine import FixedTimeContractStateMachine


@dataclass(slots=True)
class FixedTimeContract:
    """
    Representa um contrato de tempo fixo.

    A entidade protege as regras de negócio e coordena seu ciclo
    de vida utilizando a máquina de estados e o calculador de
    liquidação do domínio.
    """

    symbol: str
    direction: FixedTimeDirection
    stake: Decimal
    payout: Decimal
    duration: timedelta
    mode: OperationalMode = OperationalMode.PAPER

    contract_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    external_contract_id: str | None = None

    status: ContractStatus = ContractStatus.CREATED
    result: ContractResult | None = None

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    submitted_at: datetime | None = None
    opened_at: datetime | None = None
    expiration_at: datetime | None = None
    expired_at: datetime | None = None
    settled_at: datetime | None = None

    entry_price: Decimal | None = None
    expiration_price: Decimal | None = None

    net_profit: Decimal | None = None
    returned_amount: Decimal | None = None

    failure_reason: str | None = None

    def __post_init__(self) -> None:
        """
        Valida e normaliza os dados iniciais do contrato.
        """

        self.symbol = self._normalize_symbol(self.symbol)

        self._validate_direction(self.direction)
        self._validate_stake(self.stake)
        self._validate_payout(self.payout)
        self._validate_duration(self.duration)
        self._validate_mode(self.mode)
        self._validate_timezone(self.created_at)

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        """
        Normaliza o símbolo do ativo.

        Exemplos:
            btc/usdt -> BTCUSDT
            BTC-USDT -> BTCUSDT
            btc_usdt -> BTCUSDT
        """

        if not isinstance(symbol, str):
            raise ValueError(
                "O símbolo do contrato deve ser uma string."
            )

        normalized_symbol = (
            symbol.strip()
            .upper()
            .replace("/", "")
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
        )

        if not normalized_symbol:
            raise ValueError(
                "O símbolo do contrato não pode estar vazio."
            )

        return normalized_symbol

    @staticmethod
    def _validate_direction(
        direction: FixedTimeDirection,
    ) -> None:
        """
        Valida a direção CALL ou PUT.
        """

        if not isinstance(direction, FixedTimeDirection):
            raise InvalidContractDirectionError(
                "A direção deve ser FixedTimeDirection.CALL "
                "ou FixedTimeDirection.PUT."
            )

    @staticmethod
    def _validate_stake(stake: Decimal) -> None:
        """
        Valida o valor comprometido na operação.
        """

        if not isinstance(stake, Decimal):
            raise InvalidStakeError(
                "A stake deve utilizar Decimal."
            )

        if stake <= Decimal("0"):
            raise InvalidStakeError(
                "A stake deve ser maior que zero."
            )

    @staticmethod
    def _validate_payout(payout: Decimal) -> None:
        """
        Valida o payout líquido.

        Exemplo:
            Decimal("0.80") representa 80%.
        """

        if not isinstance(payout, Decimal):
            raise InvalidPayoutError(
                "O payout deve utilizar Decimal."
            )

        if payout < Decimal("0") or payout > Decimal("1"):
            raise InvalidPayoutError(
                "O payout deve estar entre 0 e 1."
            )

    @staticmethod
    def _validate_duration(duration: timedelta) -> None:
        """
        Valida a duração do contrato.
        """

        if not isinstance(duration, timedelta):
            raise InvalidContractDurationError(
                "A duração deve utilizar datetime.timedelta."
            )

        if duration <= timedelta(0):
            raise InvalidContractDurationError(
                "A duração deve ser maior que zero."
            )

    @staticmethod
    def _validate_mode(mode: OperationalMode) -> None:
        """
        Valida o modo operacional.
        """

        if not isinstance(mode, OperationalMode):
            raise InvalidOperationalModeError(
                "O modo deve ser PAPER, DEMO ou REAL."
            )

    @staticmethod
    def _validate_timezone(timestamp: datetime) -> None:
        """
        Garante que o horário possua timezone explícito.
        """

        if not isinstance(timestamp, datetime):
            raise InvalidContractTimestampError(
                "O timestamp deve utilizar datetime."
            )

        if (
            timestamp.tzinfo is None
            or timestamp.utcoffset() is None
        ):
            raise InvalidContractTimestampError(
                "O timestamp deve possuir timezone explícito."
            )

    @staticmethod
    def _validate_price(
        price: Decimal,
        price_name: str,
    ) -> None:
        """
        Valida preços financeiros.
        """

        if not isinstance(price, Decimal):
            raise InvalidContractPriceError(
                f"{price_name} deve utilizar Decimal."
            )

        if price <= Decimal("0"):
            raise InvalidContractPriceError(
                f"{price_name} deve ser maior que zero."
            )

    @staticmethod
    def _normalize_reason(
        reason: str,
        field_name: str,
    ) -> str:
        """
        Valida e normaliza uma justificativa textual.
        """

        if not isinstance(reason, str):
            raise ValueError(
                f"{field_name} deve ser uma string."
            )

        normalized_reason = reason.strip()

        if not normalized_reason:
            raise ValueError(
                f"{field_name} não pode estar vazio."
            )

        return normalized_reason

    def _transition_to(
        self,
        new_status: ContractStatus,
    ) -> None:
        """
        Solicita uma transição à máquina de estados.
        """

        self.status = FixedTimeContractStateMachine.transition(
            current_status=self.status,
            new_status=new_status,
        )

    def submit(
        self,
        submitted_at: datetime | None = None,
    ) -> None:
        """
        Marca o contrato como enviado para execução.
        """

        timestamp = submitted_at or datetime.now(UTC)

        self._validate_timezone(timestamp)
        self._transition_to(ContractStatus.SUBMITTED)

        self.submitted_at = timestamp

    def open(
        self,
        entry_price: Decimal,
        opened_at: datetime | None = None,
        external_contract_id: str | None = None,
    ) -> None:
        """
        Confirma que o contrato foi aberto.
        """

        timestamp = opened_at or datetime.now(UTC)

        self._validate_price(
            entry_price,
            "O preço de entrada",
        )
        self._validate_timezone(timestamp)

        if external_contract_id is not None:
            external_contract_id = self._normalize_reason(
                external_contract_id,
                "O identificador externo",
            )

        self._transition_to(ContractStatus.OPEN)

        self.entry_price = entry_price
        self.opened_at = timestamp
        self.expiration_at = timestamp + self.duration
        self.external_contract_id = external_contract_id

    def mark_expired(
        self,
        expired_at: datetime | None = None,
    ) -> None:
        """
        Marca que o horário de expiração foi atingido.
        """

        timestamp = expired_at or datetime.now(UTC)

        self._validate_timezone(timestamp)

        if self.expiration_at is None:
            raise InvalidContractTimestampError(
                "O contrato não possui horário de expiração."
            )

        if timestamp < self.expiration_at:
            raise InvalidContractTimestampError(
                "O contrato não pode expirar antes do horário previsto."
            )

        self._transition_to(ContractStatus.EXPIRED)

        self.expired_at = timestamp

    def reject(self, reason: str) -> None:
        """
        Registra a rejeição do contrato.
        """

        normalized_reason = self._normalize_reason(
            reason,
            "O motivo da rejeição",
        )

        self._transition_to(ContractStatus.REJECTED)

        self.failure_reason = normalized_reason

    def cancel(
        self,
        reason: str | None = None,
    ) -> None:
        """
        Cancela um contrato que ainda não foi aberto.
        """

        normalized_reason: str | None = None

        if reason is not None:
            normalized_reason = self._normalize_reason(
                reason,
                "O motivo do cancelamento",
            )

        self._transition_to(ContractStatus.CANCELLED)

        self.failure_reason = normalized_reason

    def fail(self, reason: str) -> None:
        """
        Registra uma falha técnica.

        Uma falha técnica não representa automaticamente uma perda.
        """

        normalized_reason = self._normalize_reason(
            reason,
            "O motivo da falha",
        )

        self._transition_to(ContractStatus.FAILED)

        self.failure_reason = normalized_reason

    def mark_unknown(self, reason: str) -> None:
        """
        Marca o contrato como incerto.

        Utilizado quando a solicitação foi enviada, mas a plataforma
        não confirmou claramente o estado da operação.
        """

        normalized_reason = self._normalize_reason(
            reason,
            "O motivo da incerteza",
        )

        self._transition_to(ContractStatus.UNKNOWN)

        self.failure_reason = normalized_reason

    def begin_reconciliation(self) -> None:
        """
        Inicia a reconciliação de um contrato incerto ou com falha.
        """

        self._transition_to(ContractStatus.RECONCILING)

    def settle(
        self,
        expiration_price: Decimal,
        settled_at: datetime | None = None,
    ) -> ContractResult:
        """
        Liquida o contrato e registra seu resultado financeiro.
        """

        if self.status == ContractStatus.SETTLED:
            raise ContractAlreadySettledError(
                "O contrato já foi liquidado."
            )

        if self.status != ContractStatus.EXPIRED:
            raise ContractNotReadyForSettlementError(
                "Somente contratos expirados podem ser liquidados."
            )

        if self.entry_price is None:
            raise ContractNotReadyForSettlementError(
                "O contrato não possui preço de entrada."
            )

        timestamp = settled_at or datetime.now(UTC)

        self._validate_price(
            expiration_price,
            "O preço de expiração",
        )
        self._validate_timezone(timestamp)

        calculation = FixedTimeSettlementCalculator.calculate(
            direction=self.direction,
            stake=self.stake,
            payout=self.payout,
            entry_price=self.entry_price,
            expiration_price=expiration_price,
        )

        self._transition_to(ContractStatus.SETTLED)

        self.expiration_price = expiration_price
        self.result = calculation.result
        self.net_profit = calculation.net_profit
        self.returned_amount = calculation.returned_amount
        self.settled_at = timestamp

        return calculation.result