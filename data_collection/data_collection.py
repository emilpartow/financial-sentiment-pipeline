"""
Reddit post collector for financial keywords/companies across multiple subreddits.

Uses PRAW to fetch recent Reddit submissions about each company/keyword in the given subreddits,
saves results per company (across all subreddits) as CSV, and only appends truly new posts
(not already in the existing file).

Can be used as a library function or in a scheduled script.

Args:
    companies (list of str): Companies or keywords to search for (e.g. ['Apple', 'Tesla']).
    client_id (str): Reddit API client ID.
    client_secret (str): Reddit API client secret.
    user_agent (str): Reddit API user agent.
    subreddits (list of str, optional): List of subreddits to search. Defaults to ['stocks'].
    posts_per_subreddit (int, optional): Max posts to fetch per subreddit per company. Default: 10.
    sleep_time (int, optional): Seconds to sleep between subreddit queries (for API rate limiting).
    save_dir (str, optional): Directory to save output CSVs.

Returns:
    dict: {company: DataFrame} for each company, with all fetched (and deduplicated) posts.

Example:
    >>> collect_reddit_posts(
            companies=["Apple", "Tesla"],
            client_id="...",
            client_secret="...",
            user_agent="...",
            subreddits=["stocks", "wallstreetbets"],
            posts_per_subreddit=50
        )
"""

import praw
import pandas as pd
import time
import os
import datetime
import logging
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import reddit_config

# Jetzt kannst du z.B. verwenden:
CLIENT_ID = config.CLIENT_ID

def collect_reddit_posts(
    companies,
    client_id,
    client_secret,
    user_agent,
    subreddits=["stocks"],
    posts_per_subreddit=10,
    sleep_time=10,
    save_dir="data_collection/data"
):
    """
    Collect recent Reddit posts mentioning given companies/keywords from multiple subreddits,
    and store/update per-company CSVs with deduplication.

    Args:
        companies (list of str): Companies or keywords to search.
        client_id (str): Reddit API client ID.
        client_secret (str): Reddit API client secret.
        user_agent (str): Reddit API user agent.
        subreddits (list of str, optional): List of subreddits to search. Defaults to ['stocks'].
        posts_per_subreddit (int, optional): Max posts per subreddit/company. Default: 10.
        sleep_time (int, optional): Pause between subreddit queries (seconds).
        save_dir (str, optional): Directory to save output CSVs.

    Returns:
        dict: {company: DataFrame} mapping, where each DataFrame contains all collected posts for that company.
    """
    os.makedirs(save_dir, exist_ok=True)
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    all_dfs = {}

    # Loop over all companies/keywords to collect posts
    for company in companies:
        all_posts = []
        for subreddit in subreddits:
            posts = []
            try:
                # Fetch recent posts for this company in this subreddit
                for submission in reddit.subreddit(subreddit).search(company, sort="new", limit=posts_per_subreddit):
                    posts.append({
                        "id": submission.id,
                        "title": submission.title,
                        "text": submission.selftext,
                        "created_utc": submission.created_utc,
                        "created_datetime": datetime.datetime.utcfromtimestamp(submission.created_utc),
                        "author": str(submission.author),
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                        "upvote_ratio": submission.upvote_ratio,
                        "flair": getattr(submission, "link_flair_text", None),
                        "permalink": submission.permalink,
                        "url": submission.url,
                        "subreddit": str(submission.subreddit),
                        "company": company
                    })
                logging.info(f"{company} | r/{subreddit}: {len(posts)} posts fetched from API.")
                time.sleep(sleep_time)  # Pause to avoid hitting Reddit's rate limits
            except Exception as e:
                logging.error(f"Error fetching posts for {company} in r/{subreddit}: {e}", exc_info=True)
            all_posts.extend(posts)

        # Save all collected posts for this company to CSV (with deduplication)
        df = pd.DataFrame(all_posts)
        file_name = f"{save_dir}/{company.lower().replace(' ', '_')}_reddit.csv"

        num_new_posts = 0
        if os.path.exists(file_name):
            existing_df = pd.read_csv(file_name)
            existing_ids = set(existing_df["id"])
            new_posts = df[~df["id"].isin(existing_ids)]
            num_new_posts = len(new_posts)
            combined_df = pd.concat([existing_df, new_posts], ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset='id')
            combined_df.to_csv(file_name, index=False)
            all_dfs[company] = combined_df
        else:
            num_new_posts = len(df)
            df.to_csv(file_name, index=False)
            all_dfs[company] = df

        logging.info(f"{company}: {num_new_posts} truly new posts added, {len(all_dfs[company])} total posts saved.")

    return all_dfs