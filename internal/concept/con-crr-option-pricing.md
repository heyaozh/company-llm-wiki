---
id: con-crr-option-pricing
type: concept
title: "Cox–Ross–Rubinstein (CRR) Binomial Option Pricing Model"
parent: ""
concept_kind: pricing
model: model-crr
status: draft
owner: dl625
version: 1
review_year: 2026
last_reviewed: 2026-06-24
completeness: theory_only
open_questions:
  - "Confirm concept_kind: set to `pricing`; switch to `methodology` if your taxonomy classes pricing-model theory there."
  - "Parent framework id is not yet set (which framework this concept sits under)."
  - "Which products use CRR, and whether early-exercise (American) features are in scope, is not documented."
  - "Tree step count / convergence and any firm-specific calibration are not documented."
  - "Source document and its SharePoint link to be added to source_refs."
  - "Verify the theory below against the source document and correct any firm-specific conventions."
source_refs:
  - "REPLACE - CRR model source document (local PDF; upload to SharePoint and link)"
references:
  - model-crr
tags: [valuation, options, lattice]
---

# Cox–Ross–Rubinstein (CRR) Binomial Option Pricing Model

> Verify the theory below against the source document and correct any firm-specific
> conventions before marking this note complete.

## Summary
CRR (Cox, Ross & Rubinstein, 1979) prices options on a **discrete-time binomial lattice**.
Each step the underlying moves up by factor u or down by factor d; the option is valued by
backward induction under the risk-neutral probability. It handles early exercise naturally and
converges to the continuous-time price as the number of steps increases.

## Theory / content
Over a step of length Δt, with volatility σ and risk-free rate r, the standard CRR parameters
are:

$$ u = e^{\sigma\sqrt{\Delta t}}, \qquad d = \frac{1}{u}, \qquad p = \frac{e^{r\Delta t} - d}{u - d}, $$

where p is the risk-neutral probability of an up move. Terminal payoffs are discounted back
through the tree:

$$ V_t = e^{-r\Delta t}\left[\,p\,V_{t+\Delta t}^{\,up} + (1-p)\,V_{t+\Delta t}^{\,down}\,\right]. $$

For American options, at each node take the maximum of the continuation value above and the
immediate exercise value.

## Inputs & data
Requires: spot/forward price, strike K, time to expiry T, volatility σ, risk-free rate r, and
the number of steps N. The specific data sources and step settings used in our implementation
are not documented here (see open_questions).

## Assumptions & limitations
- Discrete binomial dynamics; accuracy depends on the number of steps N (converges as N → ∞).
- Constant volatility and rate per step in the standard formulation.
- Risk-neutral, arbitrage-free single-factor model.
- Computationally heavier than closed-form Black-76, especially for many steps / many options.

## Relationships
- **Model:** [CRR model overview](../../knowledge/model/model-crr.md).
- **Related concept:** [Black-76 Option Pricing Model](con-black76-option-pricing.md) — closed-form alternative; CRR converges to it for European options.
