"""
AEGIS - Fixed-Time Contract State Machine

Controla as transições de estado permitidas no ciclo de vida
dos contratos de tempo fixo.
"""

from src.fixed_time.enums import ContractStatus
from src.fixed_time.exceptions import InvalidContractStateError


_ALLOWED_TRANSITIONS: dict[ContractStatus, frozenset[ContractStatus]] = {
    ContractStatus.CREATED: frozenset(
        {
            ContractStatus.SUBMITTED,
            ContractStatus.REJECTED,
            ContractStatus.CANCELLED,
            ContractStatus.FAILED,
        }
    ),
    ContractStatus.SUBMITTED: frozenset(
        {
            ContractStatus.OPEN,
            ContractStatus.REJECTED,
            ContractStatus.FAILED,
            ContractStatus.UNKNOWN,
        }
    ),
    ContractStatus.OPEN: frozenset(
        {
            ContractStatus.EXPIRED,
            ContractStatus.FAILED,
            ContractStatus.UNKNOWN,
        }
    ),
    ContractStatus.EXPIRED: frozenset(
        {
            ContractStatus.SETTLED,
            ContractStatus.FAILED,
            ContractStatus.UNKNOWN,
        }
    ),
    ContractStatus.UNKNOWN: frozenset(
        {
            ContractStatus.RECONCILING,
            ContractStatus.FAILED,
        }
    ),
    ContractStatus.RECONCILING: frozenset(
        {
            ContractStatus.OPEN,
            ContractStatus.EXPIRED,
            ContractStatus.REJECTED,
            ContractStatus.FAILED,
            ContractStatus.UNKNOWN,
        }
    ),
    ContractStatus.FAILED: frozenset(
        {
            ContractStatus.RECONCILING,
        }
    ),
    ContractStatus.SETTLED: frozenset(),
    ContractStatus.REJECTED: frozenset(),
    ContractStatus.CANCELLED: frozenset(),
}


class FixedTimeContractStateMachine:
    """
    Valida e executa transições de estado de contratos de tempo fixo.

    A classe não altera diretamente a entidade. Ela recebe o estado
    atual, valida o próximo estado e retorna o novo estado aprovado.
    """

    @staticmethod
    def transition(
        current_status: ContractStatus,
        new_status: ContractStatus,
    ) -> ContractStatus:
        """
        Valida uma transição e retorna o novo estado.

        Raises:
            InvalidContractStateError:
                Quando a transição solicitada não é permitida.
        """

        if not isinstance(current_status, ContractStatus):
            raise InvalidContractStateError(
                "O estado atual deve ser uma instância de ContractStatus."
            )

        if not isinstance(new_status, ContractStatus):
            raise InvalidContractStateError(
                "O novo estado deve ser uma instância de ContractStatus."
            )

        allowed_statuses = _ALLOWED_TRANSITIONS[current_status]

        if new_status not in allowed_statuses:
            raise InvalidContractStateError(
                "Transição inválida: "
                f"{current_status.value} -> {new_status.value}."
            )

        return new_status

    @staticmethod
    def can_transition(
        current_status: ContractStatus,
        new_status: ContractStatus,
    ) -> bool:
        """
        Informa se uma transição pode ser realizada.
        """

        if not isinstance(current_status, ContractStatus):
            return False

        if not isinstance(new_status, ContractStatus):
            return False

        return new_status in _ALLOWED_TRANSITIONS[current_status]

    @staticmethod
    def allowed_transitions(
        current_status: ContractStatus,
    ) -> frozenset[ContractStatus]:
        """
        Retorna os próximos estados permitidos para o estado atual.
        """

        if not isinstance(current_status, ContractStatus):
            raise InvalidContractStateError(
                "O estado atual deve ser uma instância de ContractStatus."
            )

        return _ALLOWED_TRANSITIONS[current_status]