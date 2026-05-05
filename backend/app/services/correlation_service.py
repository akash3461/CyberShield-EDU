from app.utils.logger import logger

class CorrelationService:
    def __init__(self):
        # Definition of Cross-Modal Patterns
        self.patterns = [
            {
                "id": "academic_financial_fraud",
                "name": "Academic Financial Fraud",
                "conditions": {"intent": "FINANCIAL", "category": "ACADEMIC"},
                "boost": 0.4,
                "reason": "Official academic opportunities rarely demand non-standard payments (Crypto/Third-party apps)."
            },
            {
                "id": "social_redirection_scam",
                "name": "Social Redirection Scam",
                "conditions": {"intent": "URGENCY", "platform": ["WhatsApp", "Telegram"]},
                "boost": 0.35,
                "reason": "Scammers often move conversations to encrypted apps to avoid corporate security filters."
            },
            {
                "id": "unverified_official",
                "name": "Unverified Official Document",
                "conditions": {"metadata_trust": "low", "intent": "OFFICIAL"},
                "boost": 0.3,
                "reason": "This document claims to be an official offer but lacks verifying digital signatures or trusted metadata."
            },
            {
                "id": "high_risk_infrastructure",
                "name": "High-Risk Link Infrastructure",
                "conditions": {"url_status": "suspicious", "intent": "ACADEMIC"},
                "boost": 0.25,
                "reason": "Student offers using high-entropy or short-link infrastructure are statistically high-risk."
            },
            {
                "id": "comment_bait_harvesting",
                "name": "Data Harvesting Bait",
                "conditions": {"intent": "DATA_HARVESTING"},
                "boost": 0.3,
                "reason": "Legitimate employers never ask you to drop your private Gmail or WhatsApp in public social media comments."
            }
        ]

    def evaluate(self, findings):
        """
        findings: dict containing observed traits.
        Example: {
            "intents": ["FINANCIAL", "ACADEMIC"],
            "platform": "Telegram",
            "url_status": "suspicious",
            "metadata_trust": "low"
        }
        """
        boost_total = 0.0
        applied_reasons = []
        
        intents = findings.get("intents", [])
        categories = findings.get("categories", [])
        platform = findings.get("platform", "Unknown")
        url_status = findings.get("url_status", "safe")
        metadata_trust = findings.get("metadata_trust", "medium")

        for pattern in self.patterns:
            match = True
            cond = pattern["conditions"]
            
            # Check Intents
            if "intent" in cond and cond["intent"] not in intents:
                match = False
            
            # Check Categories
            if "category" in cond and cond["category"] not in categories:
                match = False
            
            # Check Platform
            if "platform" in cond:
                if isinstance(cond["platform"], list):
                    if platform not in cond["platform"]:
                        match = False
                elif cond["platform"] != platform:
                    match = False
            
            # Check URL Status
            if "url_status" in cond and cond["url_status"] != url_status:
                match = False
            
            # Check Metadata
            if "metadata_trust" in cond and cond["metadata_trust"] != metadata_trust:
                match = False

            if match:
                logger.info(f"Correlation Match: {pattern['name']}")
                boost_total += pattern["boost"]
                applied_reasons.append(f"🔍 Pattern Match: {pattern['reason']}")

        return {
            "boost": round(boost_total, 2),
            "reasons": applied_reasons
        }

correlation_service = CorrelationService()
