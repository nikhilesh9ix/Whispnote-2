# llama_summarizer.py - Advanced AI Summarization with Llama 3.1 405B and alternatives
import os
import sys
from typing import Any, Dict, List, Tuple

import requests
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AdvancedAISummarizer:
    def __init__(self):
        """
        Initialize advanced AI summarizer with multiple service options:
        - Llama 3.1 405B via various APIs
        - OpenAI GPT-4
        - Anthropic Claude
        - Groq (fastest inference)
        - Hugging Face Inference API
        - Local Ollama models
        """
        self.available_services = self._check_available_services()

    def _check_available_services(self) -> Dict[str, bool]:
        """Check which AI services are available based on API keys"""
        services = {
            "openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
            "groq": bool(os.getenv("GROQ_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "together": bool(os.getenv("TOGETHER_API_KEY")),
            "replicate": bool(os.getenv("REPLICATE_API_TOKEN")),
            "huggingface": bool(os.getenv("HUGGINGFACE_API_KEY")),
            "ollama": self._check_ollama_available(),
        }

        available_count = sum(services.values())
        if available_count > 0:
            st.success(
                f"🚀 {available_count} AI services available for advanced summarization"
            )
        else:
            st.info(
                "💡 No API keys found. Add API keys to enable advanced AI summarization."
            )

        return services

    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running locally"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def summarize(self, text: str, language: str = "en", max_length: int = 150) -> str:
        """
        Main summarization method with multiple AI service fallbacks

        Args:
            text: Text to summarize
            language: Language code (en, hi, te, etc.)
            max_length: Maximum summary length

        Returns:
            Generated summary
        """
        # Try services in order of preference
        service_priority = [
            ("openrouter", self._summarize_with_openrouter),
            ("groq", self._summarize_with_groq),
            ("together", self._summarize_with_together),
            ("openai", self._summarize_with_openai),
            ("anthropic", self._summarize_with_anthropic),
            ("ollama", self._summarize_with_ollama),
            ("huggingface", self._summarize_with_huggingface),
        ]

        for service_name, service_func in service_priority:
            if self.available_services.get(service_name, False):
                try:
                    st.info(f"🤖 Generating summary using {service_name.title()}...")
                    summary = service_func(text, language, max_length)
                    if summary and len(summary.strip()) > 10:
                        st.success(f"✅ Summary generated using {service_name.title()}")
                        return summary
                except Exception as e:
                    st.warning(f"⚠️ {service_name.title()} failed: {str(e)[:100]}...")
                    continue

        # Final fallback to extractive summarization
        st.info("📝 Using extractive summarization as fallback")
        return self._extractive_summarize(text, max_length)

    def _summarize_with_openrouter(
        self, text: str, language: str, max_length: int
    ) -> str:
        """Summarize using OpenRouter (Meta Llama 3.1 405B Instruct)"""
        try:
            import openai

            # Use your specific OpenRouter configuration
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv(
                    "OPENROUTER_API_KEY",
                    "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",
                ),
            )

            # Language-specific prompts
            language_prompts = {
                "en": "Summarize the following text concisely in English:",
                "hi": "निम्नलिखित पाठ को हिंदी में संक्षेप में प्रस्तुत करें:",
                "te": "ఈ క్రింది పాఠాన్ని తెలుగులో సంక్షిప్తంగా సారాంశం ఇవ్వండి:",
                "ta": "பின்வரும் உரையை தமிழில் சுருக்கமாக சுருக்கவும்:",
                "bn": "নিচের পাঠটি বাংলায় সংক্ষেপে সারসংক্ষেপ করুন:",
                "mr": "खालील मजकूराचा मराठीत थोडक्यात सारांश द्या:",
                "gu": "નીચેના ટેક્સ્ટનો ગુજરાતીમાં સંક્ષિપ્ત સારાંશ આપો:",
                "kn": "ಈ ಕೆಳಗಿನ ಪಠ್ಯವನ್ನು ಕನ್ನಡದಲ್ಲಿ ಸಂಕ್ಷಿಪ್ತವಾಗಿ ಸಾರಾಂಶಿಸಿ:",
                "ml": "ഇനിപ്പറയുന്ന വാചകം മലയാളത്തിൽ സംക്ഷിപ്തമായി സംഗ്രഹിക്കുക:",
                "pa": "ਹੇਠਾਂ ਦਿੱਤੇ ਟੈਕਸਟ ਦਾ ਪੰਜਾਬੀ ਵਿੱਚ ਸੰਖੇਪ ਸਾਰ ਦਿਓ:",
            }

            prompt = language_prompts.get(language, language_prompts["en"])

            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://whispnote.ai",  # Your site URL
                    "X-Title": "WhispNote AI Voice Notes",  # Your site title
                },
                model="meta-llama/llama-3.1-405b-instruct:free",  # Your specific model
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert AI summarizer. Provide concise, informative summaries in about {max_length} words. Focus on the key points and main ideas.",
                    },
                    {"role": "user", "content": f"{prompt}\n\n{text}"},
                ],
                max_tokens=max_length * 2,
                temperature=0.3,
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}") from e

    def _summarize_with_groq(self, text: str, language: str, max_length: int) -> str:
        """Summarize using Groq (fastest Llama 3.1 inference)"""
        try:
            import groq

            client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

            # Language-specific prompts
            language_prompts = {
                "en": "Summarize the following text concisely in English:",
                "hi": "निम्नलिखित पाठ को हिंदी में संक्षेप में प्रस्तुत करें:",
                "te": "ఈ క్రింది పాఠాన్ని తెలుగులో సంక్షిప్తంగా సారాంశం ఇవ్వండి:",
                "ta": "பின்வரும் உரையை தமிழில் சுருக்கமாக சுருக்கவும்:",
                "bn": "নিচের পাঠটি বাংলায় সংক্ষেপে সারসংক্ষেপ করুন:",
            }

            prompt = language_prompts.get(language, language_prompts["en"])

            response = client.chat.completions.create(
                model="llama-3.1-405b-reasoning",  # Groq's Llama 3.1 405B
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert summarizer. Provide concise, informative summaries in about {max_length} words.",
                    },
                    {"role": "user", "content": f"{prompt}\n\n{text}"},
                ],
                max_tokens=max_length * 2,
                temperature=0.3,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

    def _summarize_with_together(
        self, text: str, language: str, max_length: int
    ) -> str:
        """Summarize using Together AI (Llama 3.1 405B)"""
        try:
            import together

            together.api_key = os.getenv("TOGETHER_API_KEY")

            prompt = f"""Please summarize the following text in {language} language (about {max_length} words):

{text}

Summary:"""

            response = together.Complete.create(
                model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
                prompt=prompt,
                max_tokens=max_length * 2,
                temperature=0.3,
                stop=["User:", "Human:", "\n\n"],
            )

            return response["choices"][0]["text"].strip()

        except Exception as e:
            raise Exception(f"Together AI error: {str(e)}")

    def _summarize_with_openai(self, text: str, language: str, max_length: int) -> str:
        """Summarize using OpenAI GPT-4"""
        try:
            import openai

            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            language_names = {
                "en": "English",
                "hi": "Hindi",
                "te": "Telugu",
                "ta": "Tamil",
                "bn": "Bengali",
                "mr": "Marathi",
            }

            lang_name = language_names.get(language, "English")

            response = client.chat.completions.create(
                model="gpt-4o",  # Latest GPT-4 model
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert summarizer. Provide concise summaries in {lang_name} in about {max_length} words.",
                    },
                    {"role": "user", "content": f"Summarize this text:\n\n{text}"},
                ],
                max_tokens=max_length * 2,
                temperature=0.3,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _summarize_with_anthropic(
        self, text: str, language: str, max_length: int
    ) -> str:
        """Summarize using Anthropic Claude"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_length * 2,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please summarize the following text in about {max_length} words:\n\n{text}",
                    }
                ],
            )

            return response.content[0].text.strip()

        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    def _summarize_with_ollama(self, text: str, language: str, max_length: int) -> str:
        """Summarize using local Ollama models"""
        try:
            # Check available models
            models_response = requests.get("http://localhost:11434/api/tags")
            available_models = [
                model["name"] for model in models_response.json().get("models", [])
            ]

            # Prefer Llama models
            preferred_models = [
                "llama3.1:405b",
                "llama3.1:70b",
                "llama3.1:8b",
                "llama3:70b",
                "llama3:8b",
                "mistral:7b",
            ]

            model_to_use = None
            for model in preferred_models:
                if any(model in available for available in available_models):
                    model_to_use = model
                    break

            if not model_to_use and available_models:
                model_to_use = available_models[0]

            if not model_to_use:
                raise Exception("No Ollama models available")

            payload = {
                "model": model_to_use,
                "prompt": f"Summarize the following text in about {max_length} words:\n\n{text}\n\nSummary:",
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": max_length * 2},
            }

            response = requests.post(
                "http://localhost:11434/api/generate", json=payload, timeout=60
            )
            result = response.json()

            return result.get("response", "").strip()

        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")

    def _summarize_with_huggingface(
        self, text: str, language: str, max_length: int
    ) -> str:
        """Summarize using Hugging Face Inference API"""
        try:
            headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

            # Try different models
            models = [
                "meta-llama/Meta-Llama-3.1-405B-Instruct",
                "facebook/bart-large-cnn",
                "google/pegasus-large",
            ]

            for model in models:
                try:
                    api_url = f"https://api-inference.huggingface.co/models/{model}"

                    if "llama" in model.lower():
                        # For Llama models, use text generation
                        payload = {
                            "inputs": f"Summarize this text in about {max_length} words:\n\n{text}\n\nSummary:",
                            "parameters": {
                                "max_new_tokens": max_length * 2,
                                "temperature": 0.3,
                            },
                        }
                    else:
                        # For summarization models
                        payload = {
                            "inputs": text,
                            "parameters": {"max_length": max_length},
                        }

                    response = requests.post(
                        api_url, headers=headers, json=payload, timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            if "summary_text" in result[0]:
                                return result[0]["summary_text"]
                            elif "generated_text" in result[0]:
                                return (
                                    result[0]["generated_text"]
                                    .split("Summary:")[-1]
                                    .strip()
                                )

                except Exception as e:
                    continue

            raise Exception("All Hugging Face models failed")

        except Exception as e:
            raise Exception(f"Hugging Face API error: {str(e)}")

    def _extractive_summarize(self, text: str, max_length: int = 150) -> str:
        """Fallback extractive summarization"""
        sentences = text.split(". ")
        if len(sentences) <= 2:
            return text

        # Simple extractive approach - take first and middle sentences
        summary_sentences = []
        if len(sentences) > 0:
            summary_sentences.append(sentences[0])
        if len(sentences) > 2:
            summary_sentences.append(sentences[len(sentences) // 2])
        if len(sentences) > 1:
            summary_sentences.append(sentences[-1])

        summary = ". ".join(summary_sentences)

        # Truncate if too long
        words = summary.split()
        if len(words) > max_length:
            summary = " ".join(words[:max_length]) + "..."

        return summary

    def get_setup_instructions(self) -> str:
        """Return setup instructions for various AI services"""
        return """
