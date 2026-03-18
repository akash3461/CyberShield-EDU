import pytesseract
from PIL import Image
import io
import os
from app.services.text_detector import text_detector
from app.utils.logger import logger

class ImageDetectorService:
    def __init__(self):
        # Configure tesseract path if needed for Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass

    async def analyze_screenshot(self, image_bytes: bytes):
        """Extracts text from an image and runs it through the text detector."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # OCR Extraction
            logger.info("Starting OCR extraction from image...")
            extracted_text = pytesseract.image_to_string(image)
            
            if not extracted_text.strip():
                return {
                    "prediction": "unknown",
                    "confidence": 0.0,
                    "reasoning": ["No readable text found in the image."],
                    "extracted_text": ""
                }

            logger.info(f"OCR Complete. Extracted {len(extracted_text)} chars.")
            
            # Forward to text detector
            result = await text_detector.analyze(extracted_text)
            result["source"] = "ocr_scan"
            result["extracted_text_preview"] = extracted_text[:200] + "..."
            
            return result

        except Exception as e:
            logger.error(f"OCR Analysis failed: {str(e)}")
            return {
                "prediction": "error",
                "confidence": 0.0,
                "reasoning": [f"Visual analysis failed: {str(e)}"],
                "extracted_text": ""
            }

image_detector = ImageDetectorService()
