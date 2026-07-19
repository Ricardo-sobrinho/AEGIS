# RFC-002 — Portfolio and Position Management

- **Status:** Proposed
- **Version:** AEGIS v0.8.0
- **Created:** 2026-07-18
- **Authors:** AEGIS Project
- **Area:** Portfolio, Position Management and Profit Calculation

---

## 1. Summary

This RFC defines the evolution of the AEGIS portfolio architecture for version 0.8.0.

The current portfolio implementation supports:

- opening one position per asset;
- validating available cash;
- closing positions;
- rejecting invalid operations;
- publishing portfolio events.

Version 0.8.0 will expand this architecture to support:

- multiple purchases of the same asset;
- weighted average price calculation;
- partial position closing;
- total position closing;
- realized profit and loss;
- unrealized profit and loss;
- invested value;
- market value;
- total portfolio equity.

The `PortfolioEngine` will remain the only component authorized to modify portfolio and position state.

---

## 2. Motivation

The current AEGIS portfolio implementation allows only one purchase per asset.

When a position already exists, a second purchase is rejected.

Example:

```text
First purchase:
1 BTC at 64,000

Second purchase:
1 BTC at 66,000

Current behavior:
Second purchase rejected