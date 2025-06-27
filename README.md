# Reddit Finance Sentiment Pipeline

This repository provides a pipeline for collecting, enriching, and analyzing Reddit posts related to financial companies and topics.  
It uses [PRAW](https://praw.readthedocs.io/en/stable/) for data collection and [FinBERT](https://huggingface.co/yiyanghkust/finbert-tone) for finance-specific sentiment analysis.

## Disclaimer

This project is for research, educational, and demonstration purposes only.

**Nothing in this repository constitutes financial advice or investment recommendations.**  
The data, analysis, and code provided here are not intended to be used for making trading or investment decisions.  
Use at your own risk.

Always do your own research and consult with a qualified financial advisor before making any investment decisions.

## Features

- **Automated Reddit Data Collection:**  
  Collects and updates Reddit submissions mentioning selected companies or keywords across multiple finance-related subreddits.
- **Sentiment Enrichment with FinBERT:**  
  Applies FinBERT (finance-tuned BERT model) to analyze sentiment (negative, neutral, positive) in the collected posts.
- **Deduplication:**  
  Only new posts are processed and appended to the results, so repeated runs are efficient.
- **Easy CSV Export:**  
  Both raw and sentiment-enriched data are saved as CSV files for further analysis or visualization.
- **Costumizable:**  
  Supports flexible company/keyword lists, subreddits, and collection intervals.
- **Easily Extendable:**  
  The modular design allows you to easily add new companies, subreddits, or even other social media/comment sources. You can customize or expand the pipeline for your own research needs.


## Directory Structure
```
your_project/
│
├── reddit_config.py                  # (Your Reddit API credentials, not in git)
│
├── data_collection/
│   ├── run_data_collection.py        # Script to collect Reddit data (batch/scheduled)
│   ├── reddit_collector.log          # Log file for collection runs
│   ├── data_collection.py            # Core collection functions
│   └── data/                         # Raw collected Reddit CSVs (per company)
│       ├── apple_reddit.csv
│       ├── microsoft_reddit.csv
│       └── ...
│
├── sentiment_analysis/
│   ├── finbert_sentiment.py          # FinBERT sentiment analysis utility class
│   ├── enrich_sentiment.py           # Batch-enrich collected data with FinBERT sentiment
│   ├── enrich_sentiment.log          # Log file for enrichment runs
│   └── results/                      # Enriched (with sentiment) CSVs (per company)
│       ├── apple_sentiment_reddit.csv
│       ├── microsoft_sentiment_reddit.csv
│       └── ...
│ 
├── demo/                           
│   └── example_plot.py
│ 
├── requirements.txt
│ 
├── README.md
└── .gitignore
```

## Usage

1. **Set up Reddit API credentials:**  
   Create a file called `reddit_config.py` (see example below) in your main project directory.  
   **Do NOT commit this file!** Add it to your `.gitignore`.

   ```python
   # reddit_config.py
   CLIENT_ID = "your_client_id"
   CLIENT_SECRET = "your_client_secret"
   USER_AGENT = "your_user_agent"
   ```
   
2. **Install requirements:**
   ```sh
   pip install -r requirements.txt
   ```
   
3. **Collect Reddit posts:**
   ```sh
   python run_data_collection.py
   ```
4. **Enrich posts with sentiment:**
   ```sh
   python enrich_sentiment.py
   ```
   
## Demos & Example Plots

See the `demo/` folder for an example script showing
how to visualize the enriched data.

## Sample Data Included

For demonstration and testing purposes, this repository includes small example CSV files for the companies **Apple**, **Tesla**, and **Microsoft**:

- `data_collection/data/`
    - Contains sample Reddit post CSVs (`apple_reddit.csv`, `tesla_reddit.csv`, `microsoft_reddit.csv`), each with a few example comments. This allows the demo scripts and plots to run out of the box and illustrates the expected input structure.

- `sentiment_analysis/results/`
    - Contains corresponding sample enriched files (`apple_sentiment_reddit.csv`, etc.), showing what the output of the sentiment analysis step looks like.

**Note:**  
These files are for demo and development only.  
For your own analysis, replace them with actual Reddit data collected using the scripts in this repository.

