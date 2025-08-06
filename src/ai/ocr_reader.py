# ocr_reader.py
import streamlit as st
from typing import Optional
import os
from PIL import Image

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    st.warning("Tesseract OCR not available")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

class OCRReader:
    def __init__(self):
        """Initialize OCR reader with available engines"""
        self.tesseract_available = TESSERACT_AVAILABLE
        self.easyocr_available = EASYOCR_AVAILABLE
        self.easyocr_reader = None
        
        # Set tesseract path if needed (adjust for your system)
        if self.tesseract_available:
            try:
                # Try common paths
                possible_paths = [
                    '/usr/bin/tesseract',
                    '/usr/local/bin/tesseract',
                    'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
                    'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
            except Exception:
                pass
    
    @st.cache_resource
    def _load_easyocr(_self):
        """Load EasyOCR reader (cached for performance)"""
        if not _self.easyocr_available:
            return None
        try:
            import easyocr
            # Load with common Indian languages
            return easyocr.Reader(['en', 'hi', 'te', 'ta', 'bn', 'mr', 'gu', 'kn', 'ml'])
        except Exception as e:
            st.warning(f"Failed to load EasyOCR: {str(e)}")
            return None
    
    def extract_text(self, image_path: str, language: str = 'eng') -> Optional[str]:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to image file
            language: Language code for OCR (tesseract format)
            
        Returns:
            Extracted text or None if failed
        """
        if not os.path.exists(image_path):
            st.error(f"Image file not found: {image_path}")
            return None
        
        try:
            # Try EasyOCR first (better for multilingual)
            if self.easyocr_available:
                text = self._extract_with_easyocr(image_path)
                if text and text.strip():
                    return text
            
            # Fall back to Tesseract
            if self.tesseract_available:
                text = self._extract_with_tesseract(image_path, language)
                if text and text.strip():
                    return text
            
            # Final fallback - simple text extraction attempt
            return self._basic_text_extraction(image_path)
            
        except Exception as e:
            st.error(f"OCR extraction failed: {str(e)}")
            return None
    
    def _extract_with_easyocr(self, image_path: str) -> Optional[str]:
        """Extract text using EasyOCR"""
        try:
            if self.easyocr_reader is None:
                self.easyocr_reader = self._load_easyocr()
            
            if self.easyocr_reader is None:
                return None
            
            results = self.easyocr_reader.readtext(image_path)
            
            # Combine all detected text
            extracted_texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Filter low confidence detections
                    extracted_texts.append(text)
            
            return '\n'.join(extracted_texts).strip()
            
        except Exception as e:
            st.warning(f"EasyOCR failed: {str(e)}")
            return None
    
    def _extract_with_tesseract(self, image_path: str, language: str = 'eng') -> Optional[str]:
        """Extract text using Tesseract OCR"""
        try:
            # Map common language codes to tesseract format
            lang_mapping = {
                'en': 'eng',
                'hi': 'hin',
                'te': 'tel', 
                'ta': 'tam',
                'bn': 'ben',
                'mr': 'mar',
                'gu': 'guj',
                'kn': 'kan',
                'ml': 'mal',
                'pa': 'pan'
            }
            
            tesseract_lang = lang_mapping.get(language, 'eng')
            
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text
            extracted_text = pytesseract.image_to_string(
                image, 
                lang=tesseract_lang,
                config='--psm 6'  # Uniform block of text
            )
            
            return extracted_text.strip()
            
        except Exception as e:
            st.warning(f"Tesseract OCR failed: {str(e)}")
            return None
    
    def _basic_text_extraction(self, image_path: str) -> str:
        """Basic fallback text extraction (placeholder)"""
        try:
            # This is a very basic fallback - in practice, you might want to
            # implement a more sophisticated approach or use cloud OCR APIs
            return "OCR extraction failed. Please try with a clearer image or install OCR dependencies."
        except Exception:
            return "Text extraction unavailable"
    
    def detect_text_regions(self, image_path: str) -> list:
        """
        Detect text regions in image
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of text regions with bounding boxes
        """
        try:
            if self.easyocr_available:
                if self.easyocr_reader is None:
                    self.easyocr_reader = self._load_easyocr()
                
                if self.easyocr_reader is not None:
                    results = self.easyocr_reader.readtext(image_path)
                    
                    regions = []
                    for (bbox, text, confidence) in results:
                        regions.append({
                            'bbox': bbox,
                            'text': text,
                            'confidence': confidence
                        })
                    
                    return regions
            
            return []
            
        except Exception as e:
            st.warning(f"Text region detection failed: {str(e)}")
            return []
    
    def preprocess_image_for_ocr(self, image_path: str, output_path: str = None) -> str:
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image_path: Path to input image
            output_path: Path for processed image (optional)
            
        Returns:
            Path to processed image
        """
        try:
            from PIL import Image, ImageEnhance, ImageFilter
            
            # Open image
            image = Image.open(image_path)
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Save processed image
            if output_path is None:
                output_path = image_path.replace('.', '_processed.')
            
            image.save(output_path)
            return output_path
            
        except Exception as e:
            st.warning(f"Image preprocessing failed: {str(e)}")
            return image_path  # Return original path if preprocessing fails
    
    def get_supported_languages(self) -> dict:
        """Get supported OCR languages"""
        return {
            'English': 'en',
            'Hindi': 'hi',
            'Telugu': 'te',
            'Tamil': 'ta',
            'Bengali': 'bn',
            'Marathi': 'mr',
            'Gujarati': 'gu',
            'Kannada': 'kn',
            'Malayalam': 'ml',
            'Punjabi': 'pa'
        }
    
    def is_available(self) -> bool:
        """Check if any OCR engine is available"""
        return self.tesseract_available or self.easyocr_available