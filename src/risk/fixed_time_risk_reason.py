"""
Fixed-time risk rejection reasons for the AEGIS risk domain.

This module defines the stable reason codes returned when a fixed-time
operation is rejected by ``FixedTimeRiskManager``.

Reason codes are represented by ``StrEnum`` so they can be:

- compared safely in domain logic and tests;
- serialized naturally in APIs, logs, and events;
- stored without depending on human-readable messages;
- translated by presentation layers without changing the risk domain.
"""

from enum import StrEnum


class FixedTimeRiskReason(StrEnum):
    """
    Stable reason codes for fixed-time risk rejections.

    These values identify which policy rules were violated during an
    evaluation. They are domain identifiers and must not be treated as
    presentation messages.

    The enum values use lowercase snake case to support predictable
    serialization in logs, events, databases, and external interfaces.
    """

    STAKE_BELOW_MINIMUM = "stake_below_minimum"
    STAKE_ABOVE_MAXIMUM = "stake_above_maximum"
    STAKE_PERCENTAGE_ABOVE_MAXIMUM = (
        "stake_percentage_above_maximum"
    )
    PAYOUT_BELOW_MINIMUM = "payout_below_minimum"
    EXPOSURE_PERCENTAGE_ABOVE_MAXIMUM = (
        "exposure_percentage_above_maximum"
    )
    ACTIVE_CONTRACT_LIMIT_REACHED = (
        "active_contract_limit_reached"
    )