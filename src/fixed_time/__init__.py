"""
AEGIS - Fixed-Time Contract Domain

Expõe os principais componentes públicos do domínio de contratos
de tempo fixo.
"""

from src.fixed_time.contract import FixedTimeContract
from src.fixed_time.enums import (
    ContractResult,
    ContractStatus,
    FixedTimeDirection,
    OperationalMode,
)
from src.fixed_time.exceptions import (
    ContractAlreadySettledError,
    ContractNotReadyForSettlementError,
    FixedTimeContractError,
    InvalidContractDirectionError,
    InvalidContractDurationError,
    InvalidContractPriceError,
    InvalidContractStateError,
    InvalidContractTimestampError,
    InvalidOperationalModeError,
    InvalidPayoutError,
    InvalidStakeError,
)
from src.fixed_time.settlement import (
    FixedTimeSettlementCalculator,
    SettlementCalculation,
)
from src.fixed_time.state_machine import (
    FixedTimeContractStateMachine,
)

__all__ = [
    "ContractAlreadySettledError",
    "ContractNotReadyForSettlementError",
    "ContractResult",
    "ContractStatus",
    "FixedTimeContract",
    "FixedTimeContractError",
    "FixedTimeContractStateMachine",
    "FixedTimeDirection",
    "FixedTimeSettlementCalculator",
    "InvalidContractDirectionError",
    "InvalidContractDurationError",
    "InvalidContractPriceError",
    "InvalidContractStateError",
    "InvalidContractTimestampError",
    "InvalidOperationalModeError",
    "InvalidPayoutError",
    "InvalidStakeError",
    "OperationalMode",
    "SettlementCalculation",
]