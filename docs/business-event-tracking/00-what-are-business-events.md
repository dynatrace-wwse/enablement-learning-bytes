---
description: Learn how to capture, send, and query business events in Dynatrace. Understand the BizEvents pipeline from instrumentation to dashboard.
tags:
  - business-analytics
  - bizevents
  - dql
difficulty: beginner
duration: 8
---

> **Scenario** — Your e-commerce team wants to track checkout funnel conversions. You'll set up business event capture to measure cart additions, checkout starts, and completed purchases.
>
> **Your goal:** Understand the business events pipeline and how to query conversion data with DQL.

# What Are Business Events?

Business events (BizEvents) capture domain-specific occurrences that matter to your business — not just technical metrics.

## Examples

| Event | Type | Key Data |
|-------|------|----------|
| Cart item added | `com.shop.cart.add` | productId, quantity, price |
| Checkout started | `com.shop.checkout.start` | cartTotal, itemCount |
| Purchase completed | `com.shop.purchase.complete` | orderId, total, paymentMethod |
| User signed up | `com.shop.user.signup` | plan, source |

## How They Work

1. **Instrumentation**: Your app sends events via the OneAgent API or REST API
2. **Ingestion**: Events flow through the BizEvents pipeline with OpenPipeline processing
3. **Storage**: Events are stored in Grail for querying
4. **Analysis**: Use DQL to explore, aggregate, and visualize

## Event Structure

Every business event includes:
- `event.type` — The event category (e.g., `com.shop.cart.add`)
- `event.provider` — The source system
- `timestamp` — When it happened
- Custom attributes — Your domain-specific data

<!-- LAB_QUESTION
type: multiple-choice
question: Which field uniquely identifies the category of a business event?
options:
  - event.name
  - event.type
  - event.category
  - event.id
correct: 1
explanation: '`event.type` is the standard field that categorizes business events (e.g., `com.shop.cart.add`).'
-->
