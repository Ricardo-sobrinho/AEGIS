"""
AEGIS - Fixed-Time Domain Exceptions.

This module defines all domain-specific exceptions related to
fixed-time (binary options / fixed-time contracts) operations.

The purpose of these exceptions is to provide clear, explicit and
type-safe error handling throughout the domain layer.

Infrastructure-specific exceptions (HTTP, WebSocket, database,
authentication, etc.) must NOT be defined here.
"""


class FixedTimeError(Exception):
    """
    Base exception for the fixed-time domain.

    Every exception raised by the fixed-time domain should inherit
    from this class.
    """


class InvalidTradeIntentError(FixedTimeError):
    """
    Raised when a TradeIntent contains invalid or inconsistent data.
    """


class InvalidFixedTimeContractError(FixedTimeError):
    """
    Raised when a FixedTimeContract is invalid.
    """


class InvalidFixedTimeContractTransitionError(FixedTimeError):
    """
    Raised when an invalid state transition is attempted.
    """


class DuplicateFixedTimeContractError(FixedTimeError):
    """
    Raised when attempting to create a contract that already exists.
    """


class FixedTimeContractNotFoundError(FixedTimeError):
    """
    Raised when a contract cannot be found.
    """


class FixedTimeContractAlreadySettledError(FixedTimeError):
    """
    Raised when attempting to settle a contract that has already
    been settled.
    """


class FixedTimeContractSubmissionError(FixedTimeError):
    """
    Raised when a contract cannot be submitted for execution.
    """


class FixedTimeContractResultError(FixedTimeError):
    """
    Raised when an invalid contract result is received or processed.
    """


class FixedTimeContractReconciliationRequiredError(FixedTimeError):
    """
    Raised when the contract enters an unknown external state and
    manual or automatic reconciliation becomes necessary.
    """


class StakeReservationError(FixedTimeError):
    """
    Raised when the BankrollEngine cannot reserve the requested stake.
    """


class RiskApprovalRequiredError(FixedTimeError):
    """
    Raised when execution is attempted without prior risk approval.
    """


class BrokerOperationRejectedError(FixedTimeError):
    """
    Raised when the broker definitively rejects an operation.
    """


class InvalidExecutionModeError(FixedTimeError):
    """
    Raised when an unsupported execution mode is supplied.
    """


class InvalidDirectionError(FixedTimeError):
    """
    Raised when an invalid CALL/PUT direction is supplied.
    """


class InvalidContractDirectionError(InvalidDirectionError):
    """
    Raised when an invalid fixed-time contract direction is supplied.
    """


class InvalidPayoutError(FixedTimeError):
    """
    Raised when the payout value is invalid.
    """


class InvalidStakeError(FixedTimeError):
    """
    Raised when the stake value is invalid.
    """


class InvalidContractPriceError(FixedTimeError):
    """
    Raised when a fixed-time contract price is invalid.
    """


class InvalidExpirationError(FixedTimeError):
    """
    Raised when the expiration time is invalid.
    """


class ContractLifecycleError(FixedTimeError):
    """
    Raised when an operation violates the contract lifecycle.
    """


class DuplicateBrokerReferenceError(FixedTimeError):
    """
    Raised when a duplicated broker reference is detected.
    """


class ContractAlreadySubmittedError(FixedTimeError):
    """
    Raised when attempting to submit an already submitted contract.
    """


class ContractAlreadyAcceptedError(FixedTimeError):
    """
    Raised when attempting to accept an already accepted contract.
    """


class ContractAlreadyExpiredError(FixedTimeError):
    """
    Raised when attempting to expire an already expired contract.
    """


class ContractAlreadyCancelledError(FixedTimeError):
    """
    Raised when attempting to cancel an already cancelled contract.
    """


class ContractAlreadyRejectedError(FixedTimeError):
    """
    Raised when attempting to reject an already rejected contract.
    """