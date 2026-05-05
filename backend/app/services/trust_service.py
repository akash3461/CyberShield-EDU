import logging
import re
from sqlalchemy.orm import Session
from app.models.schema import VerifiedProvider
from app.database import SessionLocal
from urllib.parse import urlparse

logger = logging.getLogger("CyberShield")

class TrustService:
    """
    Pillar 3: The Shield of Trust (Whitelist Engine).
    Proactively identifies and badges legitimate career portals and institutional partners.
    """

    def __init__(self):
        # Format: "Brand Name": ["Primary Domain", "Other Allowed Domains"]
        self.watch_list = {
            "amazon": ["amazon.com", "amazon.in", "media-amazon.com", "amzn.to"],
            "paypal": ["paypal.com", "paypal-objects.com", "paypal.me"],
            "google": ["google.com", "gstatic.com", "googleapis.com", "google.co.in"],
            "microsoft": ["microsoft.com", "office.com", "outlook.com", "live.com", "msn.com"],
            "apple": ["apple.com", "icloud.com", "me.com"],
            "netflix": ["netflix.com"],
            "facebook": ["facebook.com", "fb.com", "messenger.com"],
            "instagram": ["instagram.com", "ig.me"],
            "whatsapp": ["whatsapp.com", "wa.me"],
            "binance": ["binance.com", "bnbstatic.com"],
            "coinbase": ["coinbase.com"],
            "metamask": ["metamask.io"],
            "ebay": ["ebay.com", "ebay.in"],
            "fedex": ["fedex.com"],
            "ups": ["ups.com"],
            "dhl": ["dhl.com"],
            "stripe": ["stripe.com"],
            "university": [".edu", "ac.uk", "edu.au", "edu.pk"], 
            "college": [".edu", "ac.uk"],
            "internship": ["lever.co", "greenhouse.io", "internshala.com"],
        }

    def check_company_impersonation(self, text: str, source_domain: str = None) -> dict:
        """
        Detects if the text claims to be from a high-trust company 
        while the source/link is unrelated.
        """
        if not text:
            return None
            
        text_lower = text.lower()
        
        # We also check for common phrasings like "from PayPal" or "at Amazon"
        for brand, trusted_domains in self.watch_list.items():
            # Use word boundaries or just check if brand is mentioned
            # We use a bit more aggressive check to catch "Pay-Pal" or "Amz"
            brand_pat = brand
            if brand == "paypal": brand_pat = r"pay[\s-]?pal"
            elif brand == "amazon": brand_pat = r"ama[\s-]?zon"
            
            if re.search(brand_pat, text_lower):
                # If we have a source domain (e.g. from a link or email author)
                if source_domain:
                    source_domain = source_domain.lower().strip()
                    if source_domain.startswith("www."):
                        source_domain = source_domain[4:]
                    
                    # Check if the source domain matches any of the trusted domains
                    is_legit = False
                    for trusted in trusted_domains:
                        # Match root domain or subdomain
                        # e.g. "paypal.com" in "login.paypal.com" -> True
                        # e.g. "paypal.com" in "paypal-scam.net" -> False (if we anchor)
                        if trusted.startswith("."): # Generic TLD check
                            if source_domain.endswith(trusted):
                                is_legit = True
                                break
                        else:
                            if source_domain == trusted or source_domain.endswith("." + trusted):
                                is_legit = True
                                break
                    
                    if not is_legit:
                        logger.warning(f"IMPERSONATION TRIGGERED: Message mentions '{brand}' but domain is '{source_domain}'")
                        return {
                            "brand": brand.capitalize(),
                            "risk": "high",
                            "reason": f"CRITICAL IMPERSONATION: Message claims origin is '{brand.capitalize()}' but the digital fingerprint points to an unrelated domain ({source_domain})."
                        }
        
        return None

    def check_domain(self, domain: str) -> dict:
        """
        Cross-references a domain against the institutional trust registry.
        """
        if not domain:
            return None
            
        db = SessionLocal()
        try:
            domain = domain.lower().strip()
            if domain.startswith("www."):
                domain = domain[4:]
                
            # 1. Exact Match in DB
            provider = db.query(VerifiedProvider).filter(VerifiedProvider.official_url.contains(domain)).first()
            
            # 2. Subdomain/Root Match Loop
            if not provider:
                parts = domain.split('.')
                if len(parts) > 2:
                    root_domain = ".".join(parts[-2:])
                    provider = db.query(VerifiedProvider).filter(VerifiedProvider.official_url.contains(root_domain)).first()

            if provider:
                logger.info(f"SHIELD OF TRUST: Domain {domain} verified via {provider.name}")
                return {
                    "name": provider.name,
                    "category": provider.category,
                    "security_tips": provider.security_tips,
                    "verified_at": provider.verified_at.isoformat() if provider.verified_at else None
                }
            
            return None
        except Exception as e:
            logger.error(f"Trust lookup failed: {e}")
            return None
        finally:
            db.close()

trust_service = TrustService()
