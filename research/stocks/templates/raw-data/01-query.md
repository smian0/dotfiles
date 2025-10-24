# Perplexity Query - {TICKER} - {DATE}

**Date:** {DATE}
**Ticker:** {TICKER}
**Company:** {COMPANY_NAME}
**Perplexity URL:** https://www.perplexity.ai/finance/{TICKER}

---

## Query Text

```
{QUERY_TEXT}
```

---

## Query Parameters

- **Entry Zone:** ${ENTRY_LOW}-${ENTRY_HIGH}
- **Previous Earnings Date:** {PREV_EARNINGS_DATE}
- **Next Earnings Date:** {NEXT_EARNINGS_DATE}
- **Research Type:** Daily Update

---

## Template Used

```
Latest update on {COMPANY_NAME} ({TICKER}) for {DATE}:
(1) Current stock price and today's intraday price action,
(2) Any news or developments in past 24-48 hours,
(3) Has price reached the ${ENTRY_LOW}-${ENTRY_HIGH} entry zone yet?
(4) Updated RSI and MACD readings if available,
(5) Any changes to earnings date (currently {NEXT_EARNINGS_DATE}) or new catalysts scheduled.
```

---

**Timestamp:** {TIMESTAMP}
**Session ID:** {SESSION_ID}
