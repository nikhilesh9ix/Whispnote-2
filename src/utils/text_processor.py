#!/usr/bin/env python3
"""
Text Processing Utilities for WhispNote
Handles cleaning, formatting, and enhancing transcribed text
"""

import re
from typing import Any, Dict, List, Tuple


class TranscriptionProcessor:
    """Processes and cleans transcribed text from speech-to-text"""

    def __init__(self) -> None:
        # Common filler words in multiple languages
        self.filler_words = {
            "en": [
                "um",
                "uh",
                "er",
                "ah",
                "hmm",
                "like",
                "you know",
                "i mean",
                "so",
                "well",
                "okay",
                "right",
                "actually",
                "basically",
                "literally",
                "obviously",
                "definitely",
                "totally",
            ],
            "hi": [
                "उम",
                "आह",
                "ओह",
                "हम्म",
                "अरे",
                "यार",
                "मतलब",
                "बस",
                "वो",
                "ये",
                "तो",
                "ना",
                "हां",
                "अच्छा",
            ],
            "te": [
                "అమ్మో",
                "అయ్యో",
                "ఓహ్",
                "హమ్",
                "అరె",
                "ఎంటి",
                "అదే",
                "అలాగే",
                "కానీ",
                "అప్పుడు",
                "ఇప్పుడు",
            ],
        }

        # Initialize NLTK data for TextBlob
        self._ensure_nltk_data()

        # Initialize AI processor (optional)
        self.ai_processor = None
        self._init_ai_processor()

    def _init_ai_processor(self) -> None:
        """Initialize AI text processor if available"""
        try:
            from src.ai.llama_summarizer import AdvancedAISummarizer

            self.ai_processor = AdvancedAISummarizer()
        except ImportError:
            print(
                "LLaMA AI processor not available - using traditional NLP methods only"
            )

    def _ensure_nltk_data(self) -> None:
        """Ensure required NLTK data is available for TextBlob"""
        try:
            import nltk
            from nltk.data import find

            # Check if required data exists, download if not
            required_data = ["punkt", "brown", "punkt_tab", "wordnet", "omw-1.4"]

            for data_name in required_data:
                try:
                    find(
                        f"tokenizers/{data_name}"
                        if "punkt" in data_name
                        else (
                            f"corpora/{data_name}"
                            if data_name in ["brown", "wordnet", "omw-1.4"]
                            else data_name
                        )
                    )
                except LookupError:
                    print(f"Downloading NLTK data: {data_name}")
                    nltk.download(data_name, quiet=True)

        except ImportError:
            print("NLTK not available, spell checking may not work properly")

        # Repeated phrases patterns
        self.repetition_patterns = [
            r"\b(\w+)\s+\1\b",  # word word
            r"\b(\w+\s+\w+)\s+\1\b",  # phrase phrase
            r"\b(\w+)\s+\1\s+\1\b",  # word word word
        ]

        # False starts patterns
        self.false_start_patterns = [
            r"\b\w+\s*-\s*\w+",  # word - word
            r"\b\w+\.\.\.\s*\w+",  # word... word
            r"\b[A-Z][a-z]*\s+[A-Z][a-z]*",  # multiple capitalized words (possible restarts)
        ]

    def clean_transcription(
        self, text: str, language: str = "en", use_ai: bool = False
    ) -> Dict[str, Any]:
        """
        Clean transcribed text by removing filler words, repetitions, and false starts

        Args:
            text: Raw transcribed text
            language: Language code for language-specific cleaning
            use_ai: Whether to use AI-powered enhancement

        Returns:
            Dictionary with original, cleaned, and processing steps
        """
        if not text or not text.strip():
            return {
                "original": text,
                "cleaned": text,
                "removed_elements": [],
                "confidence_score": 0.0,
                "processing_method": "none",
            }

        # If AI processing is requested and available
        if use_ai and self.ai_processor:
            return self._ai_enhanced_cleaning(text, language)

        # Traditional NLP processing
        return self._traditional_cleaning(text, language)

    def _ai_enhanced_cleaning(self, text: str, language: str) -> Dict[str, Any]:
        """AI-powered text enhancement using LLaMA 3.1"""
        try:
            ai_result = self.ai_processor.clean_text(text, language)
            return ai_result
        except Exception as e:
            print(
                f"LLaMA AI enhancement failed, falling back to traditional processing: {e}"
            )
            return self._traditional_cleaning(text, language)

    def _traditional_cleaning(self, text: str, language: str) -> Dict[str, Any]:
        """Traditional NLP-based text cleaning"""

        original_text = text
        removed_elements = []
        processing_steps = []

        # Step 1: Normalize whitespace and punctuation
        text = self._normalize_text(text)
        processing_steps.append("Normalized whitespace and punctuation")

        # Step 2: Remove filler words
        text, removed_fillers = self._remove_filler_words(text, language)
        if removed_fillers:
            removed_elements.extend(removed_fillers)
            processing_steps.append(f"Removed {len(removed_fillers)} filler words")

        # Step 3: Fix repetitions
        text, removed_repetitions = self._fix_repetitions(text)
        if removed_repetitions:
            removed_elements.extend(removed_repetitions)
            processing_steps.append(f"Fixed {len(removed_repetitions)} repetitions")

        # Step 4: Clean false starts
        text, removed_false_starts = self._clean_false_starts(text)
        if removed_false_starts:
            removed_elements.extend(removed_false_starts)
            processing_steps.append(f"Cleaned {len(removed_false_starts)} false starts")

        # Step 5: Improve sentence structure
        text = self._improve_sentence_structure(text)
        processing_steps.append("Improved sentence structure")

        # Step 6: Spell and grammar check
        spell_grammar_result = self.check_spelling_and_grammar(text)
        text = spell_grammar_result["corrected_text"]
        processing_steps.append("Spell and grammar check completed")

        # Step 7: Calculate confidence score
        confidence_score = self._calculate_confidence_score(original_text, text)

        return {
            "original": original_text,
            "cleaned": text.strip(),
            "removed_elements": removed_elements,
            "processing_steps": processing_steps,
            "confidence_score": confidence_score,
            "processing_method": "traditional_nlp",
            "word_count_original": len(original_text.split()),
            "word_count_cleaned": len(text.split()),
            "reduction_percentage": (
                ((len(original_text) - len(text)) / len(original_text) * 100)
                if original_text
                else 0
            ),
            "spelling_corrections": spell_grammar_result["spelling_corrections"],
            "grammar_issues": spell_grammar_result["grammar_issues"],
        }
        text, removed_false_starts = self._clean_false_starts(text)
        if removed_false_starts:
            removed_elements.extend(removed_false_starts)
            processing_steps.append(f"Cleaned {len(removed_false_starts)} false starts")

        # Step 5: Improve sentence structure
        text = self._improve_sentence_structure(text)
        processing_steps.append("Improved sentence structure")

        # Step 6: Spell and grammar check
        spell_grammar_result = self.check_spelling_and_grammar(text)
        text = spell_grammar_result["corrected_text"]
        processing_steps.append("Spell and grammar check completed")

        # Step 7: Calculate confidence score
        confidence_score = self._calculate_confidence_score(original_text, text)

        return {
            "original": original_text,
            "cleaned": text.strip(),
            "removed_elements": removed_elements,
            "processing_steps": processing_steps,
            "confidence_score": confidence_score,
            "word_count_original": len(original_text.split()),
            "word_count_cleaned": len(text.split()),
            "reduction_percentage": (
                ((len(original_text) - len(text)) / len(original_text) * 100)
                if original_text
                else 0
            ),
            "spelling_corrections": spell_grammar_result["spelling_corrections"],
            "grammar_issues": spell_grammar_result["grammar_issues"],
        }

    def check_spelling_and_grammar(self, text: str) -> Dict[str, Any]:
        """
        Check and correct spelling and grammar in the text.
        Returns corrected text, list of spelling corrections, and grammar issues.
        """
        try:
            import language_tool_python
            from textblob import TextBlob

            # Spell check using TextBlob
            try:
                blob = TextBlob(text)
                corrected_text = str(blob.correct())
                spelling_corrections = []
                for orig, corr in zip(blob.words, TextBlob(corrected_text).words):
                    if orig != corr:
                        spelling_corrections.append(
                            {"original": str(orig), "corrected": str(corr)}
                        )
            except Exception as e:
                print(f"TextBlob spell check error: {e}")
                # Fallback to original text
                corrected_text = text
                spelling_corrections = []

            # Grammar check using language_tool_python
            try:
                tool = language_tool_python.LanguageTool("en-US")
                matches = tool.check(corrected_text)
                grammar_issues = []
                for match in matches:
                    grammar_issues.append(
                        {
                            "message": match.message,
                            "context": match.context,
                            "suggestions": match.replacements,
                            "offset": match.offset,
                            "errorLength": match.errorLength,
                        }
                    )
            except Exception as e:
                print(f"Grammar check error: {e}")
                grammar_issues = []

            return {
                "corrected_text": corrected_text,
                "spelling_corrections": spelling_corrections,
                "grammar_issues": grammar_issues,
            }

        except ImportError as e:
            print(f"Required libraries not available for spell/grammar check: {e}")
            return {
                "corrected_text": text,
                "spelling_corrections": [],
                "grammar_issues": [],
            }

    def _normalize_text(self, text: str) -> str:
        """Normalize whitespace and basic punctuation"""
        # Fix multiple spaces
        text = re.sub(r"\s+", " ", text)

        # Fix punctuation spacing
        text = re.sub(r"\s*([,.!?;:])\s*", r"\1 ", text)

        # Remove extra dots
        text = re.sub(r"\.{2,}", "...", text)

        return text.strip()

    def _remove_filler_words(self, text: str, language: str) -> Tuple[str, List[str]]:
        """Remove filler words based on language"""
        fillers = self.filler_words.get(language, self.filler_words["en"])
        removed = []

        words = text.split()
        cleaned_words = []

        i = 0
        while i < len(words):
            word = words[i].lower().strip(".,!?;:")

            # Check for single word fillers
            if word in fillers:
                removed.append(words[i])
                i += 1
                continue

            # Check for multi-word fillers
            found_multiword = False
            for filler in fillers:
                if " " in filler:  # Multi-word filler
                    filler_words = filler.split()
                    if (
                        i + len(filler_words) <= len(words)
                        and " ".join(words[i : i + len(filler_words)]).lower() == filler
                    ):
                        removed.extend(words[i : i + len(filler_words)])
                        i += len(filler_words)
                        found_multiword = True
                        break

            if not found_multiword:
                cleaned_words.append(words[i])
                i += 1

        return " ".join(cleaned_words), removed

    def _fix_repetitions(self, text: str) -> Tuple[str, List[str]]:
        """Fix word and phrase repetitions"""
        removed = []

        for pattern in self.repetition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                full_match = match.group(0)
                repeated_part = match.group(1)
                removed.append(f"Repetition: {full_match}")
                text = text.replace(full_match, repeated_part, 1)

        return text, removed

    def _clean_false_starts(self, text: str) -> Tuple[str, List[str]]:
        """Clean false starts and partial words"""
        removed = []

        # Remove partial words with dashes
        pattern = r"\b\w*-\s*"
        matches = re.findall(pattern, text)
        for match in matches:
            removed.append(f"False start: {match}")
            text = re.sub(re.escape(match), "", text)

        # Clean up double spaces created by removals
        text = re.sub(r"\s+", " ", text)

        return text, removed

    def _improve_sentence_structure(self, text: str) -> str:
        """Improve basic sentence structure"""
        if not text:
            return text

        # Capitalize first letter of sentences
        sentences = re.split(r"([.!?]+)", text)
        improved_sentences = []

        for i, sentence in enumerate(sentences):
            if i % 2 == 0 and sentence.strip():  # Text parts (not punctuation)
                sentence = sentence.strip()
                if sentence:
                    sentence = sentence[0].upper() + sentence[1:]
                improved_sentences.append(sentence)
            else:
                improved_sentences.append(sentence)

        result = "".join(improved_sentences)

        # Ensure text starts with capital letter
        if result and result[0].islower():
            result = result[0].upper() + result[1:]

        return result

    def _calculate_confidence_score(self, original: str, cleaned: str) -> float:
        """Calculate confidence score based on cleaning operations"""
        if not original:
            return 0.0

        # Base score
        score = 0.7

        # Length reduction factor (moderate reduction is good)
        length_reduction = (len(original) - len(cleaned)) / len(original)
        if 0.1 <= length_reduction <= 0.3:  # Good reduction
            score += 0.2
        elif length_reduction > 0.5:  # Too much reduction
            score -= 0.2

        # Word count factor
        original_words = len(original.split())
        cleaned_words = len(cleaned.split())
        if cleaned_words >= original_words * 0.5:  # Retained at least 50% words
            score += 0.1

        return min(1.0, max(0.0, score))

    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """Get detailed statistics about the text"""
        if not text:
            return {}

        words = text.split()
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "character_count": len(text),
            "character_count_no_spaces": len(text.replace(" ", "")),
            "average_words_per_sentence": (
                len(words) / len(sentences) if sentences else 0
            ),
            "longest_sentence": max(sentences, key=len) if sentences else "",
            "shortest_sentence": min(sentences, key=len) if sentences else "",
            "estimated_reading_time_minutes": len(words) / 200,  # Average reading speed
        }

    def suggest_improvements(self, processing_result: Dict[str, Any]) -> List[str]:
        """Suggest manual improvements based on processing results"""
        suggestions = []

        if processing_result["confidence_score"] < 0.5:
            suggestions.append(
                "⚠️ Low confidence score - please review the cleaned text carefully"
            )

        if processing_result["reduction_percentage"] > 40:
            suggestions.append(
                "📝 Large amount of content was removed - verify important information wasn't lost"
            )

        if processing_result["word_count_cleaned"] < 10:
            suggestions.append(
                "📏 Very short transcription - consider re-recording for better quality"
            )

        removed_count = len(processing_result["removed_elements"])
        if removed_count > processing_result["word_count_original"] * 0.3:
            suggestions.append(
                f"🔍 {removed_count} elements were removed - review for accuracy"
            )

        return suggestions
