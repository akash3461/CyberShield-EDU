import pdfplumber
import io
import re
from app.utils.logger import logger
from app.config import settings
from app.services.url_detector import url_detector
from app.services.trust_service import trust_service
import asyncio

from app.services.text_detector import text_detector

class PDFAnalyzerService:
    def __init__(self):
        self.scam_keywords = settings.SCAM_KEYWORDS

    async def analyze(self, file_content: bytes, filename: str):
        logger.info(f"Analyzing PDF: {filename}")
        
        reasoning = []
        metadata = {}
        trust_info = None
        risk_score = 0.0
        keyword_hits = []
        found_urls = [] # Will store objects: {"url": str, "type": "visible"|"ghost"}
        ai_analysis = None

        try:
            # 1. Check for Encryption (Pre-parse)
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                # Stable encryption check
                is_encrypted = False
                try:
                    is_encrypted = pdf.doc.encryption is not None
                except:
                    pass

                if is_encrypted:
                    logger.warning(f"Encrypted PDF detected: {filename}")
                    return {
                        "prediction": "scam",
                        "confidence": 0.8,
                        "scam_score": 0.7,
                        "reasoning": ["Document is password protected. Scammers often encrypt files to bypass security scanners."],
                        "metadata": {"filename": filename, "is_encrypted": True, "page_count": 0}
                    }

                # 2. Inspect Metadata
                metadata = pdf.metadata or {}
                author = metadata.get('Author', '').lower()
                
                if not author or author == "none":
                    risk_score += 0.5
                else:
                    # Check Shield of Trust for author/domain
                    trust_info = trust_service.check_domain(author)
                    if trust_info:
                        risk_score = max(0, risk_score - 0.3)
                        reasoning.append(f"🛡️ Shield of Trust: Verified Document Author ({trust_info['name']})")
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

                    # 7. Recursive URL & Annotation Extraction (Pillar 8: Deep Structural Audit)
                    visible_urls = set(re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text))
                    ghost_urls = set()
                    
                    # Extract Hidden Links (Annotations)
                    for page in pdf.pages:
                        if hasattr(page, 'annots') and page.annots:
                            for annot in page.annots:
                                uri = annot.get('uri')
                                if uri and uri.startswith('http'):
                                    if uri not in visible_urls:
                                        ghost_urls.add(uri)
                    
                    # Merge and tag (Top 10 prioritizing ghost links for forensics)
                    analysis_queue = []
                    for u in list(ghost_urls)[:10]:
                        analysis_queue.append({"url": u, "type": "ghost"})
                    for u in list(visible_urls)[:max(0, 10 - len(analysis_queue))]:
                        analysis_queue.append({"url": u, "type": "visible"})
                    
                    if analysis_queue:
                        tasks = [url_detector.analyze(item["url"]) for item in analysis_queue]
                        try:
                            # Added 10s safety timeout to prevent document hang on bad links
                            url_results = await asyncio.wait_for(
                                asyncio.gather(*tasks, return_exceptions=True),
                                timeout=10.0
                            )
                            
                            for item, result in zip(analysis_queue, url_results):
                                if isinstance(result, Exception):
                                    logger.error(f"Recursive scan failed for {item['url']}: {str(result)}")
                                    continue
                                    
                                found_urls.append({
                                    "url": item["url"],
                                    "type": item["type"],
                                    "prediction": result["prediction"],
                                    "score": result["scam_score"],
                                    "forensics": result.get("forensics", {}),
                                    "redirect_chain": result.get("redirect_chain", [])
                                })
                                
                                # Elevate risk for Ghost-Links linking to SCAM or high-entropy
                                if item["type"] == "ghost":
                                    risk_score += 0.15
                                    reasoning.append(f"Ghost-Link Detected: Hidden structural URI identified ({item['url']})")
                                
                                if result["prediction"] == "scam":
                                    risk_score += 0.4
                                    reasoning.append(f"High-Risk URL detected inside PDF: {item['url']}")
                        except asyncio.TimeoutError:
                            logger.warning("Recursive URL audit timed out - finishing report with available data.")
                            reasoning.append("Warning: Some internal links were slow to respond and were skipped for speed.")

                # 8. Multi-Modal Correlation
                from app.services.correlation_service import correlation_service
                
                # Prepare findings for correlation
                # Check for intents and categories from the AI Text Analysis
                intents = ai_res.get("intents", []) if ai_analysis else []
                categories = ai_res.get("categories", []) if ai_analysis else []
                
                # Add "Official" intent if Author was unverified but signature missing
                if metadata.get('Author') and not trust_info:
                    intents.append("OFFICIAL")

                findings = {
                    "intents": list(set(intents)),
                    "categories": list(set(categories)),
                    "platform": "Unknown", # PDFs are cross-platform
                    "url_status": "suspicious" if any(u["prediction"] == "scam" for u in found_urls) else "safe",
                    "metadata_trust": trust_info.get("trust_level", "medium") if trust_info else "low"
                }
                
                correlation = correlation_service.evaluate(findings)
                risk_score = min(1.0, risk_score + correlation["boost"])
                reasoning.extend(correlation["reasons"])

                # 9. Structural Anomalies
                page_count = len(pdf.pages)
                if page_count > 10:
                    risk_score += 0.1
                    reasoning.append(f"Unusually large document ({page_count} pages)")

        except Exception as e:
            logger.error(f"PDF Analysis error: {str(e)}")
            return {
                "prediction": "error", 
                "confidence": 0.0,
                "scam_score": 0.0,
                "reasoning": [f"Failed to process PDF: {str(e)}"],
                "message": f"Critical Forensic Error: {str(e)}"
            }

        # New: Tri-state prediction logic from DB Config
        from app.utils.config_helper import config_helper
        thresholds = config_helper.get_thresholds()
        low_t = thresholds.get("low", 0.3)
        high_t = thresholds.get("high", 0.7)

        if risk_score >= high_t:
            prediction = "scam"
        elif risk_score >= low_t:
            prediction = "suspicious"
        else:
            prediction = "safe"
            
        return {
            "prediction": prediction,
            "confidence": float(risk_score),
            "scam_score": float(risk_score),
            "reasoning": list(set(reasoning)), # De-duplicate
            "correlation_report": correlation,
            "ai_analysis": ai_analysis,
            "metadata": {
                "filename": filename,
                "forensics": {
                    "author": metadata.get('Author', 'Unknown'),
                    "creator_tool": metadata.get('Creator', 'Unknown'),
                    "producer": metadata.get('Producer', 'Unknown'),
                    "creation_date": metadata.get('CreationDate', 'Unknown'),
                    "is_encrypted": metadata.get('Encrypt', False),
                    "is_digitally_signed": b"/Sig" in file_content or b"/ByteRange" in file_content,
                    "trust_info": trust_info
                },
                "page_count": len(pdf.pages) if 'pdf' in locals() else 0,
                "found_urls_count": len(found_urls)
            },
            "url_analysis": found_urls[:5]
        }

pdf_analyzer = PDFAnalyzerService()

