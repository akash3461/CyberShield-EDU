import re
import logging
from sqlalchemy.orm import Session
from app.models.schema import ThreatPattern, ScamKeyword
from app.database import SessionLocal
from app.config import settings

logger = logging.getLogger("CyberShield")

class PatternService:
    """
    Pillar 2: Dynamic Pattern Engine.
    Manages and executes detection heuristics (Regex, Keywords, TLDs).
    """
    def __init__(self):
        self.patterns = {"keyword": [], "regex": [], "tld": [], "domain": []}
        self.is_loaded = False

    def load_from_db(self, db: Session = None):
        """Loads all patterns from database into memory for fast matching."""
        db_created = False
        if db is None:
            db = SessionLocal()
            db_created = True
            
        try:
            # 1. Fetch from ThreatPattern table
            all_patterns = db.query(ThreatPattern).filter(ThreatPattern.is_active == True).all()
            
            # Reset memory cache
            self.patterns = {"keyword": [], "regex": [], "tld": [], "domain": []}
            
            for p in all_patterns:
                if p.pattern_type in self.patterns:
                    self.patterns[p.pattern_type].append({
                        "value": p.value,
                        "risk": p.risk_score,
                        "desc": p.description
                    })

            # 2. Add legacy ScamKeywords as keywords
            legacy = db.query(ScamKeyword).all()
            for l in legacy:
                self.patterns["keyword"].append({
                    "value": l.keyword,
                    "risk": l.weight or 0.1,
                    "desc": "Legacy Scam Keyword"
                })

            # 3. Fallback to settings if DB is empty
            if not all_patterns and not legacy:
                for kw in settings.SCAM_KEYWORDS:
                    self.patterns["keyword"].append({"value": kw, "risk": 0.1, "desc": "Initial Config Keyword"})
                for tld in settings.HIGH_RISK_TLDS:
                    self.patterns["tld"].append({"value": tld, "risk": 0.3, "desc": "Initial Config TLD"})

            self.is_loaded = True
            logger.info(f"Pattern Engine: Loaded {len(all_patterns) + len(legacy)} total rules into memory.")
        except Exception as e:
            logger.error(f"Pattern Engine Load Failure: {e}")
        finally:
            if db_created:
                db.close()

    def analyze_text(self, text: str) -> dict:
        """Runs text through keyword and regex patterns with tiered weight logic."""
        if not self.is_loaded: self.load_from_db()
        
        matches = []
        total_risk = 0.0
        text_lower = text.lower()
        
        has_context = False
        has_high_risk = False

        # Intent & Category tagging for correlation
        intents = []
        categories = []
        
        intent_map = {
            "payment": "FINANCIAL", "transfer": "FINANCIAL", "upi": "FINANCIAL", "crypto": "FINANCIAL", "fee": "FINANCIAL",
            "jama": "FINANCIAL", "paise": "FINANCIAL", "bhejein": "FINANCIAL", "bharta": "FINANCIAL",
            "urgent": "URGENCY", "now": "URGENCY", "limited": "URGENCY", "immediately": "URGENCY",
            "jaldi": "URGENCY", "fauran": "URGENCY", "shandaar": "URGENCY",
            "official": "OFFICIAL", "letter": "OFFICIAL", "agreement": "OFFICIAL", "mubarak": "OFFICIAL",
            "drop your": "DATA_HARVESTING", "write your": "DATA_HARVESTING", "comment your": "DATA_HARVESTING",
            "in the comments": "DATA_HARVESTING", "gmail below": "DATA_HARVESTING", "whatsapp below": "DATA_HARVESTING"
        }
        category_map = {
            "internship": "ACADEMIC", "scholarship": "ACADEMIC", "job": "PROFESSIONAL", "career": "PROFESSIONAL",
            "naukri": "PROFESSIONAL", "mulazmat": "PROFESSIONAL"
        }

        # Keyword matching
        for k in self.patterns["keyword"]:
            val = k["value"].lower()
            if val in text_lower:
                risk = k["risk"]
                
                # Check for Intent tags
                for key, tag in intent_map.items():
                    if key in val: intents.append(tag)
                # Check for Category tags
                for key, tag in category_map.items():
                    if key in val: categories.append(tag)

                # Context words like 'internship' or 'offer' get reduced weight if seen alone
                context_words = ["internship", "offer", "job", "scholarship", "career"]
                is_context = any(cw in val for cw in context_words)
                
                if is_context:
                    has_context = True
                    risk = risk * 0.5 # Reduce context risk
                else:
                    has_high_risk = True

                matches.append({
                    "type": "keyword",
                    "value": k["value"],
                    "desc": k["desc"],
                    "risk": risk
                })
                total_risk += risk

        # Combinatorial adjustment: If we ONLY have context words, cap the risk
        if has_context and not has_high_risk:
            total_risk = min(0.2, total_risk)

        # Regex matching
        for r in self.patterns["regex"]:
            try:
                if re.search(r["value"], text, re.IGNORECASE):
                    match_desc = r["desc"] or r["value"]
                    matches.append({
                        "type": "regex",
                        "value": r["value"],
                        "desc": match_desc,
                        "risk": r["risk"]
                    })
                    total_risk += r["risk"]
            except re.error:
                continue
                
        return {
            "matches": matches, 
            "risk_score": total_risk,
            "intents": list(set(intents)),
            "categories": list(set(categories))
        }

    def analyze_url(self, url: str) -> dict:
        """
        Runs full URL through TLD, domain, and keyword patterns.
        Implements tiered weighting to prevent 'internship' etc. from auto-flagging.
        """
        if not self.is_loaded: self.load_from_db()
        
        matches = []
        total_risk = 0.0
        
        # Normalize and split
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            full_path = f"{domain}{parsed.path}".lower()
        except:
            full_path = url.lower()
            domain = url.lower()
        
        # 1. TLD matching
        for t in self.patterns["tld"]:
            if domain.endswith(t["value"]):
                matches.append({
                    "type": "tld",
                    "value": t["value"],
                    "desc": t["desc"],
                    "risk": t["risk"]
                })
                total_risk += t["risk"]

        # 2. Blacklisted domains
        for d in self.patterns["domain"]:
            if d["value"].lower() in domain:
                matches.append({
                    "type": "domain",
                    "value": d["value"],
                    "desc": d["desc"],
                    "risk": d["risk"]
                })
                total_risk += d["risk"]
        
        # 3. Path & Domain Keywords (The "Bait" Shield)
        # Tiered logic: Context keywords are less heavy than actual threats
        context_words = ["internship", "offer", "job", "scholarship", "career", "hiring"]
        has_context = False
        has_threat = False

        for k in self.patterns["keyword"]:
            kw = k["value"].lower()
            if kw in full_path:
                risk = k["risk"]
                is_context = any(cw in kw for cw in context_words)
                
                if is_context:
                    has_context = True
                    risk = risk * 0.3 # Significantly reduce standalone context risk in URLs
                else:
                    has_threat = True

                matches.append({
                    "type": "bait",
                    "value": kw,
                    "desc": k["desc"],
                    "risk": risk
                })
                total_risk += risk
        
        # If ONLY context words are found in the URL, cap the bait risk at 0.15
        if has_context and not has_threat and not any(m['type'] in ['tld', 'domain'] for m in matches):
            total_risk = min(0.15, total_risk)
                
        return {"matches": matches, "risk_score": total_risk}

pattern_service = PatternService()
