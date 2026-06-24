---
id: model-crr
type: model
title: "Cox–Ross–Rubinstein (CRR) Binomial Option Pricing Model"
status: draft
owner: dl625
version: 1
review_year: 2026
last_reviewed: 2026-06-24
completeness: theory_only
open_questions:
  - "Which specific option products this model is applied to (and whether for American-style early exercise) is not documented."
  - "Number of tree steps / convergence settings used in our implementation are not documented."
  - "Downstream business requirements and specifications are not yet written."
source_refs:
  - "REPLACE - CRR model source document (local PDF; upload to SharePoint and link)"
references:
  - con-crr-option-pricing
  - topic-risk-neutral-valuation
tags: [valuation, options, lattice]
---

# Cox–Ross–Rubinstein (CRR) Binomial Option Pricing Model

> A model page is the entry point to one model's documents. Distilled overview — verify
> against the source documents.

## Overview
CRR is a discrete-time **binomial lattice** model for option valuation. The underlying price
moves up or down by fixed factors each step; option value is obtained by backward induction
under risk-neutral probabilities. Unlike the closed-form [Black-76](model-black76.md), the
lattice naturally handles **early exercise** (American-style) and converges to Black–Scholes /
Black-76 as the number of steps grows.

## Documents (traceability)
- **Concept (methodology/pricing):** [CRR Option Pricing Model](../../internal/concept/con-crr-option-pricing.md)
- **Manuals:** _none yet_
- **Business requirements / specifications:** _none yet_

## Distilled topics
- [Risk-neutral valuation](../topic/topic-risk-neutral-valuation.md) — the discounted-expectation pricing principle this model evaluates numerically by backward induction.

## Status & review
Draft, last reviewed 2026-06-24. Theory only — products covered, step settings, and downstream
linkage not yet documented.
