from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import logging

class FinBERTSentiment:
    """
    A sentiment analysis utility using the FinBERT model (finance-tuned BERT) for financial text.

    This class loads the FinBERT model from Huggingface, provides methods for sentiment prediction
    on single texts, lists, or entire DataFrames, and maps results to numeric sentiment scores.

    Attributes:
        model_name (str): Huggingface model identifier.
        device (str): Torch device ("cuda" or "cpu").
        labels (list): List of sentiment labels ["negative", "neutral", "positive"].
        tokenizer: The loaded Huggingface tokenizer.
        model: The loaded Huggingface model.
    """

    def __init__(self, model_name="yiyanghkust/finbert-tone", device=None, verbose=True):
        """
        Initialize the FinBERT sentiment analyzer.

        Args:
            model_name (str): Huggingface model to use. Defaults to "yiyanghkust/finbert-tone".
            device (str, optional): Device to use ("cuda" or "cpu"). Auto-detects if not set.
            verbose (bool): Whether to print info messages.
        """
        self.labels = ['negative', 'neutral', 'positive']
        self.model_name = model_name
        self.verbose = verbose
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        if self.verbose:
            logging.info(f"Loading FinBERT model on device: {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.to(self.device)

    def reload_model(self, model_name):
        """
        Reload the model and tokenizer with a new model name.

        Args:
            model_name (str): Huggingface model identifier to load.
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.to(self.device)
        if self.verbose:
            logging.info(f"Model reloaded: {self.model_name}")

    def predict(self, text, return_probs=False):
        """
        Predict sentiment for a single text string.

        Args:
            text (str): Input text to analyze.
            return_probs (bool): If True, return softmax probabilities as well.

        Returns:
            str or (str, np.ndarray): Sentiment label, optionally with probability array.
        """
        if not isinstance(text, str) or not text.strip():
            # Return neutral for empty or invalid text
            if return_probs:
                return "neutral", np.array([0, 1, 0])
            return "neutral"
        # Tokenize and run through model
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
        sentiment = self.labels[np.argmax(probs)]
        if return_probs:
            return sentiment, probs
        return sentiment

    def predict_many(self, texts, return_probs=False, batch_size=16, show_progress=True):
        """
        Predict sentiment for a list or Series of texts, with batching for speed.

        Args:
            texts (list or pd.Series): List of input texts.
            return_probs (bool): Whether to return probabilities.
            batch_size (int): Number of samples per batch.
            show_progress (bool): Whether to show a tqdm progress bar.

        Returns:
            list: List of predicted sentiment labels (or label, prob tuples).
        """
        results = []
        texts = list(texts)
        iterator = tqdm(range(0, len(texts), batch_size), desc="FinBERT Sentiment", disable=not show_progress)
        for i in iterator:
            # Prepare and sanitize batch
            batch_texts = [t if isinstance(t, str) and t.strip() else "" for t in texts[i:i+batch_size]]
            inputs = self.tokenizer(batch_texts, return_tensors="pt", truncation=True, padding=True, max_length=128)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1).cpu().numpy()
            for idx, p in enumerate(probs):
                sentiment = self.labels[np.argmax(p)] if batch_texts[idx].strip() else "neutral"
                if return_probs:
                    results.append((sentiment, p))
                else:
                    results.append(sentiment)
        return results

    def predict_dataframe(self, df, text_column="fulltext", return_probs=True, batch_size=16, show_progress=True):
        """
        Predict sentiment for a DataFrame column of texts.

        Args:
            df (pd.DataFrame): DataFrame containing text data.
            text_column (str): Name of column containing text.
            return_probs (bool): Whether to add probability columns.
            batch_size (int): Batch size for model inference.
            show_progress (bool): Show tqdm progress bar.

        Returns:
            pd.DataFrame: Copy of input DataFrame with sentiment columns appended.
        """
        results = self.predict_many(df[text_column], return_probs=return_probs, batch_size=batch_size, show_progress=show_progress)
        df = df.copy()
        df["sentiment"] = [x[0] for x in results]
        if return_probs:
            df["prob_negative"] = [x[1][0] for x in results]
            df["prob_neutral"]  = [x[1][1] for x in results]
            df["prob_positive"] = [x[1][2] for x in results]
        return df

    def to_score(self, sentiment):
        """
        Map a sentiment label to a numeric score (negative=0, neutral=0.5, positive=1).

        Args:
            sentiment (str): Sentiment label.

        Returns:
            float: Sentiment score.
        """
        score_map = {"negative": 0, "neutral": 0.5, "positive": 1}
        return score_map.get(sentiment, 0.5)

    def add_score_column(self, df, sentiment_col="sentiment", new_col="sentiment_score"):
        """
        Add a numeric sentiment score column to the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame with sentiment label column.
            sentiment_col (str): Name of sentiment label column.
            new_col (str): Name for the new score column.

        Returns:
            pd.DataFrame: DataFrame with sentiment score column added.
        """
        df[new_col] = df[sentiment_col].map(self.to_score)
        return df