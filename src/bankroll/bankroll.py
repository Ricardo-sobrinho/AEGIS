"""
AEGIS - Bankroll Engine.

Define o agregado responsável por registrar movimentações financeiras e
manter os saldos da banca para contratos de tempo fixo.

Somente o BankrollEngine pode alterar os saldos disponível e reservado.
O ledger é exposto como uma tupla imutável e cada entrada é uma
BankrollTransaction também imutável.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from src.bankroll.enums import (
    BankrollEntryStatus,
    BankrollTransactionType,
)
from src.bankroll.exceptions import (
    DuplicateBankrollTransactionError,
    InsufficientBankrollBalanceError,
    InvalidBankrollBalanceError,
    InvalidBankrollTransactionError,
    InvalidBankrollTransactionStatusError,
)
from src.bankroll.statistics import BankrollStatistics
from src.bankroll.transaction import BankrollTransaction
from src.bankroll.transaction_factory import BankrollTransactionFactory


ZERO = Decimal("0")


@dataclass(slots=True)
class BankrollEngine:
    """
    Gerencia o estado financeiro da banca.

    O engine recebe ou cria transações válidas, aplica suas consequências
    financeiras de forma atômica e somente então adiciona a entrada ao
    ledger.

    Attributes:
        initial_balance:
            Saldo disponível existente antes da primeira entrada do
            ledger.
    """

    initial_balance: Decimal = ZERO

    _available_balance: Decimal = field(
        init=False,
        repr=False,
    )

    _reserved_balance: Decimal = field(
        init=False,
        repr=False,
    )

    _ledger: tuple[BankrollTransaction, ...] = field(
        init=False,
        repr=False,
        default_factory=tuple,
    )

    _transaction_ids: set[UUID] = field(
        init=False,
        repr=False,
        default_factory=set,
    )

    _reserved_by_contract: dict[UUID, Decimal] = field(
        init=False,
        repr=False,
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        """
        Valida e inicializa os saldos controlados pelo engine.
        """

        self._validate_balance(
            value=self.initial_balance,
            field_name="initial_balance",
        )

        self._available_balance = self.initial_balance
        self._reserved_balance = ZERO

    @property
    def available_balance(self) -> Decimal:
        """
        Retorna o saldo disponível para novas operações.

        Returns:
            Saldo financeiro não comprometido.
        """

        return self._available_balance

    @property
    def reserved_balance(self) -> Decimal:
        """
        Retorna o saldo atualmente reservado.

        Returns:
            Soma das stakes comprometidas em contratos abertos.
        """

        return self._reserved_balance

    @property
    def total_balance(self) -> Decimal:
        """
        Retorna o patrimônio financeiro total da banca.

        Returns:
            Soma do saldo disponível com o saldo reservado.
        """

        return self._available_balance + self._reserved_balance

    @property
    def ledger(self) -> tuple[BankrollTransaction, ...]:
        """
        Retorna uma fotografia imutável do ledger financeiro.

        Returns:
            Tupla contendo todas as transações registradas.
        """

        return self._ledger

    @property
    def statistics(self) -> BankrollStatistics:
        """
        Retorna uma fotografia estatística somente de leitura.

        Returns:
            Estatísticas calculadas a partir do estado atual da banca.
        """

        return BankrollStatistics(
            ledger=self._ledger,
            available_balance=self._available_balance,
            reserved_balance=self._reserved_balance,
        )

    def deposit(
        self,
        amount: Decimal,
        **transaction_data: object,
    ) -> BankrollTransaction:
        """
        Cria e registra um depósito.

        Args:
            amount:
                Valor que será creditado no saldo disponível.

            **transaction_data:
                Dados opcionais aceitos pela TransactionFactory.

        Returns:
            Transação de depósito registrada.
        """

        transaction = BankrollTransactionFactory.create_deposit(
            amount=amount,
            **transaction_data,
        )

        return self.register(transaction)

    def withdraw(
        self,
        amount: Decimal,
        **transaction_data: object,
    ) -> BankrollTransaction:
        """
        Cria e registra um saque.

        Args:
            amount:
                Valor que será retirado do saldo disponível.

            **transaction_data:
                Dados opcionais aceitos pela TransactionFactory.

        Returns:
            Transação de saque registrada.

        Raises:
            InsufficientBankrollBalanceError:
                Quando não houver saldo disponível suficiente.
        """

        transaction = BankrollTransactionFactory.create_withdrawal(
            amount=amount,
            **transaction_data,
        )

        return self.register(transaction)

    def reserve_stake(
        self,
        amount: Decimal,
        contract_id: UUID,
        **transaction_data: object,
    ) -> BankrollTransaction:
        """
        Cria e registra uma reserva de stake.

        A reserva transfere capital do saldo disponível para o saldo
        reservado, sem alterar o patrimônio total da banca.

        Args:
            amount:
                Valor da stake que será reservada.

            contract_id:
                Identificador do contrato associado.

            **transaction_data:
                Dados opcionais aceitos pela TransactionFactory.

        Returns:
            Transação de reserva registrada.

        Raises:
            InsufficientBankrollBalanceError:
                Quando não houver saldo disponível suficiente.
        """

        transaction = BankrollTransactionFactory.reserve_stake(
            amount=amount,
            contract_id=contract_id,
            **transaction_data,
        )

        return self.register(transaction)

    def release_stake(
        self,
        amount: Decimal,
        contract_id: UUID,
        **transaction_data: object,
    ) -> BankrollTransaction:
        """
        Cria e registra a liberação de uma stake.

        A liberação devolve ao saldo disponível uma reserva que não será
        liquidada como WIN, LOSS ou DRAW.

        Args:
            amount:
                Valor reservado que será liberado.

            contract_id:
                Identificador do contrato associado.

            **transaction_data:
                Dados opcionais aceitos pela TransactionFactory.

        Returns:
            Transação de liberação registrada.

        Raises:
            InsufficientBankrollBalanceError:
                Quando o contrato não possuir reserva suficiente.
        """

        transaction = BankrollTransactionFactory.release_stake(
            amount=amount,
            contract_id=contract_id,
            **transaction_data,
        )

        return self.register(transaction)

    def settle_win(
        self,
        amount: Decimal,
        contract_id: UUID,
        **transaction_data: object,
    ) -> BankrollTransaction:
        """
        Cria e registra a liquidação WIN de um contrato.

        Toda a reserva vinculada ao contrato é removida. O valor da
        transação é creditado no saldo disponível.

        Args:
            amount:
                Retorno financeiro total creditado pela liquidação.

            contract_id:
                Identificador do contrato liquidado.

            **transaction_data:
                Dados opcionais aceitos pela TransactionFactory.

        Returns:
            Transação de liquidação WIN registrada.
        """

        transaction = BankrollTransactionFactory.settle_win(
            amount=amount,
            contract_id=contract_id,
            **transaction_data,
        )

        return self.register(transaction)

    def settle_loss(
        self,
        contract_id: UUID,
        **transaction_data: object,
    ) -> BankrollTransaction:
        """
        Cria e registra a liquidação LOSS de um contrato.

        Toda a reserva vinculada ao contrato é removida. Nenhum novo
        débito é aplicado ao saldo disponível, pois a stake já havia
        sido retirada durante a reserva.

        Args:
            contract_id:
                Identificador do contrato liquidado.

            **transaction_data:
                Dados opcionais aceitos pela TransactionFactory.

        Returns:
            Transação de liquidação LOSS registrada.
        """

        transaction = BankrollTransactionFactory.settle_loss(
            contract_id=contract_id,
            **transaction_data,
        )

        return self.register(transaction)

    def settle_draw(
        self,
        amount: Decimal,
        contract_id: UUID,
        **transaction_data: object,
    ) -> BankrollTransaction:
        """
        Cria e registra a liquidação DRAW de um contrato.

        Toda a reserva vinculada ao contrato é removida. O valor
        devolvido pela liquidação é creditado no saldo disponível.

        Args:
            amount:
                Valor devolvido ao saldo disponível.

            contract_id:
                Identificador do contrato liquidado.

            **transaction_data:
                Dados opcionais aceitos pela TransactionFactory.

        Returns:
            Transação de liquidação DRAW registrada.
        """

        transaction = BankrollTransactionFactory.settle_draw(
            amount=amount,
            contract_id=contract_id,
            **transaction_data,
        )

        return self.register(transaction)

    def register(
        self,
        transaction: BankrollTransaction,
    ) -> BankrollTransaction:
        """
        Registra uma transação e aplica seus efeitos financeiros.

        A operação é atômica. Todas as validações e os novos saldos são
        calculados antes da alteração do estado interno.

        Args:
            transaction:
                Transação imutável que será adicionada ao ledger.

        Returns:
            A mesma transação após o registro bem-sucedido.

        Raises:
            InvalidBankrollTransactionError:
                Quando o objeto recebido não é uma transação válida.

            InvalidBankrollTransactionStatusError:
                Quando a transação não possui status REGISTERED.

            DuplicateBankrollTransactionError:
                Quando o identificador já existe no ledger.

            InsufficientBankrollBalanceError:
                Quando a movimentação não pode ser suportada pelos
                saldos atuais.
        """

        self._validate_transaction(transaction)

        (
            next_available_balance,
            next_reserved_balance,
            next_reserved_by_contract,
        ) = self._calculate_next_state(transaction)

        self._available_balance = next_available_balance
        self._reserved_balance = next_reserved_balance
        self._reserved_by_contract = next_reserved_by_contract

        self._ledger = (
            *self._ledger,
            transaction,
        )

        self._transaction_ids.add(
            transaction.transaction_id
        )

        return transaction

    def reserved_for_contract(
        self,
        contract_id: UUID,
    ) -> Decimal:
        """
        Retorna o valor atualmente reservado para um contrato.

        Args:
            contract_id:
                Identificador do contrato consultado.

        Returns:
            Valor reservado ou zero quando não houver reserva.

        Raises:
            InvalidBankrollTransactionError:
                Quando contract_id não for UUID.
        """

        if not isinstance(contract_id, UUID):
            raise InvalidBankrollTransactionError(
                "contract_id deve ser uma instância de UUID"
            )

        return self._reserved_by_contract.get(
            contract_id,
            ZERO,
        )

    def _validate_transaction(
        self,
        transaction: BankrollTransaction,
    ) -> None:
        """
        Valida uma transação antes de qualquer mudança de estado.
        """

        if not isinstance(
            transaction,
            BankrollTransaction,
        ):
            raise InvalidBankrollTransactionError(
                "transaction deve ser uma BankrollTransaction"
            )

        if transaction.status is not BankrollEntryStatus.REGISTERED:
            raise InvalidBankrollTransactionStatusError(
                "apenas transações com status REGISTERED podem ser "
                "registradas"
            )

        if transaction.transaction_id in self._transaction_ids:
            raise DuplicateBankrollTransactionError(
                "transaction_id já existe no ledger"
            )

    def _calculate_next_state(
        self,
        transaction: BankrollTransaction,
    ) -> tuple[
        Decimal,
        Decimal,
        dict[UUID, Decimal],
    ]:
        """
        Calcula o próximo estado financeiro sem alterar o engine.

        Args:
            transaction:
                Transação que será interpretada.

        Returns:
            Tupla contendo:
                - próximo saldo disponível;
                - próximo saldo reservado;
                - próximas reservas por contrato.
        """

        available = self._available_balance
        reserved = self._reserved_balance

        reserved_by_contract = dict(
            self._reserved_by_contract
        )

        transaction_type = transaction.transaction_type

        if transaction_type in {
            BankrollTransactionType.DEPOSIT,
            BankrollTransactionType.CREDIT_ADJUSTMENT,
        }:
            available += transaction.amount

        elif transaction_type in {
            BankrollTransactionType.WITHDRAWAL,
            BankrollTransactionType.DEBIT_ADJUSTMENT,
        }:
            self._ensure_available_balance(
                transaction.amount
            )

            available -= transaction.amount

        elif (
            transaction_type
            is BankrollTransactionType.STAKE_RESERVED
        ):
            contract_id = self._require_contract_id(
                transaction
            )

            self._ensure_available_balance(
                transaction.amount
            )

            available -= transaction.amount
            reserved += transaction.amount

            reserved_by_contract[contract_id] = (
                reserved_by_contract.get(
                    contract_id,
                    ZERO,
                )
                + transaction.amount
            )

        elif (
            transaction_type
            is BankrollTransactionType.STAKE_RELEASED
        ):
            contract_id = self._require_contract_id(
                transaction
            )

            self._ensure_contract_reservation(
                contract_id=contract_id,
                amount=transaction.amount,
                reserved_by_contract=reserved_by_contract,
            )

            available += transaction.amount
            reserved -= transaction.amount

            self._decrease_contract_reservation(
                contract_id=contract_id,
                amount=transaction.amount,
                reserved_by_contract=reserved_by_contract,
            )

        elif transaction_type in {
            BankrollTransactionType.SETTLEMENT_WIN,
            BankrollTransactionType.SETTLEMENT_LOSS,
            BankrollTransactionType.SETTLEMENT_DRAW,
        }:
            contract_id = self._require_contract_id(
                transaction
            )

            contract_reservation = (
                reserved_by_contract.get(
                    contract_id,
                    ZERO,
                )
            )

            if contract_reservation <= ZERO:
                raise InsufficientBankrollBalanceError(
                    "não existe saldo reservado para o contrato"
                )

            reserved -= contract_reservation
            reserved_by_contract.pop(contract_id)

            if transaction_type in {
                BankrollTransactionType.SETTLEMENT_WIN,
                BankrollTransactionType.SETTLEMENT_DRAW,
            }:
                available += transaction.amount

        else:
            raise InvalidBankrollTransactionError(
                "tipo de transação não suportado pelo "
                "BankrollEngine"
            )

        self._validate_calculated_balances(
            available_balance=available,
            reserved_balance=reserved,
        )

        return (
            available,
            reserved,
            reserved_by_contract,
        )

    def _ensure_available_balance(
        self,
        amount: Decimal,
    ) -> None:
        """
        Garante saldo disponível suficiente para um débito.

        Args:
            amount:
                Valor que será debitado.

        Raises:
            InsufficientBankrollBalanceError:
                Quando o saldo disponível for insuficiente.
        """

        if amount > self._available_balance:
            raise InsufficientBankrollBalanceError(
                "saldo disponível insuficiente para a transação"
            )

    @staticmethod
    def _ensure_contract_reservation(
        contract_id: UUID,
        amount: Decimal,
        reserved_by_contract: dict[UUID, Decimal],
    ) -> None:
        """
        Garante reserva suficiente para uma liberação.

        Args:
            contract_id:
                Identificador do contrato.

            amount:
                Valor que será liberado.

            reserved_by_contract:
                Fotografia das reservas atuais.

        Raises:
            InsufficientBankrollBalanceError:
                Quando o contrato não possuir reserva suficiente.
        """

        contract_reservation = reserved_by_contract.get(
            contract_id,
            ZERO,
        )

        if amount > contract_reservation:
            raise InsufficientBankrollBalanceError(
                "saldo reservado insuficiente para o contrato"
            )

    @staticmethod
    def _decrease_contract_reservation(
        contract_id: UUID,
        amount: Decimal,
        reserved_by_contract: dict[UUID, Decimal],
    ) -> None:
        """
        Reduz ou remove a reserva associada a um contrato.

        Args:
            contract_id:
                Identificador do contrato.

            amount:
                Valor que será removido.

            reserved_by_contract:
                Estado calculado das reservas.
        """

        remaining = (
            reserved_by_contract[contract_id]
            - amount
        )

        if remaining == ZERO:
            reserved_by_contract.pop(contract_id)
            return

        reserved_by_contract[contract_id] = remaining

    @staticmethod
    def _require_contract_id(
        transaction: BankrollTransaction,
    ) -> UUID:
        """
        Retorna o contract_id obrigatório da transação.

        Args:
            transaction:
                Transação contratual.

        Returns:
            Identificador do contrato.

        Raises:
            InvalidBankrollTransactionError:
                Quando a transação não possuir contract_id.
        """

        if transaction.contract_id is None:
            raise InvalidBankrollTransactionError(
                "a transação exige contract_id"
            )

        return transaction.contract_id

    @staticmethod
    def _validate_balance(
        value: Decimal,
        field_name: str,
    ) -> None:
        """
        Valida um saldo financeiro informado ao engine.

        Args:
            value:
                Saldo que será validado.

            field_name:
                Nome do campo usado na mensagem de erro.

        Raises:
            InvalidBankrollBalanceError:
                Quando o valor não for Decimal, não for finito ou for
                negativo.
        """

        if not isinstance(value, Decimal):
            raise InvalidBankrollBalanceError(
                f"{field_name} deve ser uma instância de Decimal"
            )

        if not value.is_finite():
            raise InvalidBankrollBalanceError(
                f"{field_name} deve ser um valor finito"
            )

        if value < ZERO:
            raise InvalidBankrollBalanceError(
                f"{field_name} não pode ser negativo"
            )

    @classmethod
    def _validate_calculated_balances(
        cls,
        available_balance: Decimal,
        reserved_balance: Decimal,
    ) -> None:
        """
        Valida os saldos calculados antes de confirmar a transação.

        Args:
            available_balance:
                Próximo saldo disponível.

            reserved_balance:
                Próximo saldo reservado.
        """

        cls._validate_balance(
            value=available_balance,
            field_name="available_balance",
        )

        cls._validate_balance(
            value=reserved_balance,
            field_name="reserved_balance",
        )