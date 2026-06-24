---
id: model-black76
type: model
title: "Black-76 Option Pricing Model"
status: draft
owner: dl625
version: 2
review_year: 2026
last_reviewed: 2026-06-24
completeness: theory_only
open_questions:
  - "Which specific index option products this model is applied to is not yet documented."
  - "Downstream business requirements and specifications are not yet written."
source_refs:
  - "black76 option pricing model.pdf (local; upload to SharePoint and replace with the link)"
references:
  - con-black76-option-pricing
tags: [valuation, options, index-options]
---

# Black-76 Option Pricing Model

> A model page is the entry point to one model's documents. Distilled overview — verify
> against the source documents.

## Overview
Black-76 is the standard closed-form model for pricing European options on a forward or
futures price. In our team it is used to value many index options, as part of the chain from
valuation to margin.

## Documents (traceability)
- **Concept (methodology/pricing):** [Black-76 Option Pricing Model](../../internal/concept/con-black76-option-pricing.md)
- **Manuals:** _none yet_
- **Business requirements / specifications:** _none yet_

## Distilled topics
- _none yet_ — to be extracted (e.g. forward price, risk-neutral valuation, log-normal assumption).

## Status & review
Draft, last reviewed 2026-06-24. Theory only — downstream IT/data and margin linkage not yet
documented.
