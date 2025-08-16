# keyword_extractor.py
import re
from collections import Counter
from typing import List

import streamlit as st

try:
    from keybert import KeyBERT

    KEYBERT_AVAILABLE = True
except ImportError:
    KEYBERT_AVAILABLE = False
    st.warning("KeyBERT not available, using fallback method")


class KeywordExtractor:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize keyword extractor

        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.kw_model = None

    @st.cache_resource
    def _load_model(_self):
        """Load KeyBERT model (cached for performance)"""
        if not KEYBERT_AVAILABLE:
            return None

        try:
            return KeyBERT(model=_self.model_name)
        except Exception as e:
            st.warning(f"Failed to load KeyBERT model: {str(e)}")
            return None

    def extract_keywords(
        self, text: str, num_keywords: int = 10, min_ngram: int = 1, max_ngram: int = 2
    ) -> List[str]:
        """
        Extract keywords from text

        Args:
            text: Input text
            num_keywords: Number of keywords to extract
            min_ngram: Minimum n-gram size
            max_ngram: Maximum n-gram size

        Returns:
            List of extracted keywords
        """
        if not text.strip():
            return []

        try:
            # Try KeyBERT first
            if KEYBERT_AVAILABLE:
                if self.kw_model is None:
                    self.kw_model = self._load_model()

                if self.kw_model is not None:
                    keywords = self.kw_model.extract_keywords(
                        text,
                        keyphrase_ngram_range=(min_ngram, max_ngram),
                        stop_words="english",
                        top_k=num_keywords,
                        use_maxsum=True,
                        nr_candidates=20,
                    )
                    return [kw[0] for kw in keywords]

            # Fallback to TF-IDF based extraction
            return self._tfidf_keywords(text, num_keywords, min_ngram, max_ngram)

        except Exception as e:
            st.warning(f"KeyBERT extraction failed, using fallback: {str(e)}")
            return self._tfidf_keywords(text, num_keywords, min_ngram, max_ngram)

    def _tfidf_keywords(
        self, text: str, num_keywords: int, min_ngram: int, max_ngram: int
    ) -> List[str]:
        """
        Fallback TF-IDF based keyword extraction

        Args:
            text: Input text
            num_keywords: Number of keywords to extract
            min_ngram: Minimum n-gram size
            max_ngram: Maximum n-gram size

        Returns:
            List of keywords
        """
        try:
            # Clean and preprocess text
            text = text.lower()
            text = re.sub(r"[^\w\s]", " ", text)
            words = text.split()

            # Remove common stop words
            stop_words = {
                "a",
                "an",
                "and",
                "are",
                "as",
                "at",
                "be",
                "by",
                "for",
                "from",
                "has",
                "he",
                "in",
                "is",
                "it",
                "its",
                "of",
                "on",
                "that",
                "the",
                "to",
                "was",
                "were",
                "will",
                "with",
                "this",
                "but",
                "they",
                "have",
                "had",
                "what",
                "said",
                "each",
                "which",
                "their",
                "time",
                "if",
                "up",
                "out",
                "many",
                "then",
                "them",
                "these",
                "so",
                "some",
                "her",
                "would",
                "make",
                "like",
                "into",
                "him",
                "two",
                "more",
                "very",
                "after",
                "words",
                "long",
                "than",
                "first",
                "been",
                "call",
                "who",
                "oil",
                "sit",
                "now",
                "find",
                "down",
                "day",
                "did",
                "get",
                "come",
                "made",
                "may",
                "part",
            }

            # Filter words
            filtered_words = [
                word for word in words if len(word) > 2 and word not in stop_words
            ]

            # Generate n-grams
            ngrams = []
            for n in range(min_ngram, max_ngram + 1):
                for i in range(len(filtered_words) - n + 1):
                    ngram = " ".join(filtered_words[i : i + n])
                    ngrams.append(ngram)

            # Count frequency
            word_freq = Counter(ngrams)

            # Get top keywords
            top_keywords = word_freq.most_common(num_keywords)
            return [keyword for keyword, _ in top_keywords]

        except Exception as e:
            st.error(f"TF-IDF keyword extraction failed: {str(e)}")
            return []

    def extract_topics(self, text: str, num_topics: int = 5) -> List[str]:
        """
        Extract main topics from text (simplified approach)

        Args:
            text: Input text
            num_topics: Number of topics to extract

        Returns:
            List of topics
        """
        try:
            # Use keyword extraction with longer n-grams for topics
            topics = self.extract_keywords(text, num_topics, min_ngram=2, max_ngram=3)
            return topics[:num_topics]
        except Exception as e:
            st.error(f"Topic extraction failed: {str(e)}")
            return []

    def get_word_frequency(self, text: str, top_n: int = 20) -> dict:
        """
        Get word frequency distribution

        Args:
            text: Input text
            top_n: Number of top words to return

        Returns:
            Dictionary of word frequencies
        """
        try:
            # Clean text
            text = text.lower()
            text = re.sub(r"[^\w\s]", " ", text)
            words = text.split()

            # Remove stop words and short words
            stop_words = {
                "a",
                "an",
                "and",
                "are",
                "as",
                "at",
                "be",
                "by",
                "for",
                "from",
                "has",
                "he",
                "in",
                "is",
                "it",
                "its",
                "of",
                "on",
                "that",
                "the",
                "to",
                "was",
                "were",
                "will",
                "with",
            }

            filtered_words = [
                word for word in words if len(word) > 2 and word not in stop_words
            ]

            # Count frequency
            word_freq = Counter(filtered_words)
            return dict(word_freq.most_common(top_n))

        except Exception as e:
            st.error(f"Word frequency analysis failed: {str(e)}")
            return {}
