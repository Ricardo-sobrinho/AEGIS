"""
AEGIS - Fixed-Time Contract Enums.

Define as enumerações fundamentais do domínio de contratos de tempo
fixo.

Os enums deste módulo representam:

- a direção da operação;
- o estado do ciclo de vida do contrato;
- o resultado financeiro do contrato;
- o modo utilizado para executar a operação.

Este módulo não contém regras financeiras, integração com corretoras
ou alteração de estado da banca.
"""

from enum import StrEnum


class FixedTimeDirection(StrEnum):
    """
    Representa a direção de uma operação de tempo fixo.

    CALL:
        A operação espera que o preço de expiração seja maior que o
        preço de entrada.

    PUT:
        A operação espera que o preço de expiração seja menor que o
        preço de entrada.
    """

    CALL = "CALL"
    PUT = "PUT"


class FixedTimeContractStatus(StrEnum):
    """
    Representa o estado atual de um contrato de tempo fixo.

    O contrato deverá percorrer somente transições explicitamente
    autorizadas pela máquina de estados do domínio.

    CREATED:
        Contrato criado, ainda sem aprovação de risco.

    RISK_APPROVED:
        Operação aprovada pelas políticas de risco.

    STAKE_RESERVED:
        Stake reservada pelo BankrollEngine.

    SUBMITTED:
        Contrato enviado ao adaptador de execução.

    ACCEPTED:
        Contrato aceito pela plataforma ou pelo adaptador paper.

    ACTIVE:
        Contrato ativo e aguardando o horário de expiração.

    EXPIRED:
        Horário de expiração alcançado e resultado disponível para
        processamento.

    SETTLED:
        Resultado processado e liquidação financeira concluída.

    REJECTED:
        Contrato rejeitado pelo risco, plataforma ou adaptador antes
        de sua ativação.

    CANCELLED:
        Contrato cancelado de forma confirmada.

    FAILED:
        O fluxo encontrou uma falha que impediu sua continuação
        normal.
    """

    CREATED = "CREATED"
    RISK_APPROVED = "RISK_APPROVED"
    STAKE_RESERVED = "STAKE_RESERVED"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    SETTLED = "SETTLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class FixedTimeContractResult(StrEnum):
    """
    Representa o resultado de um contrato de tempo fixo.

    PENDING:
        O resultado ainda não foi determinado.

    WIN:
        A previsão direcional foi vencedora.

    LOSS:
        A previsão direcional foi perdedora.

    DRAW:
        O contrato terminou empatado, normalmente quando o preço de
        expiração é igual ao preço de entrada.

    CANCELLED:
        A plataforma confirmou o cancelamento do contrato.

    UNKNOWN:
        Não foi possível determinar o resultado com segurança.
        Contratos com esse resultado exigem reconciliação.
    """

    PENDING = "PENDING"
    WIN = "WIN"
    LOSS = "LOSS"
    DRAW = "DRAW"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"


class ExecutionMode(StrEnum):
    """
    Representa o ambiente utilizado para executar uma operação.

    PAPER:
        Simulação realizada internamente pela AEGIS, sem comunicação
        com uma conta externa.

    DEMO:
        Operação enviada para uma conta demonstrativa oficial de uma
        plataforma.

    REAL:
        Operação enviada para uma conta com recursos financeiros reais.

    O modo de execução não poderá ser alterado silenciosamente durante
    o ciclo de vida de um contrato.
    """

    PAPER = "PAPER"
    DEMO = "DEMO"
    REAL = "REAL"