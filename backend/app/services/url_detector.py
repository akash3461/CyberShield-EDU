import re
import math
import aiohttp
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from app.utils.logger import logger
from app.config import settings
from app.services.text_detector import text_detector
from app.services.external_intel import external_intel

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

    async def fetch_web_content(self, url: str) -> str:
        """Fetches the raw HTML content of the URL with a strict timeout."""
        try:
            # We spoof a standard User-Agent so we don't get blocked
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
            timeout = aiohttp.ClientTimeout(total=5) # 5 seconds max wait
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Extract only visible text using BeautifulSoup
                        soup = BeautifulSoup(html, 'html.parser')
                        # Remove script, style, and navigation elements
                        for element in soup(["script", "style", "nav", "footer", "header"]):
                            element.decompose()
                        
                        text = soup.get_text(separator=' ', strip=True)
                        return text
            return ""
        except Exception as e:
            logger.warning(f"Failed to deep scan URL {url}: {e}")
            return ""

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
        
        # --- STATIC HEURISTICS ---
        
        # 1. Protocol check
        if parsed.scheme == 'http':
            risk_score += 0.1
            reasoning.append("Uses insecure HTTP protocol")

        # 2. TLD Check
        for tld in self.high_risk_tlds:
            if domain.endswith(tld):
                risk_score += 0.3
                reasoning.append(f"Domain uses high-risk TLD: {tld}")
                break

        # 3. Keyword Check
        found_keywords = [kw for kw in self.suspicious_keywords if kw in domain or kw in path]
        if found_keywords:
            risk_score += 0.15 * len(found_keywords)
            reasoning.append(f"Found suspicious keywords: {', '.join(found_keywords)}")

        # 4. Shortener Check
        if any(shortener in domain for shortener in self.url_shorteners):
            risk_score += 0.2
            reasoning.append("URL uses a known link shortener")

        # 5. Typosquatting Check
        typosquats = self.check_typosquatting(domain)
        if typosquats:
            risk_score += 0.4
            reasoning.append(f"Possible typosquatting detected for: {', '.join(typosquats)}")

        # 6. Entropy Check (DGA)
        entropy = self.calculate_entropy(domain)
        if entropy > 4.0:
            risk_score += 0.25
            reasoning.append(f"High domain entropy detected ({entropy:.2f}), possible machine-generated domain")

        # 7. Advanced: Homoglyph Attack
        if self.check_homoglyphs(domain):
            risk_score += 0.6
            reasoning.append("CRITICAL: Domain uses visually deceptive foreign characters (Homoglyph Attack)")
            
        # 8. Advanced: IP Masking
        if self.check_ip_masking(domain):
            risk_score += 0.5
            reasoning.append("CRITICAL: URL hides destination using raw IP digits instead of a registered domain name")
            
        # 9. Advanced: Subdomain Abuse
        if self.check_subdomain_abuse(domain):
            risk_score += 0.3
            reasoning.append("Deep subdomain nesting detected. Often used to bury the true root domain name.")

        # Trust Factor Override
        is_trusted = any(domain.endswith(trust) for trust in self.trusted_domains)
        if is_trusted:
            risk_score = max(0, risk_score - 0.5)
            reasoning.append("Domain matches known trusted configuration")


        # --- EXTERNAL INTEL SCAN ---
        intel_result = await external_intel.check_url_reputation(url)
        if intel_result and intel_result["malicious"]:
            risk_score += 0.6
            reasoning.append(f"External Threat Intel (URLScan): URL flagged as malicious (Score: {intel_result['score']})")
        elif intel_result:
            reasoning.append("External Threat Intel: No immediate threats found in global databases")

        # --- DEEP SCAN AI INTEGRATION ---
        # Only run Deep Scan if the url is not already definitively blocked (>0.8) and not a short-circuit error.
        # We also don't deep scan trusted domains to save compute.
        deep_scan_text = ""
        ai_label = "SAFE"
        ai_confidence = 0.0
        
        if not is_trusted and risk_score < 0.8:
            logger.info("Static score inconclusive. Initializing Deep Scan web execution...")
            deep_scan_text = await self.fetch_web_content(url)
            
            if deep_scan_text and len(deep_scan_text) > 20: 
                # Run the fetched webpage content through our DistilBERT model
                ai_result = await text_detector.analyze(deep_scan_text)
                
                if ai_result["prediction"] == "scam":
                    ai_label = "SCAM"
                    ai_confidence = ai_result["confidence"]
                    risk_score += 0.5 # Massive penalty if the AI catches scam content on the page
                    reasoning.append(f"DEEP SCAN: AI model detected scam-like intent in the webpage's content (Confidence: {ai_confidence*100:.1f}%)")
                else:
                    reasoning.append("DEEP SCAN: AI model analyzed webpage content and found no malicious text patterns")

        # --- FINAL SCORING ---
        risk_score = min(1.0, risk_score)
        prediction = "scam" if risk_score >= 0.5 else "safe"
        
        # Calculate a final visual confidence
        confidence = float(1.0 - abs(0.5 - risk_score) * 2)
        if prediction == "scam":
             # Boost visual confidence if we caught it via Deep Scan
             if ai_label == "SCAM":
                 confidence = max(confidence, ai_confidence)
             else:
                 confidence = min(0.99, confidence + (risk_score - 0.5))

        logger.info(f"URL Analysis Complete: {prediction.upper()} [{confidence*100:.1f}%] - Score: {risk_score}")
        
        return {
            "prediction": prediction,
            "confidence": float(confidence),
            "scam_score": float(risk_score),
            "reasoning": reasoning,
            "metadata": {
                "domain": domain,
                "entropy": round(entropy, 2),
                "is_trusted": is_trusted,
                "deep_scan_executed": bool(deep_scan_text)
            }
        }

url_detector = URLDetectorService()
