---
description: The reasoning behind Service Level Objectives — choosing an SLI, sizing an error budget, and designing multi-window burn-rate alerts. Concepts and worked arithmetic; no tenant configuration is performed.
tags:
  - sre
  - slos
  - reliability
difficulty: advanced
duration: 10
---

> **Scenario** — Your organization is adopting SRE practices. The platform team needs to define SLOs for critical customer-facing services with appropriate error budgets and alerting.
>
> **Your goal:** Design effective SLOs, understand error budget policies, and configure burn-rate alerts.

# SLI & SLO Fundamentals

## Service Level Indicator (SLI)

An SLI is a quantitative measure of a specific aspect of the service level:

- **Availability SLI**: Proportion of successful requests `good_requests / total_requests`
- **Latency SLI**: Proportion of requests faster than a threshold `fast_requests / total_requests`
- **Throughput SLI**: Request rate within expected bounds

## Service Level Objective (SLO)

An SLO sets a target for an SLI over a rolling window:

> "99.9% of API requests should succeed over a 30-day rolling window"

| Component | Example |
|-----------|---------|
| **SLI** | Success rate |
| **Target** | 99.9% |
| **Window** | 30 days (rolling) |

## Error Budget

Error budget = `1 - SLO target`

For a 99.9% SLO over 30 days:
- Error budget = 0.1% = **43.2 minutes** of downtime
- Or: **4,320 failed requests** out of 4,320,000 total

> **Key insight**: Error budget is not permission to be unreliable — it's a decision-making tool for balancing reliability and velocity.

<!-- LAB_QUESTION
type: multiple-choice
question: For a 99.9% availability SLO over 30 days, approximately how much downtime is the error budget?
options:
  - 4.3 minutes
  - 43 minutes
  - 4.3 hours
  - 43 hours
correct: 1
hint: 30 days = 43,200 minutes. 0.1% of that is...
explanation: 30 days × 24 hours × 60 minutes = 43,200 minutes. Error budget = 0.1% = 43.2 minutes.
-->

<!-- LAB_QUESTION
type: multiple-choice
question: What does the 'error budget' represent?
options:
  - The cost of fixing errors in production
  - The maximum number of bugs allowed per sprint
  - The allowable amount of unreliability within the SLO window
  - The budget allocated to the error-handling team
correct: 2
explanation: Error budget = 1 − SLO target. It quantifies how much unreliability is acceptable, enabling data-driven decisions about feature velocity vs. reliability investment.
-->
