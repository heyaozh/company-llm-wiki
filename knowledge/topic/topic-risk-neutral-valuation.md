---
id: topic-risk-neutral-valuation
type: topic
title: "Risk-Neutral Valuation"
status: draft
owner: dl625
version: 1
review_year: 2026
last_reviewed: 2026-06-24
completeness: partial
open_questions:
  - "Firm-specific discounting / numéraire conventions live in the model and concept docs, not here; review this primitive against internal standards."
source_refs:
  - "Standard no-arbitrage pricing theory (Harrison–Pliska). Cross-checked against the Black-76 and CRR source documents."
references:
  - model-black76
  - model-crr
  - con-black76-option-pricing
  - con-crr-option-pricing
tags: [valuation, no-arbitrage, pricing-principle]
---

# Risk-Neutral Valuation

> An atomic, model-agnostic pricing primitive. Several models build on it; keep it general and
> link it from each model rather than restating it.

## Definition
Under no-arbitrage, with a chosen **numéraire** $N_t$ and its associated **equivalent
martingale (risk-neutral) measure** $\mathbb{Q}$, the value of a derivative paying $H_T$ at
time $T$ is the numéraire-discounted expectation of its payoff:

$$ V_0 = N_0 \, \mathbb{E}^{\mathbb{Q}}\!\left[ \frac{H_T}{N_T} \right]. $$

With the money-market account as numéraire and a constant rate $r$, this reduces to

$$ V_0 = e^{-rT}\, \mathbb{E}^{\mathbb{Q}}\!\left[ H_T \right]. $$

Under $\mathbb{Q}$ the discounted asset price is a martingale; equivalently, the real-world
drift of the underlying is replaced by the risk-free rate (no risk premium).

## Why it matters
This is the common foundation beneath essentially all of our valuation models — and therefore
the chain from valuation to margin. Different models are just different ways of computing the
same risk-neutral expectation.

## Used by
- [Black-76 Option Pricing Model](../model/model-black76.md) — evaluates the risk-neutral
  expectation in closed form under a log-normal forward price.
- [CRR Binomial Option Pricing Model](../model/model-crr.md) — evaluates it numerically by
  backward induction using the risk-neutral up-move probability $p$.

## Related topics
- _none yet_ — candidates to extract next: no-arbitrage, equivalent martingale measure,
  numéraire / change of measure.
