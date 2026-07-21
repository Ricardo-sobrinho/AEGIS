"""
AEGIS - Bankroll Transaction Factory.

Centraliza a criação de transações financeiras válidas do domínio
Bankroll.

A factory define a combinação correta entre tipo e direção contábil,
gera identificadores únicos, utiliza timestamps UTC e mantém as
transações inicialmente com o status REGISTERED.

A factory não altera saldos. A interpretação das transações e a
atualização dos saldos disponível, reservado e total pertencem
exclusivamente ao BankrollEngine.
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.bankroll.enums import (
    BankrollEntryStatus,
    BankrollTransactionDirection,
    BankrollTransactionType,
)
from src.bankroll.exceptions import (
    IncompatibleBankrollTransactionDirectionError,
    InvalidBankrollTransactionReferenceError,
)
from src.bankroll.transaction import BankrollTransaction


class BankrollTransactionFactory:
    """
    Cria transações financeiras válidas para o ledger da banca.

    Cada método público representa uma operação autorizada pelo domínio.
    A compatibilidade entre o tipo da transação e sua direção contábil
    é garantida pela factory.

    A factory não mantém estado e não atualiza os saldos da banca.
    """

    _EXPECTED_DIRECTIONS: dict[
        BankrollTransactionType,
        BankrollTransactionDirection,
    ] = {
        BankrollTransactionType.DEPOSIT:
            BankrollTransactionDirection.CREDIT,
        BankrollTransactionType.WITHDRAWAL:
            BankrollTransactionDirection.DEBIT,
        BankrollTransactionType.STAKE_RESERVED:
            BankrollTransactionDirection.DEBIT,
        BankrollTransactionType.STAKE_RELEASED:
            BankrollTransactionDirection.CREDIT,
        BankrollTransactionType.SETTLEMENT_WIN:
            BankrollTransactionDirection.CREDIT,
        BankrollTransactionType.SETTLEMENT_LOSS:
            BankrollTransactionDirection.NEUTRAL,
        BankrollTransactionType.SETTLEMENT_DRAW:
            BankrollTransactionDirection.CREDIT,
        BankrollTransactionType.CREDIT_ADJUSTMENT:
            BankrollTransactionDirection.CREDIT,
        BankrollTransactionType.DEBIT_ADJUSTMENT:
            BankrollTransactionDirection.DEBIT,
    }

    @staticmethod
    def create_deposit(
        amount: Decimal,
        *,
        description: str | None = None,
        reference: str | None = None,
        transaction_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> BankrollTransaction:
        """
        Cria uma transação de depósito.

        Args:
            amount:
                Valor que será creditado na banca.

            description:
                Descrição opcional da movimentação.

            reference:
                Referência externa opcional.

            transaction_id:
                Identificador opcional da transação. Quando omitido,
                um novo UUID será gerado.

            created_at:
                Data e hora opcional da transação. Quando omitida,
                será utilizado o horário UTC atual.

        Returns:
            Transação de depósito registrada.
        """

        return BankrollTransactionFactory._create(
            transaction_type=BankrollTransactionType.DEPOSIT,
            direction=BankrollTransactionDirection.CREDIT,
            amount=amount,
            description=description,
            reference=reference,
            transaction_id=transaction_id,
            created_at=created_at,
        )

    @staticmethod
    def create_withdrawal(
        amount: Decimal,
        *,
        description: str | None = None,
        reference: str | None = None,
        transaction_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> BankrollTransaction:
        """
        Cria uma transação de saque.

        A verificação de saldo disponível não pertence à factory.
        Essa validação deverá ser executada pelo BankrollEngine.

        Args:
            amount:
                Valor que será debitado da banca.

            description:
                Descrição opcional da movimentação.

            reference:
                Referência externa opcional.

            transaction_id:
                Identificador opcional da transação.

            created_at:
                Data e hora opcional da transação.

        Returns:
            Transação de saque registrada.
        """

        return BankrollTransactionFactory._create(
            transaction_type=BankrollTransactionType.WITHDRAWAL,
            direction=BankrollTransactionDirection.DEBIT,
            amount=amount,
            description=description,
            reference=reference,
            transaction_id=transaction_id,
            created_at=created_at,
        )

    @staticmethod
    def reserve_stake(
        amount: Decimal,
        contract_id: UUID,
        *,
        description: str | None = None,
        reference: str | None = None,
        transaction_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> BankrollTransaction:
        """
        Cria uma transação de reserva de stake.

        A reserva retira o valor do saldo disponível. O BankrollEngine
        deverá transferir esse valor para o saldo reservado.

        Args:
            amount:
                Valor da stake que será reservada.

            contract_id:
                Identificador do contrato relacionado à reserva.

            description:
                Descrição opcional da movimentação.

            reference:
                Referência externa opcional.

            transaction_id:
                Identificador opcional da transação.

            created_at:
                Data e hora opcional da transação.

        Returns:
            Transação de reserva de stake registrada.
        """

        validated_contract_id = (
            BankrollTransactionFactory._validate_required_contract_id(
                contract_id
            )
        )

        return BankrollTransactionFactory._create(
            transaction_type=BankrollTransactionType.STAKE_RESERVED,
            direction=BankrollTransactionDirection.DEBIT,
            amount=amount,
            contract_id=validated_contract_id,
            description=description,
            reference=reference,
            transaction_id=transaction_id,
            created_at=created_at,
        )

    @staticmethod
    def release_stake(
        amount: Decimal,
        contract_id: UUID,
        *,
        description: str | None = None,
        reference: str | None = None,
        transaction_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> BankrollTransaction:
        """
        Cria uma transação de liberação de stake.

        Essa operação devolve ao saldo disponível uma stake previamente
        reservada sem liquidar o contrato como WIN, LOSS ou DRAW.

        Args:
            amount:
                Valor da stake que será liberada.

            contract_id:
                Identificador do contrato relacionado à liberação.

            description:
                Descrição opcional da movimentação.

            reference:
                Referência externa opcional.

            transaction_id:
                Identificador opcional da transação.

            created_at:
                Data e hora opcional da transação.

        Returns:
            Transação de liberação de stake registrada.
        """

        validated_contract_id = (
            BankrollTransactionFactory._validate_required_contract_id(
                contract_id
            )
        )

        return BankrollTransactionFactory._create(
            transaction_type=BankrollTransactionType.STAKE_RELEASED,
            direction=BankrollTransactionDirection.CREDIT,
            amount=amount,
            contract_id=validated_contract_id,
            description=description,
            reference=reference,
            transaction_id=transaction_id,
            created_at=created_at,
        )

    @staticmethod
    def settle_win(
        amount: Decimal,
        contract_id: UUID,
        *,
        description: str | None = None,
        reference: str | None = None,
        transaction_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> BankrollTransaction:
        """
        Cria uma transação de liquidação com resultado WIN.

        O valor deve representar o retorno financeiro total creditado
        pela plataforma, normalmente composto pela stake devolvida mais
        o lucro da operação.

        Exemplo:
            Stake:
                100.00

            Payout:
                80%

            Retorno total:
                180.00

            amount:
                Decimal("180.00")

        Args:
            amount:
                Retorno total creditado após o resultado WIN.

            contract_id:
                Identificador do contrato liquidado.

            description:
                Descrição opcional da liquidação.

            reference:
                Referência externa opcional.

            transaction_id:
                Identificador opcional da transação.

            created_at:
                Data e hora opcional da transação.

        Returns:
            Transação de liquidação WIN registrada.
        """

        validated_contract_id = (
            BankrollTransactionFactory._validate_required_contract_id(
                contract_id
            )
        )

        return BankrollTransactionFactory._create(
            transaction_type=BankrollTransactionType.SETTLEMENT_WIN,
            direction=BankrollTransactionDirection.CREDIT,
            amount=amount,
            contract_id=validated_contract_id,
            description=description,
            reference=reference,
            transaction_id=transaction_id,
            created_at=created_at,
        )

    @staticmethod
    def settle_loss(
        contract_id: UUID,
        *,
        description: str | None = None,
        reference: str | None = None,
        transaction_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> BankrollTransaction:
        """
        Cria uma transação de liquidação com resultado LOSS.

        O valor financeiro da stake já foi retirado do saldo disponível
        durante a reserva. Por isso, a liquidação LOSS é uma entrada
        neutra com valor zero.

        O BankrollEngine deverá identificar a stake vinculada ao
        contrato e removê-la do saldo reservado, sem realizar um novo
        débito no saldo disponível.

        Args:
            contract_id:
                Identificador do contrato liquidado.

            description:
                Descrição opcional da liquidação.

            reference:
                Referência externa opcional.

            transaction_id:
                Identificador opcional da transação.

            created_at:
                Data e hora opcional da transação.

        Returns:
            Transação de liquidação LOSS registrada.
        """

        validated_contract_id = (
            BankrollTransactionFactory._validate_required_contract_id(
                contract_id
            )
        )

        return BankrollTransactionFactory._create(
            transaction_type=BankrollTransactionType.SETTLEMENT_LOSS,
            direction=BankrollTransactionDirection.NEUTRAL,
            amount=Decimal("0"),
            contract_id=validated_contract_id,
            description=description,
            reference=reference,
            transaction_id=transaction_id,
            created_at=created_at,
        )

    @staticmethod
    def settle_draw(
        amount: Decimal,
        contract_id: UUID,
        *,
        description: str | None = None,
        reference: str | None = None,
        transaction_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> BankrollTransaction:
        """
        Cria uma transação de liquidação com resultado DRAW.

        Em um empate, o valor normalmente corresponde à devolução
        integral da stake reservada.

        Args:
            amount:
                Valor devolvido ao saldo disponível.

            contract_id:
                Identificador do contrato liquidado.

            description:
                Descrição opcional da liquidação.

            reference:
                Referência externa opcional.

            transaction_id:
                Identificador opcional da transação.

            created_at:
                Data e hora opcional da transação.

        Returns:
            Transação de liquidação DRAW registrada.
        """

        validated_contract_id = (
            BankrollTransactionFactory._validate_required_contract_id(
                contract_id
            )
        )

        return BankrollTransactionFactory._create(
            transaction_type=BankrollTransactionType.SETTLEMENT_DRAW,
            direction=BankrollTransactionDirection.CREDIT,
            amount=amount,
            contract_id=validated_contract_id,
            description=description,
            reference=reference,
            transaction_id=transaction_id,
            created_at=created_at,
        )

    @staticmethod
    def _create(
        transaction_type: BankrollTransactionType,
        direction: BankrollTransactionDirection,
        amount: Decimal,
        *,
        contract_id: UUID | None = None,
        description: str | None = None,
        reference: str | None = None,
        transaction_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> BankrollTransaction:
        """
        Cria internamente uma transação financeira.

        Antes de instanciar a entidade, valida se a direção contábil
        corresponde ao tipo da transação.

        Args:
            transaction_type:
                Tipo da movimentação.

            direction:
                Direção contábil da movimentação.

            amount:
                Valor absoluto da movimentação.

            contract_id:
                Identificador opcional do contrato.

            description:
                Descrição opcional.

            reference:
                Referência externa opcional.

            transaction_id:
                Identificador opcional da transação.

            created_at:
                Data e hora opcional da transação.

        Returns:
            Entidade BankrollTransaction validada.

        Raises:
            IncompatibleBankrollTransactionDirectionError:
                Quando a direção não for compatível com o tipo.
        """

        BankrollTransactionFactory._validate_direction_compatibility(
            transaction_type=transaction_type,
            direction=direction,
        )

        resolved_transaction_id = (
            BankrollTransactionFactory._resolve_transaction_id(
                transaction_id
            )
        )
        resolved_created_at = (
            BankrollTransactionFactory._resolve_created_at(created_at)
        )

        return BankrollTransaction(
            transaction_type=transaction_type,
            direction=direction,
            amount=amount,
            created_at=resolved_created_at,
            contract_id=contract_id,
            description=description,
            reference=reference,
            transaction_id=resolved_transaction_id,
            status=BankrollEntryStatus.REGISTERED,
        )

    @staticmethod
    def _validate_direction_compatibility(
        transaction_type: BankrollTransactionType,
        direction: BankrollTransactionDirection,
    ) -> None:
        """
        Valida a compatibilidade entre tipo e direção contábil.

        Args:
            transaction_type:
                Tipo da transação.

            direction:
                Direção informada para a transação.

        Raises:
            IncompatibleBankrollTransactionDirectionError:
                Quando a direção não corresponder à regra definida para
                o tipo da movimentação.
        """

        expected_direction = (
            BankrollTransactionFactory._EXPECTED_DIRECTIONS.get(
                transaction_type
            )
        )

        if expected_direction is None:
            return

        if direction is not expected_direction:
            raise IncompatibleBankrollTransactionDirectionError(
                "direção incompatível com o tipo da transação: "
                f"{transaction_type.value} exige "
                f"{expected_direction.value}, mas recebeu "
                f"{direction.value}"
            )

    @staticmethod
    def _validate_required_contract_id(contract_id: UUID) -> UUID:
        """
        Valida um identificador obrigatório de contrato.

        Args:
            contract_id:
                Identificador que será validado.

        Returns:
            O UUID validado.

        Raises:
            InvalidBankrollTransactionReferenceError:
                Quando contract_id não for UUID.
        """

        if not isinstance(contract_id, UUID):
            raise InvalidBankrollTransactionReferenceError(
                "contract_id deve ser uma instância de UUID"
            )

        return contract_id

    @staticmethod
    def _resolve_transaction_id(
        transaction_id: UUID | None,
    ) -> UUID:
        """
        Retorna o identificador informado ou gera um novo UUID.

        Args:
            transaction_id:
                Identificador opcional da transação.

        Returns:
            UUID informado ou recém-gerado.

        Raises:
            InvalidBankrollTransactionReferenceError:
                Quando o valor informado não for UUID nem None.
        """

        if transaction_id is None:
            return uuid4()

        if not isinstance(transaction_id, UUID):
            raise InvalidBankrollTransactionReferenceError(
                "transaction_id deve ser UUID ou None"
            )

        return transaction_id

    @staticmethod
    def _resolve_created_at(
        created_at: datetime | None,
    ) -> datetime:
        """
        Retorna o timestamp informado ou o horário UTC atual.

        A validação completa do datetime, incluindo a obrigatoriedade
        de timezone, é realizada pela entidade BankrollTransaction.

        Args:
            created_at:
                Timestamp opcional.

        Returns:
            Timestamp informado ou datetime atual em UTC.
        """

        if created_at is None:
            return datetime.now(UTC)

        return created_at