# RFC-003 — Performance Analytics

- **Status:** Proposed
- **Version:** AEGIS v0.9.0
- **Created:** 2026-07-19
- **Authors:** AEGIS Project
- **Area:** Performance Analytics
- **Depends on:** RFC-002 — Portfolio Position Management

---

## 1. Summary

This RFC defines the evolution of the AEGIS performance architecture
for version 0.9.0.

The current implementation of `PerformanceEngine` calculates basic
financial information based on portfolio and market updates.

The existing implementation supports:

- current equity calculation;
- unrealized profit and loss calculation;
- total profit and loss calculation;
- return on investment calculation;
- publication of `PERFORMANCE_UPDATED`.

AEGIS v0.9.0 will evolve this architecture to support:

- immutable performance snapshots;
- equity history;
- absolute return;
- percentage return;
- peak equity;
- current drawdown;
- maximum drawdown;
- realized profit and loss visibility;
- unrealized profit and loss visibility;
- total profit and loss;
- deterministic performance calculations.

The `PerformanceEngine` will remain a read-only consumer of portfolio
state.

It must never create, modify, or remove portfolio positions.

---

## 2. Motivation

RFC-002 introduced a reliable portfolio domain model.

The `Portfolio` object now provides:

- cash;
- open positions;
- realized profit and loss;
- invested value;
- market value;
- unrealized profit and loss;
- total equity.

The current `PerformanceEngine` still recalculates some of these values
independently.

Examples include:

```text
market value
unrealized profit and loss
equity