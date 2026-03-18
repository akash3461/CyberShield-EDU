import pdfplumber
import io
import re
from app.utils.logger import logger
from app.config import settings
from app.services.url_detector import url_detector

from app.services.text_detector import text_detector

class PDFAnalyzerService:
    def __init__(self):
        self.scam_keywords = settings.SCAM_KEYWORDS

    async def analyze(self, file_content: bytes, filename: str):
        logger.info(f"Analyzing PDF: {filename}")
        
        reasoning = []
        metadata = {}
        risk_score = 0.0
        keyword_hits = []
        found_urls = []
        ai_analysis = None

        try:
            # 1. Load PDF
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                # 2. Inspect Metadata
                metadata = pdf.metadata or {}
                author = metadata.get('Author', '').lower()
                
                if not author or author == "none":
                    risk_score += 0.05
                elif any(kw in author for kw in ["admin", "user", "root", "pc"]):
                    risk_score += 0.1
                    reasoning.append(f"Suspicious document author: {author}")

                # 3. Digital Signature Check (Simple Stream Inspection)
                # Looking for /Sig or /ByteRange which are indicators of signatures
                if b"/Sig" in file_content or b"/ByteRange" in file_content:
                    logger.info("Digital signature indicator found")
                    risk_score = max(0, risk_score - 0.2)
                    reasoning.append("Document appears to have a digital signature (Trust indicator)")
                else:
                    reasoning.append("No digital signature found. Use caution with official-looking offer letters.")

                # 4. Extract Text
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if not text.strip():
                    risk_score += 0.3
                    reasoning.append("PDF contains no extractable text (possible image-only scan or malicious container)")
                else:
                    # 5. AI Content Analysis (Phase 3 Synergy)
                    ai_res = await text_detector.analyze(text)
                    ai_analysis = {
                        "prediction": ai_res["prediction"],
                        "confidence": ai_res["confidence"],
                        "reasoning": ai_res["reasoning"]
                    }
                    
                    if ai_res["prediction"] == "scam":
                        risk_score += 0.4
                        reasoning.extend([f"AI Analysis: {r}" for r in ai_res["reasoning"]])

                    # 6. Keyword Detection (Heuristics)
                    clean_text = text.lower()
                    for kw in self.scam_keywords:
                        if kw in clean_text:
                            keyword_hits.append(kw)
                    
                    if keyword_hits and ai_res["prediction"] != "scam":
                        risk_score += 0.2
                        reasoning.append(f"Detected suspicious keywords: {', '.join(keyword_hits)}")

                    # 7. URL Extraction and Analysis
                    urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
                    for url in set(urls):
                        url_result = await url_detector.analyze(url)
                        found_urls.append({
                            "url": url,
                            "prediction": url_result["prediction"],
                            "score": url_result["scam_score"]
                        })
                        
                        if url_result["prediction"] == "scam":
                            risk_score += 0.4
                            reasoning.append(f"Malicious URL detected: {url}")

                # 8. Structural Anomalies
                page_count = len(pdf.pages)
                if page_count > 50:
                    risk_score += 0.1
                    reasoning.append(f"Unusually large document ({page_count} pages)")

        except Exception as e:
            logger.error(f"PDF Analysis error: {str(e)}")
            return {"prediction": "error", "message": f"Failed to process PDF: {str(e)}"}

        risk_score = min(1.0, risk_score)
        prediction = "scam" if risk_score >= 0.45 else "safe"
        
        return {
            "prediction": prediction,
            "confidence": float(1.0 - abs(0.45 - risk_score) * 2),
            "scam_score": float(risk_score),
            "reasoning": list(set(reasoning)), # De-duplicate
            "ai_analysis": ai_analysis,
            "metadata": {
                "filename": filename,
                "page_count": len(pdf.pages) if 'pdf' in locals() else 0,
                "found_urls_count": len(found_urls)
            },
            "url_analysis": found_urls[:5]
        }

pdf_analyzer = PDFAnalyzerService()
