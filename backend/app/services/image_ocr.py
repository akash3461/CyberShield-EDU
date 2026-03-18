import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import io
import cv2
import numpy as np
import re
from app.utils.logger import logger
from app.services.text_detector import text_detector
from app.services.url_detector import url_detector

class ImageOCRService:
    def __init__(self):
        # Configure tesseract path for Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Platform detection keywords
        self.platform_patterns = {
            "WhatsApp": [r"whatsapp", r"status", r"last seen", r"message"],
            "Telegram": [r"telegram", r"channel", r"group", r"join"],
            "Email": [r"from:", r"to:", r"subject:", r"reply"]
        }

    def detect_qr_codes(self, image_np):
        """Detects and decodes QR codes using OpenCV."""
        qr_detector = cv2.QRCodeDetector()
        data, _, _ = qr_detector.detectAndDecode(image_np)
        return data if data else None

    def apply_advanced_preprocessing(self, image_np):
        """Applies adaptive thresholding to handle various lighting/modes."""
        # Convert to grayscale if not already
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np
            
        # Apply median blur to reduce noise
        gray = cv2.medianBlur(gray, 3)
        
        # Apply adaptive thresholding (Gaussian)
        # This helps significantly with dark mode vs light mode
        processed = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        return processed

    def identify_platform(self, text: str) -> str:
        """Guesses the platform based on extracted text patterns."""
        lower_text = text.lower()
        for platform, patterns in self.platform_patterns.items():
            if any(re.search(p, lower_text) for p in patterns):
                return platform
        return "Unknown Platform"

    async def analyze(self, image_bytes: bytes, filename: str):
        logger.info(f"Analyzing Image with Advanced Vision: {filename}")
        
        reasoning = []
        risk_score = 0.0
        ai_analysis = None
        found_urls = []
        qr_data = None
        
        try:
            # 1. Load Image for CV2 and PIL
            nparr = np.frombuffer(image_bytes, np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # 2. QR Code Detection
            qr_data = self.detect_qr_codes(img_cv)
            if qr_data:
                logger.info(f"QR Code detected: {qr_data}")
                qr_url_res = await url_detector.analyze(qr_data)
                found_urls.append({
                    "type": "QR_CODE",
                    "url": qr_data,
                    "prediction": qr_url_res["prediction"]
                })
                reasoning.append(f"Hidden link detected in QR Code: {qr_data}")
                if qr_url_res["prediction"] == "scam":
                    risk_score += 0.5
                    reasoning.append("QR Code directs to a malicious/scam website.")

            # 3. Advanced OCR Pre-processing
            processed_cv = self.apply_advanced_preprocessing(img_cv)
            img_pil = Image.fromarray(processed_cv)
            
            # 4. OCR Extraction
            extracted_text = pytesseract.image_to_string(img_pil)
            
            if not extracted_text.strip():
                # Try fallback on original if pre-processing was too aggressive
                img_pil_orig = Image.open(io.BytesIO(image_bytes))
                extracted_text = pytesseract.image_to_string(img_pil_orig)

            if not extracted_text.strip() and not qr_data:
                return {
                    "prediction": "safe",
                    "confidence": 0.5,
                    "reasoning": ["No text or QR codes detected in the image."],
                    "metadata": {"filename": filename}
                }

            # 5. UI Platform Identification
            platform = self.identify_platform(extracted_text)
            if platform != "Unknown Platform":
                reasoning.append(f"Screenshot identified as: {platform}")

            # 6. AI Content Analysis (Phase 3 synergy)
            if extracted_text.strip():
                ai_res = await text_detector.analyze(extracted_text)
                ai_analysis = {
                    "prediction": ai_res["prediction"],
                    "confidence": ai_res["confidence"],
                    "reasoning": ai_res["reasoning"]
                }
                if ai_res["prediction"] == "scam":
                    risk_score += 0.4
                    reasoning.extend([f"AI Analysis: {r}" for r in ai_res["reasoning"]])

            # 7. URL Extraction from text
            text_urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', extracted_text)
            for url in set(text_urls):
                url_res = await url_detector.analyze(url)
                found_urls.append({
                    "type": "TEXT_LINK",
                    "url": url,
                    "prediction": url_res["prediction"]
                })
                if url_res["prediction"] == "scam":
                    risk_score += 0.4
                    reasoning.append(f"Phishing link found in screenshot text: {url}")

        except Exception as e:
            logger.error(f"Advanced Vision Analysis error: {str(e)}")
            return {"prediction": "error", "message": f"Vision processing failed: {str(e)}"}

        risk_score = min(1.0, risk_score)
        prediction = "scam" if risk_score >= 0.45 else "safe"
        
        return {
            "prediction": prediction,
            "confidence": float(1.0 - abs(0.45 - risk_score) * 2),
            "scam_score": float(risk_score),
            "reasoning": list(set(reasoning)),
            "platform": platform if 'platform' in locals() else "Unknown",
            "findings": {
                "qr_code": qr_data,
                "extracted_text_snippet": extracted_text[:300] if 'extracted_text' in locals() else "",
                "urls": found_urls
            },
            "ai_analysis": ai_analysis,
            "metadata": {"filename": filename}
        }

image_ocr = ImageOCRService()
