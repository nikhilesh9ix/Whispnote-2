# summarizer.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import streamlit as st
import torch
from typing import Optional

class IndicBARTSummarizer:
    def __init__(self, model_name: str = "ai4bharat/indicbart-ss"):
        """
        Initialize IndicBART summarizer
        
        Args:
            model_name: Name of the IndicBART model to use
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        
    @st.cache_resource
    def _load_model(_self):
        """Load IndicBART model and tokenizer (cached for performance)"""
        try:
            tokenizer = AutoTokenizer.from_pretrained(_self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(_self.model_name)
            
            # Move to GPU if available
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = model.to(device)
            
            return tokenizer, model, device
            
        except Exception as e:
            st.error(f"Failed to load IndicBART model: {str(e)}")
            # Fallback to a simpler approach
            return None, None, None
    
    def summarize(self, text: str, language_code: str = 'en', max_length: int = 150) -> Optional[str]:
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
            
            # If model loading failed, use extractive summarization
            if self.model is None:
                return self._extractive_summary(text, max_length)
            
            # Prepare text for IndicBART
            # IndicBART expects specific format for different languages
            language_prefixes = {
                'hi': '<2hi>',
                'te': '<2te>',
                'ta': '<2ta>',
                'bn': '<2bn>',
                'mr': '<2mr>',
                'gu': '<2gu>',
                'kn': '<2kn>',
                'ml': '<2ml>',
                'pa': '<2pa>',
                'en': '<2en>'
            }
            
            prefix = language_prefixes.get(language_code, '<2en>')
            formatted_text = f"{prefix} {text}"
            
            # Tokenize
            inputs = self.tokenizer(
                formatted_text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self.device)
            
            # Generate summary
            with torch.no_grad():
                summary_ids = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    min_length=30,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True,
                    no_repeat_ngram_size=3
                )
            
            # Decode summary
            summary = self.tokenizer.decode(
                summary_ids[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            return summary.strip()
            
        except Exception as e:
            st.warning(f"Neural summarization failed, using extractive method: {str(e)}")
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
            sentences = text.split('.')
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
            
            summary = '. '.join(summary_sentences)
            if summary:
                summary += '.'
            else:
                summary = text[:max_length] + "..."
                
            return summary
            
        except Exception as e:
            st.error(f"Extractive summarization failed: {str(e)}")
            return text[:max_length] + "..."
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return ['hi', 'te', 'ta', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa', 'en']
    
    def batch_summarize(self, texts: list, language_code: str = 'en') -> list:
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