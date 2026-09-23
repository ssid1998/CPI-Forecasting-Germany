# Report reminder

- Explain that Bitcoin trades 24/7, so `yfinance` still defines an opening and closing price by splitting the continuous price stream into fixed time intervals.
- For daily `BTC-USD` data in `yfinance`, the day is typically treated as a UTC calendar day:
  `Open` is the first traded price after `00:00 UTC`, and `Close` is the last traded price before the next `00:00 UTC`.
- Clarify that this is not a true market open or market close in the stock-market sense. It is the start and end of the selected reporting interval.
- Mention that for crypto, Yahoo Finance may show `Previous Close` and `Open` as the same value because one day ends exactly where the next day begins.
