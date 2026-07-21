"""
AEGIS - Bankroll Statistics.

Este módulo fornece uma visão estatística imutável e somente de leitura
sobre o estado financeiro da banca e sobre o ledger de transações.

O BankrollStatistics não possui autorização para:

- criar transações;
- alterar transações;
- modificar saldos;
- reservar stakes;
- liquidar contratos;
- publicar eventos;
- comunicar-se com corretoras.

Sua única responsabilidade é transformar um histórico financeiro
imutável em indicadores determinísticos e reutilizáveis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from types import MappingProxyType
from typing import Iterable, Mapping
from uuid import UUID

from src.bankroll.enums import BankrollTransactionType
from src.bankroll.transaction import BankrollTransaction


ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")


@dataclass(frozen=True, slots=True)
class BankrollStatistics:
    """
    Representa uma fotografia estatística imutável da banca.

    As estatísticas são calculadas a partir de:

    - ledger de transações financeiras;
    - saldo disponível;
    - saldo reservado.

    O ledger recebido é convertido internamente para tuple, impedindo que
    alterações posteriores na coleção original modifiquem esta fotografia.

    Attributes:
        ledger:
            Histórico financeiro utilizado nos cálculos.
        available_balance:
            Saldo atualmente disponível para novas operações.
        reserved_balance:
            Saldo atualmente reservado em contratos abertos.
    """

    ledger: tuple[BankrollTransaction, ...] | Iterable[
        BankrollTransaction
    ] = field(default_factory=tuple)

    available_balance: Decimal = ZERO
    reserved_balance: Decimal = ZERO

    def __post_init__(self) -> None:
        """Normaliza e valida os dados da fotografia estatística."""

        normalized_ledger = self._normalize_ledger(self.ledger)

        self._validate_balance(
            value=self.available_balance,
            field_name="available_balance",
        )
        self._validate_balance(
            value=self.reserved_balance,
            field_name="reserved_balance",
        )

        object.__setattr__(self, "ledger", normalized_ledger)

    @property
    def total_balance(self) -> Decimal:
        """
        Retorna o patrimônio financeiro total da banca.

        O saldo total corresponde à soma entre o saldo disponível e o
        saldo atualmente reservado.

        Returns:
            Saldo total da banca.
        """

        return self.available_balance + self.reserved_balance

    @property
    def total_deposits(self) -> Decimal:
        """
        Retorna o total histórico de depósitos registrados.

        Returns:
            Soma das transações do tipo DEPOSIT.
        """

        return self._sum_amounts_by_type(
            BankrollTransactionType.DEPOSIT
        )

    @property
    def total_withdrawals(self) -> Decimal:
        """
        Retorna o total histórico de saques registrados.

        Returns:
            Soma das transações do tipo WITHDRAWAL.
        """

        return self._sum_amounts_by_type(
            BankrollTransactionType.WITHDRAWAL
        )

    @property
    def total_stake_reserved(self) -> Decimal:
        """
        Retorna o valor histórico de stakes reservadas.

        Esta métrica representa o volume acumulado de capital destinado
        a operações. Ela não representa a exposição atual da banca.

        Para consultar a exposição atual, utilize reserved_balance.

        Returns:
            Soma histórica das reservas de stake.
        """

        return self._sum_amounts_by_type(
            BankrollTransactionType.STAKE_RESERVED
        )

    @property
    def total_stake_released(self) -> Decimal:
        """
        Retorna o total histórico de stakes liberadas.

        Returns:
            Soma das transações do tipo STAKE_RELEASED.
        """

        return self._sum_amounts_by_type(
            BankrollTransactionType.STAKE_RELEASED
        )

    @property
    def total_win_returns(self) -> Decimal:
        """
        Retorna o total creditado em liquidações WIN.

        O valor representa o retorno bruto creditado à banca, incluindo
        a devolução da stake quando esse for o contrato financeiro
        definido pelo adaptador da corretora.

        Returns:
            Soma das liquidações WIN.
        """

        return self._sum_amounts_by_type(
            BankrollTransactionType.SETTLEMENT_WIN
        )

    @property
    def total_draw_returns(self) -> Decimal:
        """
        Retorna o total creditado em liquidações DRAW.

        Returns:
            Soma das liquidações DRAW.
        """

        return self._sum_amounts_by_type(
            BankrollTransactionType.SETTLEMENT_DRAW
        )

    @property
    def total_operations(self) -> int:
        """
        Retorna a quantidade de operações liquidadas.

        Uma operação é considerada concluída quando possui uma transação
        de liquidação WIN, LOSS ou DRAW.

        Returns:
            Quantidade total de liquidações.
        """

        return (
            self.total_wins
            + self.total_losses
            + self.total_draws
        )

    @property
    def total_wins(self) -> int:
        """
        Retorna a quantidade de operações WIN.

        Returns:
            Quantidade de liquidações WIN.
        """

        return self._count_by_type(
            BankrollTransactionType.SETTLEMENT_WIN
        )

    @property
    def total_losses(self) -> int:
        """
        Retorna a quantidade de operações LOSS.

        Returns:
            Quantidade de liquidações LOSS.
        """

        return self._count_by_type(
            BankrollTransactionType.SETTLEMENT_LOSS
        )

    @property
    def total_draws(self) -> int:
        """
        Retorna a quantidade de operações DRAW.

        Returns:
            Quantidade de liquidações DRAW.
        """

        return self._count_by_type(
            BankrollTransactionType.SETTLEMENT_DRAW
        )

    @property
    def win_rate(self) -> Decimal:
        """
        Retorna a taxa percentual de operações WIN.

        DRAW faz parte do total de operações e, portanto, é considerado
        no denominador.

        Returns:
            Percentual de operações WIN entre 0 e 100.
        """

        return self._calculate_rate(
            occurrence_count=self.total_wins,
            total_count=self.total_operations,
        )

    @property
    def loss_rate(self) -> Decimal:
        """
        Retorna a taxa percentual de operações LOSS.

        Returns:
            Percentual de operações LOSS entre 0 e 100.
        """

        return self._calculate_rate(
            occurrence_count=self.total_losses,
            total_count=self.total_operations,
        )

    @property
    def draw_rate(self) -> Decimal:
        """
        Retorna a taxa percentual de operações DRAW.

        Returns:
            Percentual de operações DRAW entre 0 e 100.
        """

        return self._calculate_rate(
            occurrence_count=self.total_draws,
            total_count=self.total_operations,
        )

    @property
    def average_stake(self) -> Decimal:
        """
        Retorna a stake média das operações reservadas.

        Returns:
            Média das transações STAKE_RESERVED ou zero quando não
            existirem reservas.
        """

        stakes = self._stake_reservations

        if not stakes:
            return ZERO

        total = sum(
            (transaction.amount for transaction in stakes),
            start=ZERO,
        )

        return total / Decimal(len(stakes))

    @property
    def max_stake(self) -> Decimal:
        """
        Retorna a maior stake já reservada.

        Returns:
            Maior reserva de stake ou zero quando não houver reservas.
        """

        stakes = self._stake_reservations

        if not stakes:
            return ZERO

        return max(transaction.amount for transaction in stakes)

    @property
    def min_stake(self) -> Decimal:
        """
        Retorna a menor stake já reservada.

        Returns:
            Menor reserva de stake ou zero quando não houver reservas.
        """

        stakes = self._stake_reservations

        if not stakes:
            return ZERO

        return min(transaction.amount for transaction in stakes)

    @property
    def settled_stake(self) -> Decimal:
        """
        Retorna o total de stakes associado a contratos liquidados.

        Cada contrato é contado apenas uma vez, com base na primeira
        liquidação encontrada no ledger.

        Returns:
            Soma das stakes dos contratos liquidados.
        """

        stakes_by_contract = self._stakes_by_contract
        settled_contracts = self._settled_contract_ids

        return sum(
            (
                stakes_by_contract.get(contract_id, ZERO)
                for contract_id in settled_contracts
            ),
            start=ZERO,
        )

    @property
    def realized_profit(self) -> Decimal:
        """
        Calcula o resultado financeiro realizado das operações.

        Regras:

        - WIN:
          retorno creditado menos a stake reservada;
        - LOSS:
          perda integral da stake reservada;
        - DRAW:
          valor devolvido menos a stake reservada.

        Depósitos, saques, reservas, liberações e ajustes administrativos
        não são classificados como lucro operacional de trading.

        Returns:
            Lucro ou prejuízo realizado nas operações liquidadas.
        """

        stakes_by_contract = self._stakes_by_contract
        processed_contracts: set[UUID] = set()
        result = ZERO

        for transaction in self.ledger:
            if transaction.transaction_type not in (
                BankrollTransactionType.SETTLEMENT_WIN,
                BankrollTransactionType.SETTLEMENT_LOSS,
                BankrollTransactionType.SETTLEMENT_DRAW,
            ):
                continue

            contract_id = transaction.contract_id

            if contract_id is None:
                continue

            if contract_id in processed_contracts:
                continue

            stake = stakes_by_contract.get(contract_id, ZERO)

            if (
                transaction.transaction_type
                is BankrollTransactionType.SETTLEMENT_WIN
            ):
                result += transaction.amount - stake

            elif (
                transaction.transaction_type
                is BankrollTransactionType.SETTLEMENT_LOSS
            ):
                result -= stake

            else:
                result += transaction.amount - stake

            processed_contracts.add(contract_id)

        return result

    @property
    def roi(self) -> Decimal:
        """
        Retorna o ROI percentual das operações liquidadas.

        O capital utilizado como base é o total de stakes associado aos
        contratos já liquidados.

        Returns:
            ROI percentual. Retorna zero quando não houver stake
            liquidada.
        """

        capital_used = self.settled_stake

        if capital_used == ZERO:
            return ZERO

        return (
            self.realized_profit
            / capital_used
        ) * ONE_HUNDRED

    @property
    def exposure_rate(self) -> Decimal:
        """
        Retorna a exposição atual da banca em percentual.

        A exposição corresponde à parcela do patrimônio total que está
        atualmente reservada em operações abertas.

        Returns:
            Percentual do saldo total atualmente reservado.
        """

        if self.total_balance == ZERO:
            return ZERO

        return (
            self.reserved_balance
            / self.total_balance
        ) * ONE_HUNDRED

    @property
    def net_cash_flow(self) -> Decimal:
        """
        Retorna o fluxo líquido externo de capital.

        O fluxo líquido considera depósitos e saques, sem misturar
        resultados de trading.

        Returns:
            Total depositado menos total sacado.
        """

        return self.total_deposits - self.total_withdrawals

    @property
    def credit_adjustments(self) -> Decimal:
        """
        Retorna o total de ajustes administrativos de crédito.

        Returns:
            Soma das transações CREDIT_ADJUSTMENT.
        """

        return self._sum_amounts_by_type(
            BankrollTransactionType.CREDIT_ADJUSTMENT
        )

    @property
    def debit_adjustments(self) -> Decimal:
        """
        Retorna o total de ajustes administrativos de débito.

        Returns:
            Soma das transações DEBIT_ADJUSTMENT.
        """

        return self._sum_amounts_by_type(
            BankrollTransactionType.DEBIT_ADJUSTMENT
        )

    @property
    def net_adjustments(self) -> Decimal:
        """
        Retorna o resultado líquido dos ajustes administrativos.

        Returns:
            Créditos de ajuste menos débitos de ajuste.
        """

        return (
            self.credit_adjustments
            - self.debit_adjustments
        )

    @property
    def operations_by_contract(
        self,
    ) -> Mapping[UUID, BankrollTransaction]:
        """
        Retorna as liquidações indexadas por contrato.

        Apenas a primeira liquidação encontrada para cada contrato é
        considerada. O resultado é exposto por meio de um mapping
        somente de leitura.

        Returns:
            Mapeamento imutável entre contract_id e transação de
            liquidação.
        """

        operations: dict[UUID, BankrollTransaction] = {}

        for transaction in self.ledger:
            if transaction.transaction_type not in (
                BankrollTransactionType.SETTLEMENT_WIN,
                BankrollTransactionType.SETTLEMENT_LOSS,
                BankrollTransactionType.SETTLEMENT_DRAW,
            ):
                continue

            contract_id = transaction.contract_id

            if contract_id is None:
                continue

            operations.setdefault(contract_id, transaction)

        return MappingProxyType(operations)

    @property
    def _stake_reservations(
        self,
    ) -> tuple[BankrollTransaction, ...]:
        """Retorna todas as transações de reserva de stake."""

        return tuple(
            transaction
            for transaction in self.ledger
            if (
                transaction.transaction_type
                is BankrollTransactionType.STAKE_RESERVED
            )
        )

    @property
    def _stakes_by_contract(self) -> Mapping[UUID, Decimal]:
        """
        Retorna as stakes acumuladas por contrato.

        O uso de soma permite representar corretamente um contrato que,
        futuramente, possa possuir mais de uma reserva financeira válida.
        """

        stakes: dict[UUID, Decimal] = {}

        for transaction in self._stake_reservations:
            contract_id = transaction.contract_id

            if contract_id is None:
                continue

            stakes[contract_id] = (
                stakes.get(contract_id, ZERO)
                + transaction.amount
            )

        return MappingProxyType(stakes)

    @property
    def _settled_contract_ids(self) -> frozenset[UUID]:
        """Retorna os identificadores únicos dos contratos liquidados."""

        return frozenset(self.operations_by_contract.keys())

    def _sum_amounts_by_type(
        self,
        transaction_type: BankrollTransactionType,
    ) -> Decimal:
        """
        Soma os valores de um tipo específico de transação.

        Args:
            transaction_type:
                Tipo de transação que será agregado.

        Returns:
            Soma dos valores encontrados.
        """

        return sum(
            (
                transaction.amount
                for transaction in self.ledger
                if transaction.transaction_type is transaction_type
            ),
            start=ZERO,
        )

    def _count_by_type(
        self,
        transaction_type: BankrollTransactionType,
    ) -> int:
        """
        Conta as transações de um tipo específico.

        Args:
            transaction_type:
                Tipo de transação que será contado.

        Returns:
            Quantidade de transações encontradas.
        """

        return sum(
            1
            for transaction in self.ledger
            if transaction.transaction_type is transaction_type
        )

    @staticmethod
    def _calculate_rate(
        occurrence_count: int,
        total_count: int,
    ) -> Decimal:
        """
        Calcula uma taxa percentual.

        Args:
            occurrence_count:
                Número de ocorrências.
            total_count:
                Número total de elementos.

        Returns:
            Percentual entre 0 e 100. Retorna zero quando o total for
            igual a zero.
        """

        if total_count == 0:
            return ZERO

        return (
            Decimal(occurrence_count)
            / Decimal(total_count)
        ) * ONE_HUNDRED

    @staticmethod
    def _normalize_ledger(
        ledger: tuple[BankrollTransaction, ...]
        | Iterable[BankrollTransaction],
    ) -> tuple[BankrollTransaction, ...]:
        """
        Converte o ledger para uma tuple imutável e valida seus itens.

        Args:
            ledger:
                Coleção de transações financeiras.

        Returns:
            Ledger normalizado como tuple.

        Raises:
            TypeError:
                Quando ledger não for iterável ou possuir elementos que
                não sejam BankrollTransaction.
        """

        if isinstance(ledger, (str, bytes)):
            raise TypeError(
                "ledger must be an iterable of "
                "BankrollTransaction objects."
            )

        try:
            normalized_ledger = tuple(ledger)
        except TypeError as error:
            raise TypeError(
                "ledger must be an iterable of "
                "BankrollTransaction objects."
            ) from error

        for transaction in normalized_ledger:
            if not isinstance(transaction, BankrollTransaction):
                raise TypeError(
                    "Every ledger item must be a "
                    "BankrollTransaction instance."
                )

        return normalized_ledger

    @staticmethod
    def _validate_balance(
        value: Decimal,
        field_name: str,
    ) -> None:
        """
        Valida um saldo monetário.

        Args:
            value:
                Valor monetário.
            field_name:
                Nome do campo utilizado na mensagem de erro.

        Raises:
            TypeError:
                Quando o valor não for Decimal.
            ValueError:
                Quando o valor não for finito ou for negativo.
        """

        if not isinstance(value, Decimal):
            raise TypeError(
                f"{field_name} must be a Decimal."
            )

        if not value.is_finite():
            raise ValueError(
                f"{field_name} must be finite."
            )

        if value < ZERO:
            raise ValueError(
                f"{field_name} cannot be negative."
            )