from transformers import pipeline
from app.utils.logger import logger
from app.utils.text_cleaner import clean_text, extract_metadata
from app.config import settings
from app.services.trust_service import trust_service
from app.services.pattern_service import pattern_service
import torch
import os
import re


class TextDetectorService:
    def __init__(self):
        self._classifier = None


    def load_model(self):
        """Explicitly load the model during startup to avoid first-run latency."""
        if self._classifier is None:
            # Path to the fine-tuned model
            local_model_path = os.path.join(os.path.dirname(__file__), "..", "ai_models", "scam_detector_v1")
            
            if os.path.exists(local_model_path):
                logger.info(f"🚀 INITIALIZING SPECIALIZED STUDENT BRAIN (v1) from {local_model_path}")
                model_to_load = local_model_path
            else:
                logger.info("Initializing fallback: Multilingual DistilBERT (Zero-Shot)...")
                model_to_load = "distilbert-base-multilingual-cased"

            device = 0 if torch.cuda.is_available() else -1
            self._classifier = pipeline(
                "text-classification", 
                model=model_to_load,
                device=device,
                truncation=True,
                max_length=512
            )
        return self._classifier

    @property
    def classifier(self):
        return self.load_model()

    async def analyze(self, raw_text: str):
        cleaned = clean_text(raw_text)
        metadata = extract_metadata(raw_text)
        
        # Prevent massive payloads from destroying RAM before it even hits the tokenizer
        safe_text = cleaned[:3000]
        
        # 1. AI Analysis
        ai_result = self.classifier(safe_text)[0]
        ai_label = ai_result['label']
        ai_score = ai_result['score']
        
        # 2. Dynamic Pattern Analysis (Pillar 2)
        pattern_data = pattern_service.analyze_text(cleaned)
        pattern_matches = pattern_data["matches"]
        reasoning = []
        score_details = {}
        
        # 3. Decision Logic & Reasoning
        is_suspicious = False
        
        # AI Sentiment Analysis Breakdown
        if ai_result['score'] > 0.6: 
            is_suspicious = True
            sentiment_type = "Urgency/Pressure" if any(u in cleaned.lower() for u in ["urgent", "now", "immediately", "limited", "soon"]) else "Unexpected Reward" if any(r in cleaned.lower() for r in ["win", "award", "prize", "cash", "bonus"]) else "Suspicious"
            reasoning.append(f"AI Model detected {sentiment_type} sentiment (Confidence: {ai_result['score']:.2f})")
            score_details["ai_analysis"] = round(ai_result['score'] * 40, 1)

        # Heuristic Pattern Analysis Breakdown
        if pattern_matches:
            is_suspicious = True
            p_descriptions = [f"{m['value']} ({m['desc']})" for m in pattern_matches]
            reasoning.append(f"Detected heuristic threat patterns: {', '.join(p_descriptions)}")
            score_details["patterns"] = round(pattern_data["risk_score"] * 100, 1)
            
        # 4. Impersonation Check (Pillar 3 Synergy)
        impersonated_brand = None
        if metadata.get("has_link"):
            # Use the first link found for impersonation check - matches both http and www
            url_pattern = r'(?:https?://|www\.)(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
            links = re.findall(url_pattern, raw_text)
            if links:
                from urllib.parse import urlparse
                link_to_check = links[0]
                if not link_to_check.startswith('http'):
                    link_to_check = 'http://' + link_to_check
                
                source_domain = urlparse(link_to_check).netloc
                impersonation_warning = trust_service.check_company_impersonation(cleaned, source_domain)
                
                if impersonation_warning:
                    is_suspicious = True
                    reasoning.append(impersonation_warning["reason"])
                    score_details["impersonation"] = 40.0 # Increased weight
                    impersonated_brand = impersonation_warning["brand"]

        if metadata.get("has_link") and is_suspicious:
            reasoning.append("Message contains a suspicious link combined with threat patterns")
            
        # 5. Context-Aware social engineering detection
        context_flag = self._check_context_conflicts(cleaned)
        if context_flag:
            is_suspicious = True
            reasoning.append(context_flag)
            ai_score = max(ai_score, 0.95)
            score_details["context"] = 20.0
            
        # Adjust final confidence to represent 0-100% Scam Likelihood
        total_score = sum(score_details.values()) / 100.0
        confidence = max(float(ai_score) if ai_label == "LABEL_1" else 0.0, total_score)
        
        # New: Tri-state prediction logic from DB Config
        from app.utils.config_helper import config_helper
        thresholds = config_helper.get_thresholds()
        low_t = thresholds.get("low", 0.3)
        high_t = thresholds.get("high", 0.7)

        if confidence >= high_t:
            final_prediction = "scam"
        elif confidence >= low_t:
            final_prediction = "suspicious"
        else:
            final_prediction = "safe"

        logger.info(f"Analysis Complete: Label={final_prediction}, Confidence={confidence:.2f}")
        
        return {
            "prediction": final_prediction,
            "confidence": float(confidence),
            "reasoning": list(set(reasoning)),
            "score_explanation": score_details,
            "metadata": metadata,
            "insights": {
                "sentiment": ai_label,
                "complexity": self._calculate_complexity(safe_text),
                "is_context_flagged": bool(context_flag),
                "impersonated_brand": impersonated_brand
            },
            "recommendation": self._get_recommendation(final_prediction, [m['value'] for m in pattern_matches])
        }

    def _calculate_complexity(self, text: str) -> str:
        """Rough heuristic for linguistic complexity/sophistication."""
        words = text.split()
        if not words: return "N/A"
        avg_len = sum(len(w) for w in words) / len(words)
        if avg_len > 6: return "High (Professional/Sophisticated)"
        if avg_len > 4: return "Medium (Standard)"
        return "Low (Casual/Slang)"

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
