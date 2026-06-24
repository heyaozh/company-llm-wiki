---
id: con-black76-option-pricing
type: concept
title: "Black-76 Option Pricing Model"
parent: ""
concept_kind: pricing
model: model-black76
status: draft
owner: dl625
version: 2
review_year: 2026
last_reviewed: 2026-06-24
completeness: theory_only
open_questions:
  - "Confirm concept_kind: this is set to `pricing`; switch to `methodology` if your taxonomy classes pricing-model theory there."
  - "Parent framework id is not yet set (which framework this concept sits under)."
  - "Exact index option products and contract specs this model covers are not documented here."
  - "Source/vendor of the volatility, forward and discount-rate inputs is not documented."
  - "How the option value feeds the margin methodology (downstream BR/spec) is not documented."
  - "Verify the theory below against the source PDF and correct any firm-specific conventions."
  - "SharePoint link for the source PDF to be added to source_refs."
source_refs:
  - "black76 option pricing model.pdf (local; upload to SharePoint and replace with the link)"
references:
  - model-black76
tags: [valuation, options, index-options, closed-form]
---

# Black-76 Option Pricing Model

> Verify the theory below against the source PDF and correct any firm-specific conventions
> before marking this note complete.

## Summary
Black-76 (Black, 1976) is the standard closed-form model for European options written on a
**forward or futures price**. It is the forward-measure form of Black–Scholes: because the
underlying is the forward price F, the model needs no separate dividend/carry term. We use it
to value many index options.

## Theory / content
Let F be the forward price of the underlying, K the strike, r the risk-free rate, T the time
to expiry, σ the volatility, and N(·) the standard normal cumulative distribution function.

European call and put values:

$$ C = e^{-rT}\left[\,F\,N(d_1) - K\,N(d_2)\,\right] $$

$$ P = e^{-rT}\left[\,K\,N(-d_2) - F\,N(-d_1)\,\right] $$

with

$$ d_1 = \frac{\ln(F/K) + \tfrac{1}{2}\sigma^2 T}{\sigma\sqrt{T}}, \qquad d_2 = d_1 - \sigma\sqrt{T}. $$

The model assumes the forward price is log-normally distributed at expiry.

## Inputs & data
Requires: forward price F, strike K, time to expiry T, volatility σ, and a discount rate r.
The specific data sources used in our implementation are not documented here (see
open_questions).

## Assumptions & limitations
- European exercise only; no early exercise.
- Constant volatility and interest rate over the life of the option.
- Log-normal forward price; frictionless, arbitrage-free markets.
- A single volatility per option — does not by itself capture the volatility smile/skew.

## Relationships
- **Model:** [Black-76 model overview](../../knowledge/model/model-black76.md).
- **Related concept:** [CRR Option Pricing Model](con-crr-option-pricing.md) — another option-valuation model (lattice vs closed-form).
