# Burn-Rate Alerts

Traditional threshold alerts on SLO status are either too noisy or too slow. Burn-rate alerts solve this.

## What is Burn Rate?

Burn rate = how fast you're consuming your error budget relative to the window duration.

- **Burn rate 1.0** = consuming budget exactly at the rate that would exhaust it by window end
- **Burn rate 2.0** = consuming at 2x the sustainable rate → budget exhausted in half the window
- **Burn rate 10.0** = consuming at 10x → budget exhausted in 1/10 of the window

## Multi-Window, Multi-Burn-Rate Alerting

Google SRE recommends combining fast and slow windows:

| Page/Ticket | Burn Rate | Long Window | Short Window |
|-------------|-----------|-------------|--------------|
| Page (urgent) | 14.4x | 1 hour | 5 minutes |
| Page (urgent) | 6x | 6 hours | 30 minutes |
| Ticket | 3x | 1 day | 2 hours |
| Ticket | 1x | 3 days | 6 hours |

## Why Two Windows?

- **Long window**: Confirms sustained error rate (avoids alerting on brief spikes)
- **Short window**: Confirms the issue is current (avoids alerting on resolved incidents)

Both conditions must be true simultaneously to fire the alert.

<!-- LAB_QUESTION
type: multiple-choice
question: 'A burn rate of 10x on a 30-day SLO means the error budget will be exhausted in approximately:'
options:
  - 3 hours
  - 3 days
  - 10 days
  - 30 days
correct: 1
hint: If you consume at 10x the sustainable rate, the budget lasts 1/10 of the window.
explanation: 30 days ÷ 10 = 3 days. A 10x burn rate exhausts the entire 30-day error budget in just 3 days.
-->

<!-- LAB_QUESTION
type: multiple-choice
question: Why do burn-rate alerts use both a long window AND a short window?
options:
  - To calculate the average burn rate more accurately
  - Long window confirms sustained issue, short window confirms it's still happening now
  - Long window is for weekdays, short window is for weekends
  - They're redundant — either one alone would work
correct: 1
explanation: The long window catches sustained error budget consumption (filters out spikes). The short window ensures the issue is currently active (avoids stale alerts after recovery).
-->
