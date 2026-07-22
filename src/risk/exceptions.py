"""
Domain exceptions for the AEGIS fixed-time risk module.

This module centralizes every exception related to the validation and
evaluation of fixed-time risk objects.

All exceptions inherit from ``RiskError``, allowing callers to handle either
specific domain failures or every risk-domain error through a single base
exception.
"""


class RiskError(Exception):
    """
    Base exception for all errors raised by the fixed-time risk domain.

    Every domain-specific exception in ``src.risk`` must inherit from this
    class.
    """


class RiskValidationError(RiskError):
    """
    Base exception for invalid values or inconsistent domain objects.

    This exception represents failures detected while constructing or
    validating risk policies, requests, and decisions.
    """


class InvalidRiskPolicyError(RiskValidationError):
    """
    Raised when a fixed-time risk policy contains invalid values.

    Examples include inconsistent stake limits, invalid percentages, a
    negative minimum payout, or an invalid active-contract limit.
    """


class InvalidRiskRequestError(RiskValidationError):
    """
    Raised when a fixed-time risk request contains invalid or inconsistent data.

    Examples include missing operation data, invalid bankroll information,
    unsupported directions, negative exposure, or an invalid expiration.
    """


class InvalidRiskDecisionError(RiskValidationError):
    """
    Raised when a fixed-time risk decision contains inconsistent information.

    Examples include an approved decision containing a rejection reason or a
    rejected decision without an explanatory reason.
    """


class InvalidStakeValueError(RiskValidationError):
    """
    Raised when a stake value is invalid.

    This exception may be used for non-positive stake values or other stake
    inconsistencies detected while validating domain objects.
    """


class InvalidPayoutError(RiskValidationError):
    """
    Raised when a payout value is invalid.

    This exception represents malformed payout values, such as negative values
    or values outside the format accepted by the fixed-time risk domain.
    """


class InvalidExposureError(RiskValidationError):
    """
    Raised when bankroll exposure information is invalid.

    Examples include negative exposure, exposure greater than bankroll equity,
    or an inconsistent exposure percentage.
    """


class InvalidActiveContractsError(RiskValidationError):
    """
    Raised when the active-contract count is invalid.

    Active-contract quantities must always be represented by non-negative
    integer values.
    """


class RiskEvaluationError(RiskError):
    """
    Raised when a risk evaluation cannot be completed.

    This exception is reserved for failures in the evaluation process itself,
    rather than expected policy rejections. A normal risk rejection must be
    represented by ``FixedTimeRiskDecision`` and must not raise an exception.
    """