import os
import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import io
import cv2
import numpy as np
import re
from app.utils.logger import logger
from app.services.text_detector import text_detector
from app.services.url_detector import url_detector

# --- Tesseract Self-Healing Path Detection ---
def configure_tesseract():
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Tesseract-OCR", "tesseract.exe")
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            logger.info(f"Forensic Component Calibrated: Tesseract found at {path}")
            return True
            
    # Fallback: check if 'tesseract' is already in PATH
    try:
        import subprocess
        subprocess.run(["tesseract", "--version"], capture_output=True)
        return True
    except:
        logger.warning("Forensic Pulse Lost: Tesseract OCR engine not found in common Windows paths or system PATH.")
        return False

# Initialize Engine
TESSERACT_ONLINE = configure_tesseract()

class ImageOCRService:
    def __init__(self):
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
        
        # 0. Health Check for OCR Engine
        if not TESSERACT_ONLINE:
            return {
                "prediction": "error",
                "confidence": 0.0,
                "recommendation": "Forensic OCR Engine (Tesseract) is not detected on your system.",
                "reasoning": [
                    "CRITICAL: Visual Audit Engine is currently OFFLINE.",
                    "RESOLUTION: Please download and install Tesseract for Windows.",
                    "DOWNLOAD LINK: https://github.com/UB-Mannheim/tesseract/wiki"
                ],
                "metadata": {"filename": filename, "error_type": "prerequisite_missing"}
            }

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

            # 8. Forensic Integrity Calculation
            exif_data = self._get_exif_metadata(image_bytes)
            noise_data = self._calculate_noise_integrity(img_cv)
            
            # Weighted Integrity Score
            integrity_score = (
                (0.4 * (1.0 if exif_data.get("trust_level") == "high" else 0.5)) +
                (0.4 * noise_data["score"]) +
                (0.2 * (1.0 if not exif_data.get("is_ai_gen") else 0.0))
            )

            risk_score = min(1.0, risk_score + (1.0 - integrity_score) * 0.5)
            prediction = "scam" if risk_score >= 0.45 else "safe"
            
            return {
                "prediction": prediction,
                "confidence": round(risk_score, 2),
                "ai_analysis": ai_analysis,
                "forensic_report": {
                    "integrity_score": round(integrity_score * 100, 1),
                    "metadata_trust": exif_data.get("trust_level"),
                    "texture_analysis": "Suspiciously Smooth" if noise_data["is_suspiciously_smooth"] else "Natural Texture",
                    "is_synthetic": exif_data.get("is_ai_gen", False) or noise_data["is_suspiciously_smooth"]
                },
                "metadata": {
                    "filename": filename,
                    "forensics": {
                        "exif": exif_data,
                        "noise": noise_data,
                        "platform_identified": platform if 'platform' in locals() else "Unknown",
                        "qr_detected": bool(qr_data)
                    }
                }
            }
        except Exception as e:
            logger.error(f"Image Forensic Audit Failed: {str(e)}")
            return {
                "prediction": "error",
                "confidence": 0.0,
                "reasoning": [f"Forensic engine encountered a technical blackout: {str(e)}"],
                "metadata": {"filename": filename}
            }

    def _get_exif_metadata(self, image_bytes: bytes) -> dict:
        """Extracts deep EXIF metadata to identify source and AI manipulation."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            exif = img._getexif()
            
            # Common EXIF Tag IDs
            TAGS = {
                271: "make",
                272: "model",
                305: "software",
                306: "datetime",
                274: "orientation",
                42033: "lens_model",
                34855: "iso",
                33434: "exposure_time"
            }
            
            if not exif:
                return {"status": "Suspicious: No Metadata Found", "trust_level": "low"}
            
            extracted = {TAGS.get(k, k): v for k, v in exif.items() if k in TAGS}
            
            # AI Signature Detection in Software/Model strings
            ai_keywords = ["stable diffusion", "midjourney", "firefly", "dalle", "canva", "photoshop ai"]
            software_str = str(extracted.get("software", "")).lower()
            model_str = str(extracted.get("model", "")).lower()
            
            is_ai_gen = any(k in software_str or k in model_str for k in ai_keywords)
            
            return {
                "tags": extracted,
                "status": "AI Signature Detected" if is_ai_gen else "Standard Metadata",
                "is_ai_gen": is_ai_gen,
                "trust_level": "high" if "make" in extracted else "medium"
            }
        except:
            return {"status": "Error reading EXIF", "trust_level": "low"}

    def _calculate_noise_integrity(self, image_np) -> dict:
        """Detects suspiciously uniform textures (AI skin) using Laplacian Variance."""
        try:
            if len(image_np.shape) == 3:
                gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
            else:
                gray = image_np
                
            # Laplacian variance is a measure of image 'edginess' or 'sharpness'
            # AI generated faces often have suspiciously smooth/low-variance patches
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Heuristic: Extremely low variance on high-res images can indicate synthetic smoothing
            is_suspiciously_smooth = variance < 100.0 
            
            return {
                "texture_variance": round(variance, 2),
                "is_suspiciously_smooth": is_suspiciously_smooth,
                "score": 1.0 if not is_suspiciously_smooth else 0.4
            }
        except:
            return {"score": 0.5, "error": "Noise analysis failed"}

    def _get_ocr_confidence(self, pil_img) -> float:
        """Calculates average confidence of the OCR extraction."""
        try:
            data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data['conf'] if int(c) != -1]
            if not confidences: return 0.0
            return sum(confidences) / len(confidences) / 100.0
        except:
            return 0.0

image_ocr = ImageOCRService()
