import re
import math
import aiohttp
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from app.utils.logger import logger
from app.config import settings
from app.services.text_detector import text_detector
from app.services.external_intel import external_intel
from app.services.pattern_service import pattern_service
from app.services.trust_service import trust_service

try:
    from Levenshtein import distance as lev_distance
except ImportError:
    # Fallback to a simple implementation if the library is not available
    def lev_distance(s1, s2):
        if len(s1) < len(s2):
            return lev_distance(s2, s1)
        if not s2:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]


class URLDetectorService:
    def __init__(self):
        self.high_risk_tlds = set(settings.HIGH_RISK_TLDS)
        self.suspicious_keywords = set(settings.SUSPICIOUS_URL_KEYWORDS)
        self.trusted_domains = settings.TRUSTED_DOMAINS
        self.popular_domains = settings.POPULAR_DOMAINS
        self.url_shorteners = {"bit.ly", "tinyurl.com", "t.co", "ow.ly", "is.gd", "buff.ly", "short.io"}
        
        # ASCII equivalents for common Cyrillic/Greek homoglyphs used in spoofing
        self.homoglyph_map = {
            'а': 'a', 'с': 'c', 'е': 'e', 'о': 'o', 'р': 'p', 'х': 'x', 'у': 'y',
            'і': 'i', 'ј': 'j', 'ѕ': 's', 'ꙅ': 's', 'ԁ': 'd', 'ԛ': 'q', 'ԝ': 'w'
        }

    def calculate_entropy(self, domain: str) -> float:
        """Calculates the Shannon entropy of a domain name."""
        if not domain:
            return 0
        prob = [float(domain.count(c)) / len(domain) for c in dict.fromkeys(list(domain))]
        entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy

    def check_typosquatting(self, domain: str) -> list:
        """Checks if the domain is a close variant of popular domains."""
        hits = []
        clean_domain = domain.split('.')[0] # Get the main part
        
        for popular in self.popular_domains:
            pop_main = popular.split('.')[0]
            if clean_domain == pop_main:
                continue # Exact match skip
                
            dist = lev_distance(clean_domain, pop_main)
            if 0 < dist <= 2: # Very similar
                hits.append(popular)
        return hits
        
    def check_homoglyphs(self, domain: str) -> bool:
        """Detects if visually similar foreign characters are used to spoof trusted domains."""
        for char in domain:
            if char in self.homoglyph_map:
                return True
        return False
        
    def check_ip_masking(self, domain: str) -> bool:
        """Detects if the domain is actually a raw IP or Hex encoded IP."""
        # Check standard IPv4
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
            return True
        # Check Hex encoding (e.g. 0x7F000001)
        if re.match(r"^0x[0-9a-fA-F]+$", domain):
            return True
        return False
        
    def check_subdomain_abuse(self, domain: str) -> bool:
        """Detects excessively deep subdomains (e.g. login.paypal.com.scammer.net)."""
        parts = domain.split('.')
        # 4 or more dots usually indicates heavy subdomain nesting or abuse
        return len(parts) > 4

    async def fetch_web_content(self, url: str) -> dict:
        """
        Fetches the raw HTML content and records the redirect chain.
        Returns: {"text": str, "chain": List[str]}
        """
        try:
            # We spoof a standard User-Agent so we don't get blocked
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
            # Note: We allow redirects but want to see where they go
            timeout = aiohttp.ClientTimeout(total=8) # 8 seconds for deep scan redirects
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    # Capture history
                    chain = [str(r.url) for r in response.history]
                    chain.append(str(response.url))
                    
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        for element in soup(["script", "style", "nav", "footer", "header"]):
                            element.decompose()
                        
                        text = soup.get_text(separator=' ', strip=True)
                        return {"text": text, "chain": chain}
            return {"text": "", "chain": [url]}
        except Exception as e:
            logger.warning(f"Failed to deep scan URL {url}: {e}")
            return {"text": "", "chain": [url]}

    async def analyze(self, url: str):
        logger.info(f"Analyzing URL: {url}")
        
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
        except Exception as e:
            logger.error(f"URL parsing error: {e}")
            return {"prediction": "error", "message": "Invalid URL format"}

        risk_score = 0.0
        reasoning = []
        score_details = {}
        trust_info = trust_service.check_domain(domain)
        
        if trust_info:
            risk_score = -0.5 # Significant trust boost
            reasoning.append(f"🛡️ Shield of Trust: Verified {trust_info['name']} ({trust_info['category']})")
        
        # --- STATIC HEURISTICS (Pillar 2: Dynamic Pattern Engine) ---
        
        # 1. Pattern Engine Analysis (TLD, Domain, Path-Keywords)
        pattern_data = pattern_service.analyze_url(url) 
        if pattern_data["matches"]:
            risk_score += pattern_data["risk_score"]
            p_descriptions = [f"{m['value']} ({m['desc']})" for m in pattern_data["matches"]]
            reasoning.append(f"Dynamic Threat Match: Detected suspicious infrastructure or bait ({', '.join(p_descriptions)})")
            score_details["patterns"] = round(pattern_data["risk_score"] * 100, 1)

        # 2. Protocol check
        if parsed.scheme == 'http':
            risk_score += 0.1
            reasoning.append("Uses insecure HTTP protocol")
            score_details["protocol"] = 10.0

        # 4. Shortener Check
        if any(shortener in domain for shortener in self.url_shorteners):
            risk_score += 0.2
            reasoning.append("URL uses a known link shortener (Obfuscation risk)")
            score_details["obfuscation"] = 20.0

        # 5. Typosquatting Check
        typosquats = self.check_typosquatting(domain)
        if typosquats:
            risk_score += 0.4
            reasoning.append(f"Possible typosquatting detected for: {', '.join(typosquats)}")
            score_details["typosquatting"] = 40.0

        # 6. Entropy Check (DGA)
        entropy = self.calculate_entropy(domain)
        if entropy > 4.0:
            risk_score += 0.25
            reasoning.append(f"High domain entropy detected ({entropy:.2f}), possible machine-generated domain")
            score_details["entropy"] = 25.0

        # 7. Advanced: Homoglyph Attack
        if self.check_homoglyphs(domain):
            risk_score += 0.6
            reasoning.append("CRITICAL: Domain uses visually deceptive foreign characters (Homoglyph Attack)")
            score_details["homoglyph"] = 60.0
            
        # 8. Advanced: IP Masking
        if self.check_ip_masking(domain):
            risk_score += 0.5
            reasoning.append("CRITICAL: URL hides destination using raw IP digits instead of a registered domain name")
            score_details["ip_masking"] = 50.0
            
        # 9. Advanced: Subdomain Abuse
        if self.check_subdomain_abuse(domain):
            risk_score += 0.3
            reasoning.append("Deep subdomain nesting detected. Often used to bury the true root domain name.")
            score_details["subdomains"] = 30.0

        # --- EXTERNAL INTEL SCAN ---
        intel_result = await external_intel.check_url_reputation(url)
        if intel_result and intel_result["malicious"]:
            risk_score += 0.6
            reasoning.append(f"External Threat Intel (URLScan): URL flagged as malicious (Score: {intel_result['score']})")
            score_details["external_intel"] = 60.0
        elif intel_result:
            reasoning.append("External Threat Intel: No immediate threats found in global databases")

        # --- DEEP SCAN AI & REDIRECT INTEGRATION ---
        redirect_chain = [url]
        deep_scan_text = ""
        ai_label = "SAFE"
        ai_confidence = 0.0
        
        is_trusted = any(domain.endswith(trust) for trust in self.trusted_domains)
        if not is_trusted and risk_score < 0.8:
            logger.info("Initializing Deep Scan with Redirect Tracking...")
            scan_data = await self.fetch_web_content(url)
            deep_scan_text = scan_data["text"]
            redirect_chain = scan_data["chain"]
            
            # Reputation Jump Analysis
            if len(redirect_chain) > 1:
                start_domain = urlparse(redirect_chain[0]).netloc.lower()
                final_domain = urlparse(redirect_chain[-1]).netloc.lower()
                
                # Check for "High-to-Low" jump (e.g. .edu -> .xyz)
                if (".edu" in start_domain or ".gov" in start_domain) and not (".edu" in final_domain or ".gov" in final_domain):
                    risk_score += 0.35
                    reasoning.append(f"CRITICAL REDIRECT: Trusted origin ({start_domain}) jumped to an unverified domain ({final_domain})")
                    score_details["redirect_risk"] = 35.0
                
                if len(redirect_chain) > 3:
                    risk_score += 0.2
                    reasoning.append(f"Suspiciously long redirect chain detected ({len(redirect_chain)} hops)")
                    score_details["redirect_chain"] = 20.0

            if deep_scan_text and len(deep_scan_text) > 20: 
                ai_result = await text_detector.analyze(deep_scan_text)
                if ai_result["prediction"] == "scam":
                    ai_label = "SCAM"
                    ai_confidence = ai_result["confidence"]
                    risk_score += 0.5 
                    reasoning.append(f"DEEP SCAN: AI model detected scam-like intent in the webpage's content (Confidence: {ai_confidence*100:.1f}%)")
                    score_details["content_ai"] = 50.0
                else:
                    reasoning.append("DEEP SCAN: AI model analyzed webpage content and found no malicious text patterns")

        # --- FINAL SCORING & NORMALIZATION ---
        risk_score = min(1.0, risk_score)
        
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
        
        # In the v2 implementation, 'confidence' represents 'Scam Likelihood' (0.0 to 1.0)
        confidence = float(risk_score)
        
        # If the Deep Scan AI found a scam, ensure likelihood is at least 0.6
        if ai_label == "SCAM":
            confidence = max(confidence, ai_confidence, 0.6)
            if confidence >= high_t: prediction = "scam"
            elif prediction == "safe": prediction = "suspicious"

        logger.info(f"URL Analysis Complete: {prediction.upper()} [{confidence*100:.1f}%] - Score: {risk_score}")
        
        return {
            "prediction": prediction,
            "confidence": float(confidence),
            "scam_score": float(risk_score),
            "reasoning": list(set(reasoning)),
            "score_explanation": score_details,
            "forensics": {
                "domain": domain,
                "geo_location": (forensic_data := await self._get_geo_and_asn(domain))["geo"],
                "asn_info": forensic_data["asn"],
                "trust_info": trust_info
            },
            "metadata": {
                "entropy": round(entropy, 2),
                "is_trusted": is_trusted,
                "deep_scan_executed": bool(deep_scan_text),
                "redirect_chain": redirect_chain
            },
            "redirect_chain": redirect_chain
        }

    async def _get_geo_and_asn(self, domain: str) -> dict:
        """
        Pillar 2: Real-time Forensic Enrichment.
        Fetches live GeoIP and ASN data for the domain.
        """
        import socket
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            ip_address = await loop.run_in_executor(None, socket.gethostbyname, domain)
            
            api_url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,city,as,org"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            # Process ASN Info
                            asn_full = data.get("as", "AS000 Unknown")
                            asn_id = asn_full.split(' ')[0]
                            isp_name = data.get("org", data.get("as", "Unknown ISP"))
                            
                            # Generate Flag Emoji from Country Code
                            country_code = data.get("countryCode", "")
                            flag = "".join(chr(127397 + ord(c)) for c in country_code.upper()) if country_code else "⬛"
                            
                            return {
                                "geo": {
                                    "country": data.get("country", "Unknown"),
                                    "city": data.get("city", "Unknown"),
                                    "ip": ip_address,
                                    "flag": flag
                                },
                                "asn": {
                                    "asn": asn_id,
                                    "isp": isp_name
                                }
                            }
        except Exception as e:
            logger.warning(f"Forensic lookup failed for {domain}: {e}")
            
        return {
            "geo": {"country": "Unknown", "city": "Hidden", "ip": "N/A"},
            "asn": {"asn": "N/A", "isp": "Unknown ISP"}
        }

url_detector = URLDetectorService()
