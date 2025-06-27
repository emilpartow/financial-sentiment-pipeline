"""
Batch sentiment enrichment for Reddit post CSVs using FinBERT.

This script loads raw Reddit comment data for multiple stocks,
applies FinBERT sentiment analysis only to new (unprocessed) posts,
and saves/updates enriched CSVs with sentiment columns.

- Requires: finbert_sentiment.py in the same or importable directory.
- Logging writes to both terminal and 'sentiment_analysis/enrich_sentiment.log'.

Directory structure:
    data_collection/data/            # raw Reddit post CSVs, e.g. 'apple_reddit.csv'
    sentiment_analysis/results/      # enriched output files, e.g. 'apple_sentiment_reddit.csv'

Usage:
    $ python enrich_sentiment.py

Each run processes all new posts in all CSV files found in the raw data directory.
"""

import os
import pandas as pd
import logging
from finbert_sentiment import FinBERTSentiment

# Set directories for input (raw data) and output (sentiment results)
DATA_DIR = "data_collection/data"
RESULTS_DIR = "sentiment_analysis/results"
os.makedirs("sentiment_analysis", exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Setup logging to file and terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("sentiment_analysis/enrich_sentiment.log"),
        logging.StreamHandler()
    ]
)

# Initialize FinBERT sentiment analyzer
finbert = FinBERTSentiment()

# Iterate through all CSVs in the raw data directory
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".csv"):
        stock = filename.replace("_reddit.csv", "")
        logging.info(f"Processing {stock}...")

        # Load the raw Reddit data for this stock
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, filename))
        except Exception as e:
            logging.error(f"Could not read {filename}: {e}")
            continue

        # Choose which column to use for text: fulltext > text > title
        text_col = "fulltext" if "fulltext" in df.columns else ("text" if "text" in df.columns else "title")

        # Load existing sentiment results, if they exist
        result_path = os.path.join(RESULTS_DIR, f"{stock}_sentiment_reddit.csv")
        if os.path.exists(result_path):
            df_sent = pd.read_csv(result_path)
            done_ids = set(df_sent["id"])
        else:
            df_sent = pd.DataFrame()
            done_ids = set()

        # Filter only rows that have not yet been analyzed (by unique 'id')
        if "id" in df.columns:
            new_rows = df[~df["id"].isin(done_ids)]
        else:
            new_rows = df

        logging.info(f"{len(new_rows)} new posts to analyze for {stock}.")

        if len(new_rows) > 0:
            try:
                # Run sentiment prediction and add numeric score
                df_new = finbert.predict_dataframe(new_rows, text_column=text_col, return_probs=True)
                df_new = finbert.add_score_column(df_new)
                # Combine new results with previous ones, remove duplicates
                df_sent = pd.concat([df_sent, df_new], ignore_index=True)
                df_sent = df_sent.drop_duplicates(subset="id")
                df_sent.to_csv(result_path, index=False)
                logging.info(f"Updated: {result_path} ({len(df_sent)} total entries)")
            except Exception as e:
                logging.error(f"Sentiment analysis failed for {stock}: {e}")
        else:
            logging.info(f"No new posts to analyze for {stock}.")