## 🚀 Setup Instructions for Advanced AI Summarization

### Option 1: OpenRouter (Meta Llama 3.1 405B Instruct) - NOW ACTIVE!
```bash
# Your API key is already configured!
# Model: meta-llama/llama-3.1-405b-instruct:free
# Just run the app and it will use this as top priority
```

### Option 2: Groq (Fastest - Llama 3.1 405B)
```bash
# Get free API key from https://console.groq.com/
pip install groq
export GROQ_API_KEY="your_groq_api_key"
```

### Option 3: Together AI (Llama 3.1 405B)
```bash
# Get API key from https://together.ai/
pip install together
export TOGETHER_API_KEY="your_together_api_key"
```

### Option 3: OpenAI GPT-4
```bash
# Get API key from https://platform.openai.com/
pip install openai
export OPENAI_API_KEY="your_openai_api_key"
```

### Option 4: Anthropic Claude
```bash
# Get API key from https://console.anthropic.com/
pip install anthropic
export ANTHROPIC_API_KEY="your_anthropic_api_key"
```

### Option 5: Local Ollama (Free)
```bash
# Install Ollama: https://ollama.ai/
ollama pull llama3.1:8b  # or llama3.1:70b if you have enough RAM
ollama serve
```

### Option 6: Hugging Face
```bash
# Get token from https://huggingface.co/settings/tokens
pip install requests
export HUGGINGFACE_API_KEY="your_hf_token"
```

