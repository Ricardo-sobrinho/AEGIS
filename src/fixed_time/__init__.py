"""
AEGIS - Fixed-Time Domain Package.

This package exposes the public API of the Fixed-Time domain,
including entities, value objects, enums, exceptions and services.
"""

from src.fixed_time.contract import FixedTimeContract
from src.fixed_time.enums import (
    ExecutionMode,
    FixedTimeContractResult,
    FixedTimeContractStatus,
    FixedTimeDirection,
)
from src.fixed_time.exceptions import (
    BrokerOperationRejectedError,
    ContractAlreadyAcceptedError,
    ContractAlreadyCancelledError,
    ContractAlreadyExpiredError,
    ContractAlreadyRejectedError,
    ContractAlreadySubmittedError,
    ContractLifecycleError,
    DuplicateBrokerReferenceError,
    DuplicateFixedTimeContractError,
    FixedTimeContractAlreadySettledError,
    FixedTimeContractNotFoundError,
    FixedTimeContractReconciliationRequiredError,
    FixedTimeContractResultError,
    FixedTimeContractSubmissionError,
    FixedTimeError,
    InvalidContractDirectionError,
    InvalidContractPriceError,
    InvalidDirectionError,
    InvalidExecutionModeError,
    InvalidExpirationError,
    InvalidFixedTimeContractError,
    InvalidFixedTimeContractTransitionError,
    InvalidPayoutError,
    InvalidStakeError,
    InvalidTradeIntentError,
    RiskApprovalRequiredError,
    StakeReservationError,
)
from src.fixed_time.settlement import (
    FixedTimeSettlementCalculator,
    SettlementCalculation,
)
from src.fixed_time.trade_intent import TradeIntent

# -------------------------------------------------------------------------
# Backward compatibility aliases
# -------------------------------------------------------------------------

ContractStatus = FixedTimeContractStatus
ContractResult = FixedTimeContractResult

__all__ = [
    "BrokerOperationRejectedError",
    "ContractAlreadyAcceptedError",
    "ContractAlreadyCancelledError",
    "ContractAlreadyExpiredError",
    "ContractAlreadyRejectedError",
    "ContractAlreadySubmittedError",
    "ContractLifecycleError",
    "ContractResult",
    "ContractStatus",
    "DuplicateBrokerReferenceError",
    "DuplicateFixedTimeContractError",
    "ExecutionMode",
    "FixedTimeContract",
    "FixedTimeContractAlreadySettledError",
    "FixedTimeContractNotFoundError",
    "FixedTimeContractReconciliationRequiredError",
    "FixedTimeContractResult",
    "FixedTimeContractResultError",
    "FixedTimeContractStatus",
    "FixedTimeContractSubmissionError",
    "FixedTimeDirection",
    "FixedTimeError",
    "FixedTimeSettlementCalculator",
    "SettlementCalculation",
    "InvalidContractDirectionError",
    "InvalidContractPriceError",
    "InvalidDirectionError",
    "InvalidExecutionModeError",
    "InvalidExpirationError",
    "InvalidFixedTimeContractError",
    "InvalidFixedTimeContractTransitionError",
    "InvalidPayoutError",
    "InvalidStakeError",
    "InvalidTradeIntentError",
    "RiskApprovalRequiredError",
    "StakeReservationError",
    "TradeIntent",
]