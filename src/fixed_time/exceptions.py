"""
AEGIS - Fixed-Time Contract Exceptions

Define as exceções específicas do domínio de contratos de tempo fixo.
"""


class FixedTimeContractError(Exception):
    """
    Exceção base para todos os erros do domínio de contratos
    de tempo fixo.
    """


class InvalidContractStateError(FixedTimeContractError):
    """
    Gerada quando uma transição de estado não é permitida.
    """


class InvalidContractDirectionError(FixedTimeContractError):
    """
    Gerada quando a direção do contrato não é CALL ou PUT.
    """


class InvalidStakeError(FixedTimeContractError):
    """
    Gerada quando a stake informada é inválida.
    """


class InvalidPayoutError(FixedTimeContractError):
    """
    Gerada quando o payout informado é inválido.
    """


class InvalidContractDurationError(FixedTimeContractError):
    """
    Gerada quando a duração do contrato é inválida.
    """


class InvalidContractTimestampError(FixedTimeContractError):
    """
    Gerada quando um horário é inválido ou não possui timezone.
    """


class InvalidContractPriceError(FixedTimeContractError):
    """
    Gerada quando um preço obrigatório é inválido.
    """


class ContractAlreadySettledError(FixedTimeContractError):
    """
    Gerada quando há tentativa de liquidar novamente um contrato.
    """


class ContractNotReadyForSettlementError(FixedTimeContractError):
    """
    Gerada quando o contrato ainda não está pronto para liquidação.
    """


class InvalidOperationalModeError(FixedTimeContractError):
    """
    Gerada quando o modo operacional é inválido.
    """