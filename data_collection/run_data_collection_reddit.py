"""
Script to collect and regularly update Reddit posts about multiple companies across multiple subreddits.

- Runs one-off or scheduled collection using the collect_reddit_posts function.
- Saves data per company (across all subreddits) as CSV.
- Logs progress and errors to file and terminal.

Note:
    Reddit API credentials must be set in reddit_config.py (not tracked in git).
"""


import logging
import time
from data_collection import collect_reddit_posts
from reddit_config import CLIENT_ID, CLIENT_SECRET, USER_AGENT

# Setup logging (both to file and terminal)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("data_collection/reddit_collector.log"),
        logging.StreamHandler()
    ]
)

def collect_now(
    companies,
    subreddits,
    client_id,
    client_secret,
    user_agent,
    sleep_time=5,
    posts_per_subreddit=20,
    save_dir="data_collection/data"
):
    """
    Collects latest Reddit posts once for all companies and all subreddits,
    storing/updating results per stock.

    Args:
        companies (list): List of companies/keywords.
        subreddits (list): List of subreddits to search in.
        client_id (str): Reddit API client ID.
        client_secret (str): Reddit API client secret.
        user_agent (str): Reddit API user agent.
        sleep_time (int, optional): Seconds to wait between subreddit queries.
        posts_per_subreddit (int, optional): Max posts per subreddit/company.
        save_dir (str, optional): Where to save CSVs.

    Returns:
        dict: Mapping of company name to DataFrame with all collected posts.
    """
    logging.info("One-time Reddit data collection started.")
    try:
        dfs = collect_reddit_posts(
            companies=companies,
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            subreddits=subreddits, 
            posts_per_subreddit=posts_per_subreddit,
            sleep_time=sleep_time,
            save_dir=save_dir
        )
        for company, df in dfs.items():
            logging.info(f"{company}: {len(df)} posts collected (all subreddits).")
    except Exception as e:
        logging.error(f"Failed to collect data: {e}", exc_info=True)
    logging.info("One-time Reddit data collection complete.")
    return dfs

def collect_regularly(
    companies,
    subreddits,
    client_id,
    client_secret,
    user_agent,
    posts_per_subreddit=20,
    save_dir="data_collection/data",
    interval_minutes=60,
    sleep_time=5
):
    """
    Runs Reddit data collection in a loop, with a fixed interval in minutes.

    Args:
        companies, subreddits, client_id, client_secret, user_agent, posts_per_subreddit, save_dir: See collect_now().
        interval_minutes (int): Interval (minutes) to wait between each run.
        sleep_time (int): Pause (seconds) between subreddit requests.

    Returns:
        Never returns (infinite loop).
    """
    while True:
        logging.info("Scheduled Reddit data collection started.")
        collect_now(
            companies, subreddits, client_id, client_secret, user_agent,
            sleep_time=sleep_time,
            posts_per_subreddit=posts_per_subreddit,
            save_dir=save_dir
        )
        logging.info(f"Sleeping for {interval_minutes} minutes before next collection...\n")
        time.sleep(interval_minutes * 60)

# Example usage (script entrypoint)
if __name__ == "__main__":

    # Companies/keywords to search for
    companies = ["Apple", "Tesla", "Microsoft"]

    # Subreddits to search (finance, investing, markets, crypto, etc.)
    subreddits = [
        "stocks", "wallstreetbets", "investing", "StockMarket", "options", "RobinHood",
        "pennystocks", "SecurityAnalysis", "personalfinance", "Dividends", "CryptoCurrency",
        "CryptoMarkets", "ETFs", "FinancialIndependence", "ValueInvesting", "quant",
        "algotrading", "forex", "economy", "Superstonk", "spacs", "financialplanning"
    ]

    # One-time collection (call this directly)
    collect_now(
        companies,
        subreddits,
        CLIENT_ID,
        CLIENT_SECRET,
        USER_AGENT,
        sleep_time=1,
        posts_per_subreddit=1000,
        save_dir="data_collection/data"
    )

    # For scheduled/regular collection, uncomment below:
    # collect_regularly(
    #     companies,
    #     subreddits,
    #     CLIENT_ID,
    #     CLIENT_SECRET,
    #     USER_AGENT,
    #     posts_per_subreddit=100,
    #     save_dir="data_collection/data",
    #     interval_minutes=60,
    #     sleep_time=3
    # )
