# summarizer.py
from typing import Optional

import streamlit as st

# Try to import torch and transformers with fallback
try:
    import torch
    from transformers import (
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
        T5ForConditionalGeneration,
        T5Tokenizer,
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    st.warning("PyTorch and/or Transformers not available. Using extractive summarization only.")


class IndicBARTSummarizer:
    def __init__(self, model_name: str = "facebook/mbart-large-50"):
        """
        Initialize multilingual summarizer

        Falls back to extractive summarization if neural models fail to load.

        Args:
            model_name: Name of the multilingual model to use
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.use_neural = True  # Flag to control neural vs extractive

    @st.cache_resource
    def _load_model(_self):
        """Load multilingual model and tokenizer (cached for performance)"""
        if not TRANSFORMERS_AVAILABLE:
            st.info("Neural summarization not available. Using extractive summarization.")
            _self.use_neural = False
            return None, None, None

        # Try different models in order of preference (simpler models first)
        model_options = [
            "t5-small",  # Start with basic T5 - most reliable
            "facebook/bart-large-cnn",  # English BART for summarization
            "sshleifer/distilbart-cnn-12-6",  # Smaller, faster BART
        ]

        for model_name in model_options:
            try:
                st.info(f"Attempting to load model: {model_name}")

                # Add trust_remote_code and use_fast=False to avoid tokenizer issues
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    use_fast=False,  # Use slow tokenizer to avoid conversion issues
                    trust_remote_code=True
                )
                model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    trust_remote_code=True
                )

                # Move to GPU if available
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                model = model.to(device)

                st.success(f"✅ Successfully loaded model: {model_name}")
                _self.model_name = model_name  # Update the model name to the working one
                return tokenizer, model, device

            except Exception as e:
                st.warning(f"Failed to load model '{model_name}': {str(e)[:100]}...")
                continue

        # If all models fail, try a last-resort basic approach
        try:
            st.info("Attempting basic T5 with minimal configuration...")

            tokenizer = T5Tokenizer.from_pretrained("t5-small", legacy=False)
            model = T5ForConditionalGeneration.from_pretrained("t5-small")

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = model.to(device)

            st.success("✅ Successfully loaded T5 with basic configuration")
            _self.model_name = "t5-small"
            return tokenizer, model, device

        except Exception as e:
            st.warning(f"Even basic T5 failed: {str(e)[:100]}...")

        # If all models fail
        st.error("All neural summarization models failed to load. Using extractive summarization.")
        _self.use_neural = False
        return None, None, None

    def summarize(
        self, text: str, language_code: str = "en", max_length: int = 150
    ) -> Optional[str]:
        """
        Summarize text using IndicBART

        Args:
            text: Input text to summarize
            language_code: Language code for the text
            max_length: Maximum length of summary

        Returns:
            Summarized text or None if failed
        """
        if not text.strip():
            return None

        try:
            # Load model if not already loaded
            if self.tokenizer is None or self.model is None:
                self.tokenizer, self.model, self.device = self._load_model()

            # If model loading failed or neural disabled, use extractive summarization
            if self.model is None or not self.use_neural:
                return self._extractive_summary(text, max_length)

            # Handle different model types
            if "mbart" in self.model_name.lower():
                return self._mbart_summarize(text, language_code, max_length)
            elif "t5" in self.model_name.lower():
                return self._t5_summarize(text, max_length)
            else:
                # Generic approach
                return self._generic_summarize(text, max_length)

        except Exception as e:
            st.warning(f"Neural summarization failed, using extractive method: {str(e)}")
            return self._extractive_summary(text, max_length)

    def _t5_summarize(self, text: str, max_length: int) -> str:
        """Summarize using T5 model"""
        if not self.use_neural or self.tokenizer is None or self.model is None:
            return self._extractive_summary(text, max_length)

        try:
            # T5 expects "summarize: " prefix
            input_text = f"summarize: {text}"
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                summary_ids = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    min_length=30,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True,
                )

            summary = self.tokenizer.decode(
                summary_ids[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            return summary.strip()

        except Exception as e:
            st.warning(f"T5 summarization failed: {str(e)}")
            return self._extractive_summary(text, max_length)

    def _mbart_summarize(self, text: str, language_code: str, max_length: int) -> str:
        """Summarize using mBART model"""
        if not self.use_neural or self.tokenizer is None or self.model is None:
            return self._extractive_summary(text, max_length)

        try:
            # Prepare text for mBART-50
            language_mappings = {
                "hi": "hi_IN", "te": "en_XX", "ta": "en_XX", "bn": "bn_IN",
                "mr": "en_XX", "gu": "gu_IN", "kn": "en_XX", "ml": "en_XX",
                "pa": "en_XX", "en": "en_XX",
            }

            src_lang = language_mappings.get(language_code, "en_XX")

            # Check if tokenizer has src_lang attribute (mBART specific)
            if hasattr(self.tokenizer, 'src_lang'):
                self.tokenizer.src_lang = src_lang

            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                generate_kwargs = {
                    "max_length": max_length,
                    "min_length": 30,
                    "num_beams": 4,
                    "length_penalty": 2.0,
                    "early_stopping": True,
                }

                # Add forced_bos_token_id only if tokenizer supports it
                if hasattr(self.tokenizer, 'lang_code_to_id') and src_lang in self.tokenizer.lang_code_to_id:
                    generate_kwargs["forced_bos_token_id"] = self.tokenizer.lang_code_to_id[src_lang]

                summary_ids = self.model.generate(**inputs, **generate_kwargs)

            summary = self.tokenizer.decode(
                summary_ids[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            return summary.strip()

        except Exception as e:
            st.warning(f"mBART summarization failed: {str(e)}")
            return self._extractive_summary(text, max_length)

    def _generic_summarize(self, text: str, max_length: int) -> str:
        """Generic summarization for other models"""
        if not self.use_neural or self.tokenizer is None or self.model is None:
            return self._extractive_summary(text, max_length)

        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                summary_ids = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    min_length=30,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True,
                )

            # Decode summary
            summary = self.tokenizer.decode(
                summary_ids[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )

            return summary.strip()

        except Exception as e:
            st.warning(
                f"Neural summarization failed, using extractive method: {str(e)}"
            )
            return self._extractive_summary(text, max_length)

    def _extractive_summary(self, text: str, max_length: int = 150) -> str:
        """
        Fallback extractive summarization method

        Args:
            text: Input text
            max_length: Maximum length of summary

        Returns:
            Extractive summary
        """
        try:
            sentences = text.split(".")
            sentences = [s.strip() for s in sentences if s.strip()]

            if not sentences:
                return text[:max_length] + "..."

            # Simple extractive approach - take first few sentences
            summary_sentences = []
            current_length = 0

            for sentence in sentences:
                if current_length + len(sentence) > max_length:
                    break
                summary_sentences.append(sentence)
                current_length += len(sentence)

            summary = ". ".join(summary_sentences)
            if summary:
                summary += "."
            else:
                summary = text[:max_length] + "..."

            return summary

        except Exception as e:
            st.error(f"Extractive summarization failed: {str(e)}")
            return text[:max_length] + "..."

    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return ["hi", "te", "ta", "bn", "mr", "gu", "kn", "ml", "pa", "en"]

    def batch_summarize(self, texts: list, language_code: str = "en") -> list:
        """
        Summarize multiple texts in batch

        Args:
            texts: List of texts to summarize
            language_code: Language code

        Returns:
            List of summaries
        """
        summaries = []
        for text in texts:
            summary = self.summarize(text, language_code)
            summaries.append(summary)
        return summaries
