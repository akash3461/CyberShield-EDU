from transformers import pipeline
from app.utils.logger import logger
from app.utils.text_cleaner import clean_text, extract_metadata
from app.config import settings
import torch

class TextDetectorService:
    def __init__(self):
        self._classifier = None
        self.scam_keywords = settings.SCAM_KEYWORDS

    @property
    def classifier(self):
        if self._classifier is None:
            logger.info("Initializing TextDetectorService with Multilingual DistilBERT...")
            device = 0 if torch.cuda.is_available() else -1
            self._classifier = pipeline(
                "text-classification", 
                model="distilbert-base-multilingual-cased",
                device=device,
                truncation=True,
                max_length=512
            )
        return self._classifier

    async def analyze(self, raw_text: str):
        cleaned = clean_text(raw_text)
        metadata = extract_metadata(raw_text)
        
        # Prevent massive payloads from destroying RAM before it even hits the tokenizer
        # Average English word is ~5 chars. 512 tokens is roughly ~2500 chars. We'll slice at 3000 to be safe.
        safe_text = cleaned[:3000]
        
        # 1. AI Analysis
        ai_result = self.classifier(safe_text)[0]
        ai_label = ai_result['label']
        ai_score = ai_result['score']
        
        # 2. Heuristic Analysis & Highlighting
        keyword_hits = []
        reasoning = []
        
        for kw in self.scam_keywords:
            if kw in cleaned:
                keyword_hits.append(kw)
        
        # 3. Decision Logic & Reasoning
        is_suspicious = False
        
        if ai_label == "NEGATIVE" and ai_score > 0.7:
            is_suspicious = True
            reasoning.append(f"AI Model detected high scam-like sentiment (Confidence: {ai_score:.2f})")
        
        if len(keyword_hits) > 0:
            if len(keyword_hits) >= 2:
                is_suspicious = True
            reasoning.append(f"Detected suspicious keywords: {', '.join(keyword_hits)}")
            
        if metadata.get("has_link") and is_suspicious:
            reasoning.append("Message contains a suspicious link combined with scam patterns")
            
        # 4. Context-Aware social engineering detection
        context_flag = self._check_context_conflicts(cleaned)
        if context_flag:
            is_suspicious = True
            reasoning.append(context_flag)
            ai_score = max(ai_score, 0.95) # Boost confidence for explicit context matches
            
        final_prediction = "scam" if is_suspicious else "safe"
        
        # Adjust confidence
        confidence = ai_score
        if is_suspicious and len(keyword_hits) > 1:
            confidence = min(0.99, confidence + 0.15)

        logger.info(f"Analysis Complete: Label={final_prediction}, Confidence={confidence:.2f}")
        
        return {
            "prediction": final_prediction,
            "confidence": float(confidence),
            "reasoning": reasoning,
            "highlights": keyword_hits,
            "metadata": metadata,
            "recommendation": self._get_recommendation(final_prediction, keyword_hits)
        }

    def _check_context_conflicts(self, text: str) -> str:
        """Detects if a role (e.g. Professor) is performing an unusual action (e.g. asking for OTP)."""
        text = text.lower()
        
        roles = {
            "professor": ["professor", "teacher", "faculty", "dean", "lecturer"],
            "admin": ["admin", "administrator", "it support", "system access", "registrar"],
            "recruiter": ["recruiter", "hr manager", "hiring", "talent acquisition"]
        }
        
        suspicious_actions = {
            "otp_request": ["otp", "verification code", "6-digit", "security code", "pass code"],
            "payment": ["registration fee", "security deposit", "processing fee", "bank transfer"],
            "password": ["password", "login details", "credentials", "sign in info"]
        }
        
        detected_role = None
        for role, keywords in roles.items():
            if any(k in text for k in keywords):
                detected_role = role
                break
        
        if detected_role:
            for action, keywords in suspicious_actions.items():
                if any(k in text for k in keywords):
                    return f"CONTEXT ALERT: A '{detected_role}' would typically never ask for '{action.replace('_', ' ')}' via message."
        
        return None

    def _get_recommendation(self, prediction: str, keywords: list) -> str:
        if prediction == "scam":
            if "registration fee" in keywords or "security deposit" in keywords:
                return "CRITICAL: Legitimate internships NEVER ask for money. This is a scam."
            return "WARNING: This message matches profiles of known student scams. Do not engage."
        return "Looks relatively safe, but always verify the source and never share OTPs."

text_detector = TextDetectorService()
