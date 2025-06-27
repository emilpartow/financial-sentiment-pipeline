"""
Visualizes Reddit sentiment and daily stock returns for a given stock,
with rolling sentiment smoothing over a set number of calendar days.
Also plots the closing price time series for context.

Dependencies:
- pandas
- matplotlib
- yfinance

Set STOCK and TICKER at the top to analyze different companies.
Sentiment data must be available as a CSV in the given RESULTS_FILE path.
"""

import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import timedelta

# === USER SETTINGS ===
STOCK = "microsoft"      # Name for filepaths/identification (e.g., "apple")
TICKER = "MSFT"          # Yahoo Finance ticker (e.g., "AAPL" for Apple)

RESULTS_FILE = f"sentiment_analysis/results/{STOCK}_sentiment_reddit.csv"
N_DAYS = 60              # Total number of days to analyze (history length)
ROLLING_WINDOW = 3       # Rolling window size (in days) for sentiment smoothing

# === LOAD SENTIMENT DATA ===
df = pd.read_csv(RESULTS_FILE)
df['created_datetime'] = pd.to_datetime(df['created_datetime'])
df['date'] = df['created_datetime'].dt.date

# Restrict to only the last N_DAYS of data
last_date = df['date'].max()
first_date = last_date - timedelta(days=N_DAYS - 1)
recent_df = df[(df['date'] >= first_date) & (df['date'] <= last_date)]

# Calculate daily mean sentiment and apply a rolling window (by calendar days)
daily_sentiment = recent_df.groupby('date')['sentiment_score'].mean().sort_index()
daily_sentiment.index = pd.to_datetime(daily_sentiment.index)

# Rolling mean over a fixed number of days (calendar window, robust to missing dates)
rolling_sentiment = daily_sentiment.rolling(window=f"{ROLLING_WINDOW}D", min_periods=1).mean()
# Shift forward to make sentiment a "predictor" for the next day's return
rolling_sentiment = rolling_sentiment.shift(1)

# === LOAD STOCK PRICE DATA AND CALCULATE RETURNS ===
stock = yf.download(
    TICKER, 
    start=str(first_date), 
    end=str(last_date + timedelta(days=1)), 
    auto_adjust=True   # or False, if you want unadjusted prices
)
if stock.empty:
    raise ValueError(f"No stock data found for {TICKER} between {first_date} and {last_date}.")

# Calculate daily close-to-close percentage return
stock['return'] = stock['Close'].pct_change()
stock['date'] = stock.index.date

# Align returns to sentiment dates for accurate comparison
stock_returns = stock.set_index('date')['return'].reindex(rolling_sentiment.index)

# === DYNAMIC Y-LIMITS WITH PADDING (visual clarity) ===
# Sentiment axis centered around neutral (0.5)
sentiment_neutral = 0.5
sent_max = abs(rolling_sentiment - sentiment_neutral).max()
sent_range = max(sent_max * 1.15 + 0.02, 0.05)  # Add 15% and min. width for clarity
sent_ylim = (sentiment_neutral - sent_range, sentiment_neutral + sent_range)

# Return axis centered around zero
return_neutral = 0.0
ret_max = abs(stock_returns - return_neutral).max()
ret_range = max(ret_max * 1.15 + 0.001, 0.01)
ret_ylim = (return_neutral - ret_range, return_neutral + ret_range)

# === PLOT: SENTIMENT/RETURN (LEFT), CLOSE PRICE (RIGHT) ===
fig, (ax1, ax3) = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={'width_ratios': [1, 1]})
color_sent = "royalblue"
color_ret = "darkorange"

# --- Panel 1: Rolling Sentiment & Daily Return ---
ax1.set_title(f"{TICKER} (Microsoft): Sentiment vs. Return", fontsize=13)
ax1.set_xlabel("Date", fontsize=11)
ax1.set_ylabel(f"Reddit Sentiment (rolling {ROLLING_WINDOW} days)", color=color_sent, fontsize=11)
ax1.plot(rolling_sentiment.index, rolling_sentiment.values, marker='o', color=color_sent, linewidth=2, label="Sentiment")
ax1.axhline(sentiment_neutral, color='grey', linestyle='--', linewidth=1, alpha=0.8, label="Sentiment Neutral")
ax1.set_ylim(sent_ylim)
ax1.tick_params(axis='y', labelcolor=color_sent)
ax1.grid(True, linestyle=':', alpha=0.3)

# Add daily return as bar plot on secondary y-axis
ax2 = ax1.twinx()
ax2.set_ylabel("Daily Return", color=color_ret, fontsize=11)
ax2.bar(stock_returns.index, stock_returns.values, width=0.7, color=color_ret, alpha=0.3, label="Daily Return")
ax2.set_ylim(ret_ylim)
ax2.tick_params(axis='y', labelcolor=color_ret)

# Merge legends from both axes for clarity
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=10, frameon=True)

# --- Panel 2: Closing Price Time Series ---
stock_in_range = stock.loc[(stock['date'] >= first_date) & (stock['date'] <= last_date)]
ax3.plot(stock_in_range['date'], stock_in_range['Close'], color='black', linewidth=2)
ax3.set_xlabel("Date", fontsize=11)
ax3.set_ylabel("Close Price (USD)", fontsize=11)
ax3.set_title(f"{TICKER} (Microsoft): Closing Price", fontsize=13)
ax3.grid(True, linestyle=':', alpha=0.3)

# Rotate x-ticks for both panels for readability
for ax in [ax1, ax3]:
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

# Finalize and display
fig.tight_layout()

plt.show()