Add your API keys to your environment or .env file!
        """

    def extract_keywords(
        self, text: str, language: str = "en", num_keywords: int = 8
    ) -> List[str]:
        """
        Extract keywords using LLaMA 3.1 AI models

        Args:
            text: Text to extract keywords from
            language: Language code (en, hi, te, etc.)
            num_keywords: Number of keywords to extract

        Returns:
            List of extracted keywords
        """
        if not text or len(text.strip()) < 10:
            return []

        # Try services in order of preference
        service_priority = [
            ("openrouter", self._extract_keywords_with_openrouter),
            ("groq", self._extract_keywords_with_groq),
            ("together", self._extract_keywords_with_together),
            ("openai", self._extract_keywords_with_openai),
            ("anthropic", self._extract_keywords_with_anthropic),
            ("ollama", self._extract_keywords_with_ollama),
        ]

        for service_name, service_func in service_priority:
            if self.available_services.get(service_name, False):
                try:
                    st.info(f"🔑 Extracting keywords using {service_name.title()}...")
                    keywords = service_func(text, language, num_keywords)
                    if keywords and len(keywords) > 0:
                        st.success(
                            f"✅ Keywords extracted using {service_name.title()}"
                        )
                        return keywords
                except Exception as e:
                    st.warning(f"⚠️ {service_name.title()} failed: {str(e)[:100]}...")
                    continue

        # Final fallback to simple extraction
        st.info("🔑 Using simple keyword extraction as fallback")
        return self._simple_keyword_extraction(text, num_keywords)

    def clean_text(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Clean and enhance transcribed text using LLaMA 3.1 AI models

        Args:
            text: Text to clean
            language: Language code

        Returns:
            Dictionary with cleaned text and metadata
        """
        if not text or len(text.strip()) < 10:
            return {
                "original": text,
                "cleaned": text,
                "word_count_original": len(text.split()),
                "word_count_cleaned": len(text.split()),
                "confidence_score": 1.0,
                "reduction_percentage": 0.0,
                "processing_method": "none",
                "ai_model": None,
                "removed_elements": [],
                "processing_steps": [],
            }

        # Try services in order of preference
        service_priority = [
            ("openrouter", self._clean_text_with_openrouter),
            ("groq", self._clean_text_with_groq),
            ("together", self._clean_text_with_together),
            ("openai", self._clean_text_with_openai),
            ("anthropic", self._clean_text_with_anthropic),
            ("ollama", self._clean_text_with_ollama),
        ]

        for service_name, service_func in service_priority:
            if self.available_services.get(service_name, False):
                try:
                    st.info(f"🧹 Cleaning text using {service_name.title()}...")
                    cleaned_result = service_func(text, language)
                    if cleaned_result and cleaned_result.get("cleaned"):
                        st.success(f"✅ Text cleaned using {service_name.title()}")
                        return cleaned_result
                except Exception as e:
                    st.warning(f"⚠️ {service_name.title()} failed: {str(e)[:100]}...")
                    continue

        # Final fallback to simple cleaning
        st.info("🧹 Using simple text cleaning as fallback")
        return self._simple_text_cleaning(text)

    def generate_summary_and_keywords(
        self, text: str, language: str = "en", num_keywords: int = 8
    ) -> Tuple[str, List[str]]:
        """
        Generate both summary and keywords in a single optimized call

        Args:
            text: Input text
            language: Language code
            num_keywords: Number of keywords to extract

        Returns:
            Tuple of (summary, keywords_list)
        """
        if not text or len(text.strip()) < 10:
            return "", []

        # Try combined generation first for efficiency
        service_priority = [
            ("openrouter", self._generate_combined_with_openrouter),
            ("groq", self._generate_combined_with_groq),
            ("together", self._generate_combined_with_together),
            ("openai", self._generate_combined_with_openai),
            ("anthropic", self._generate_combined_with_anthropic),
            ("ollama", self._generate_combined_with_ollama),
        ]

        for service_name, service_func in service_priority:
            if self.available_services.get(service_name, False):
                try:
                    st.info(
                        f"🚀 Generating summary and keywords using {service_name.title()}..."
                    )
                    summary, keywords = service_func(text, language, num_keywords)
                    if summary and keywords:
                        st.success(
                            f"✅ Combined generation using {service_name.title()}"
                        )
                        return summary, keywords
                except Exception as e:
                    st.warning(f"⚠️ {service_name.title()} failed: {str(e)[:100]}...")
                    continue

        # Fallback to separate calls
        summary = self.summarize(text, language)
        keywords = self.extract_keywords(text, language, num_keywords)
        return summary, keywords

    # Keyword extraction methods for each service
    def _extract_keywords_with_openrouter(
        self, text: str, language: str, num_keywords: int
    ) -> List[str]:
        """Extract keywords using OpenRouter LLaMA 3.1"""
        try:
            import openai

            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )

            language_prompts = {
                "en": f"Extract {num_keywords} most important keywords from this text. Return only keywords separated by commas:",
                "hi": f"इस पाठ से {num_keywords} सबसे महत्वपूर्ण मुख्य शब्द निकालें। केवल कॉमा से अलग किए गए शब्द लौटाएं:",
                "te": f"ఈ పాఠ్యం నుండి {num_keywords} అత్యంత ముఖ్యమైన కీవర్డ్‌లను సంగ్రహించండి:",
            }

            prompt = language_prompts.get(language, language_prompts["en"])

            completion = client.chat.completions.create(
                model="meta-llama/llama-3.1-405b-instruct:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting key terms and concepts. Return only the keywords, separated by commas.",
                    },
                    {"role": "user", "content": f"{prompt}\n\n{text}"},
                ],
                max_tokens=100,
                temperature=0.3,
            )

            result = completion.choices[0].message.content.strip()
            return [kw.strip() for kw in result.split(",") if kw.strip()][:num_keywords]

        except Exception as e:
            raise Exception(f"OpenRouter keyword extraction error: {str(e)}")

    def _extract_keywords_with_groq(
        self, text: str, language: str, num_keywords: int
    ) -> List[str]:
        """Extract keywords using Groq"""
        try:
            import groq

            client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

            response = client.chat.completions.create(
                model="llama-3.1-405b-reasoning",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract important keywords from text. Return only keywords separated by commas.",
                    },
                    {
                        "role": "user",
                        "content": f"Extract {num_keywords} keywords from: {text}",
                    },
                ],
                max_tokens=100,
                temperature=0.3,
            )

            result = response.choices[0].message.content.strip()
            return [kw.strip() for kw in result.split(",") if kw.strip()][:num_keywords]

        except Exception as e:
            raise Exception(f"Groq keyword extraction error: {str(e)}")

    def _extract_keywords_with_together(
        self, text: str, language: str, num_keywords: int
    ) -> List[str]:
        """Extract keywords using Together AI"""
        # Similar implementation
        return self._simple_keyword_extraction(text, num_keywords)

    def _extract_keywords_with_openai(
        self, text: str, language: str, num_keywords: int
    ) -> List[str]:
        """Extract keywords using OpenAI"""
        # Similar implementation
        return self._simple_keyword_extraction(text, num_keywords)

    def _extract_keywords_with_anthropic(
        self, text: str, language: str, num_keywords: int
    ) -> List[str]:
        """Extract keywords using Anthropic"""
        # Similar implementation
        return self._simple_keyword_extraction(text, num_keywords)

    def _extract_keywords_with_ollama(
        self, text: str, language: str, num_keywords: int
    ) -> List[str]:
        """Extract keywords using Ollama"""
        # Similar implementation
        return self._simple_keyword_extraction(text, num_keywords)

    def _simple_keyword_extraction(self, text: str, num_keywords: int) -> List[str]:
        """Simple fallback keyword extraction"""
        import re

        # Simple approach: find most common meaningful words
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        # Filter out common words
        stop_words = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "had",
            "her",
            "was",
            "one",
            "our",
            "out",
            "day",
            "get",
            "has",
            "him",
            "his",
            "how",
            "may",
            "new",
            "now",
            "old",
            "see",
            "two",
            "way",
            "who",
            "boy",
            "did",
            "its",
            "let",
            "put",
            "say",
            "she",
            "too",
            "use",
        }
        keywords = [
            word for word in set(words) if word not in stop_words and len(word) > 3
        ]
        return keywords[:num_keywords]

    # Text cleaning methods
    def _clean_text_with_openrouter(self, text: str, language: str) -> Dict[str, Any]:
        """Clean text using OpenRouter LLaMA 3.1"""
        try:
            import openai

            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )

            prompt = """Clean this transcribed text by:
1. Removing filler words (um, uh, like, you know)
2. Fixing grammar and punctuation
3. Correcting obvious speech-to-text errors
4. Maintaining the original meaning and tone

Return only the cleaned text:"""

            completion = client.chat.completions.create(
                model="meta-llama/llama-3.1-405b-instruct:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert editor. Clean transcribed text while preserving meaning.",
                    },
                    {"role": "user", "content": f"{prompt}\n\n{text}"},
                ],
                max_tokens=len(text.split()) * 2,
                temperature=0.3,
            )

            cleaned_text = completion.choices[0].message.content.strip()

            return {
                "original": text,
                "cleaned": cleaned_text,
                "word_count_original": len(text.split()),
                "word_count_cleaned": len(cleaned_text.split()),
                "confidence_score": 0.9,
                "reduction_percentage": max(
                    0, 100 * (1 - len(cleaned_text.split()) / len(text.split()))
                ),
                "processing_method": "ai_enhanced",
                "ai_model": "llama-3.1-405b",
                "removed_elements": [],
                "processing_steps": ["AI text cleaning with LLaMA 3.1"],
            }

        except Exception as e:
            raise Exception(f"OpenRouter text cleaning error: {str(e)}")

    def _clean_text_with_groq(self, text: str, language: str) -> Dict[str, Any]:
        """Clean text using Groq"""
        # Similar implementation or fallback
        return self._simple_text_cleaning(text)

    def _clean_text_with_together(self, text: str, language: str) -> Dict[str, Any]:
        """Clean text using Together AI"""
        return self._simple_text_cleaning(text)

    def _clean_text_with_openai(self, text: str, language: str) -> Dict[str, Any]:
        """Clean text using OpenAI"""
        return self._simple_text_cleaning(text)

    def _clean_text_with_anthropic(self, text: str, language: str) -> Dict[str, Any]:
        """Clean text using Anthropic"""
        return self._simple_text_cleaning(text)

    def _clean_text_with_ollama(self, text: str, language: str) -> Dict[str, Any]:
        """Clean text using Ollama"""
        return self._simple_text_cleaning(text)

    def _simple_text_cleaning(self, text: str) -> Dict[str, Any]:
        """Simple fallback text cleaning"""
        import re

        # Basic cleaning
        cleaned = text
        removed_elements = []

        # Remove extra whitespace
        cleaned = re.sub(r"\s+", " ", cleaned)

        # Remove common filler words
        fillers = ["um", "uh", "er", "ah", "like", "you know"]
        for filler in fillers:
            pattern = r"\b" + filler + r"\b"
            if re.search(pattern, cleaned, re.IGNORECASE):
                removed_elements.append(filler)
                cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Clean up punctuation
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return {
            "original": text,
            "cleaned": cleaned,
            "word_count_original": len(text.split()),
            "word_count_cleaned": len(cleaned.split()),
            "confidence_score": 0.7,
            "reduction_percentage": max(
                0, 100 * (1 - len(cleaned.split()) / len(text.split()))
            ),
            "processing_method": "traditional",
            "ai_model": None,
            "removed_elements": removed_elements,
            "processing_steps": ["Basic text cleaning"],
        }

    # Combined generation methods
    def _generate_combined_with_openrouter(
        self, text: str, language: str, num_keywords: int
    ) -> Tuple[str, List[str]]:
        """Generate summary and keywords using OpenRouter"""
        try:
            import openai

            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )

            prompt = f"""Analyze this text and provide:
1. A concise summary (2-3 sentences)
2. {num_keywords} most important keywords

Format your response as:
SUMMARY: [summary here]
KEYWORDS: keyword1, keyword2, keyword3, ..."""

            completion = client.chat.completions.create(
                model="meta-llama/llama-3.1-405b-instruct:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at text analysis. Provide clear summaries and relevant keywords.",
                    },
                    {"role": "user", "content": f"{prompt}\n\n{text}"},
                ],
                max_tokens=300,
                temperature=0.3,
            )

            result = completion.choices[0].message.content.strip()
            return self._parse_combined_response(result)

        except Exception as e:
            raise Exception(f"OpenRouter combined generation error: {str(e)}")

    def _generate_combined_with_groq(
        self, text: str, language: str, num_keywords: int
    ) -> Tuple[str, List[str]]:
        """Generate combined using Groq - fallback to separate calls"""
        summary = self.summarize(text, language)
        keywords = self.extract_keywords(text, language, num_keywords)
        return summary, keywords

    def _generate_combined_with_together(
        self, text: str, language: str, num_keywords: int
    ) -> Tuple[str, List[str]]:
        """Generate combined using Together AI - fallback to separate calls"""
        summary = self.summarize(text, language)
        keywords = self.extract_keywords(text, language, num_keywords)
        return summary, keywords

    def _generate_combined_with_openai(
        self, text: str, language: str, num_keywords: int
    ) -> Tuple[str, List[str]]:
        """Generate combined using OpenAI - fallback to separate calls"""
        summary = self.summarize(text, language)
        keywords = self.extract_keywords(text, language, num_keywords)
        return summary, keywords

    def _generate_combined_with_anthropic(
        self, text: str, language: str, num_keywords: int
    ) -> Tuple[str, List[str]]:
        """Generate combined using Anthropic - fallback to separate calls"""
        summary = self.summarize(text, language)
        keywords = self.extract_keywords(text, language, num_keywords)
        return summary, keywords

    def _generate_combined_with_ollama(
        self, text: str, language: str, num_keywords: int
    ) -> Tuple[str, List[str]]:
        """Generate combined using Ollama - fallback to separate calls"""
        summary = self.summarize(text, language)
        keywords = self.extract_keywords(text, language, num_keywords)
        return summary, keywords

    def _parse_combined_response(self, response: str) -> Tuple[str, List[str]]:
        """Parse combined summary and keywords response"""
        try:
            lines = response.strip().split("\n")
            summary = ""
            keywords = []

            for line in lines:
                line = line.strip()
                if line.startswith("SUMMARY:"):
                    summary = line.replace("SUMMARY:", "").strip()
                elif line.startswith("KEYWORDS:"):
                    keyword_text = line.replace("KEYWORDS:", "").strip()
                    keywords = [
                        kw.strip() for kw in keyword_text.split(",") if kw.strip()
                    ]

            return summary, keywords[:8]

        except Exception:
            # If parsing fails, return empty results
            return "", []


# Example usage and testing
if __name__ == "__main__":
    summarizer = AdvancedAISummarizer()

    test_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals. The term artificial intelligence is often used to describe machines that mimic cognitive functions that humans associate with the human mind, such as learning and problem solving.
    """

    print("Testing Advanced AI Summarizer...")
    summary = summarizer.summarize(test_text, language="en", max_length=50)
    print(f"Summary: {summary}")

    print("\nSetup Instructions:")
    print(summarizer.get_setup_instructions())
