# Detection Engines — Technical Deep-Dive

> Technical breakdown of every detection engine in CyberShield-EDU. All algorithms, score formulas, and thresholds are derived directly from source code in `backend/app/services/`.

---

## Table of Contents

1. [Engine Overview](#1-engine-overview)
2. [Text Detection Engine](#2-text-detection-engine)
3. [Pattern Engine (Pillar 2)](#3-pattern-engine-pillar-2)
4. [Shield of Trust (Pillar 3)](#4-shield-of-trust-pillar-3)
5. [URL Detection Engine](#5-url-detection-engine)
6. [Image Forensic Engine](#6-image-forensic-engine)
7. [PDF Forensic Engine](#7-pdf-forensic-engine)
8. [Correlation Engine](#8-correlation-engine)
9. [Gamification Engine](#9-gamification-engine)

---

## 1. Engine Overview

| Engine | File | Primary Technology | Processing Mode |
|---|---|---|---|
| Text Detector | `text_detector.py` | DistilBERT / scam_detector_v1 | Synchronous |
| Pattern Engine | `pattern_service.py` | Regex + String Matching | Synchronous (sub-service) |
| Trust Service | `trust_service.py` | DB Whitelist + Watchlist | Synchronous (sub-service) |
| URL Detector | `url_detector.py` | 9-Layer Heuristics + aiohttp | Asynchronous |
| Image Detector | `image_detector_service.py` | OpenCV + EXIF + OCR | Async (Celery) |
| PDF Analyzer | `pdf_analyzer.py` | pdfplumber + Recursive URL | Async (Celery) |
| Correlation | `correlation_service.py` | Rule-based cross-signal | Synchronous (post-analysis) |
| Gamification | `utils/gamification.py` | XP math + DB | Synchronous (post-scan) |

All service classes are instantiated as **module-level singletons** (e.g., `text_detector = TextDetectorService()`). This means AI models and compiled patterns are loaded once and shared across all requests.

---

## 2. Text Detection Engine

**File:** `backend/app/services/text_detector.py`

### 2.1 Model Loading

On startup (`main.py` calls `text_detector.load_model()`), the system:

1. Checks for a fine-tuned model at `backend/app/ai_models/scam_detector_v1/`
2. If found → loads it as the primary classifier
3. If not found → falls back to `distilbert-base-multilingual-cased` (downloaded from HuggingFace Hub)
4. Auto-detects CUDA GPU (`device=0`) or falls back to CPU (`device=-1`)
5. Initializes HuggingFace `pipeline("text-classification", truncation=True, max_length=512)`

```python
device = 0 if torch.cuda.is_available() else -1
self._classifier = pipeline(
    "text-classification",
    model=model_to_load,
    device=device,
    truncation=True,
    max_length=512
)
```

### 2.2 Analysis Pipeline (7 Stages)

```
Raw text
  │
  ├─ clean_text() + extract_metadata()   [text_cleaner.py]
  ├─ Truncate to 3,000 chars             [RAM protection]
  │
  ▼
Stage 1: AI Model Inference
  → classifier(safe_text)[0]
  → {label: "LABEL_0/1", score: float}

Stage 2: Dynamic Pattern Engine
  → pattern_service.analyze_text(cleaned)
  → {matches, risk_score, intents, categories}

Stage 3: Sentiment Classification
  → Urgency/Pressure, Unexpected Reward, or Suspicious
  → (keyword-based, run on cleaned text)

Stage 4: Impersonation Check
  → Extracts URLs from raw text via regex
  → trust_service.check_company_impersonation(cleaned, source_domain)

Stage 5: Context Conflict Detection
  → _check_context_conflicts(cleaned)
  → Detects role+action social engineering mismatches

Stage 6: Score Aggregation
  → total_score = sum(score_details.values()) / 100.0
  → confidence = max(ai_score if scam else 0.0, total_score)

Stage 7: Tri-state Decision (from DB config)
  → load thresholds: low=0.3, high=0.7
  → "scam" / "suspicious" / "safe"
```

### 2.3 Context Conflict Detection

Detects **social engineering** by checking if an authority figure is requesting a suspicious action:

**Roles detected:**
```python
roles = {
    "professor": ["professor", "teacher", "faculty", "dean", "lecturer"],
    "admin":     ["admin", "administrator", "it support", "system access", "registrar"],
    "recruiter": ["recruiter", "hr manager", "hiring", "talent acquisition"]
}
```

**Suspicious actions:**
```python
suspicious_actions = {
    "otp_request": ["otp", "verification code", "6-digit", "security code", "pass code"],
    "payment":     ["registration fee", "security deposit", "processing fee", "bank transfer"],
    "password":    ["password", "login details", "credentials", "sign in info"]
}
```

**Alert format:** `"CONTEXT ALERT: A 'professor' would typically never ask for 'payment' via message."`

When triggered: `ai_score = max(ai_score, 0.95)` and `score_details["context"] = 20.0`

### 2.4 Linguistic Complexity

```python
avg_len = sum(len(w) for w in words) / len(words)
if avg_len > 6:   return "High (Professional/Sophisticated)"
if avg_len > 4:   return "Medium (Standard)"
return "Low (Casual/Slang)"
```

### 2.5 Score Explanation Components

| Component | Weight | Trigger |
|---|---|---|
| `ai_analysis` | `ai_score × 40` | AI confidence > 0.6 |
| `patterns` | `pattern_risk × 100` | DB pattern matches |
| `impersonation` | `40.0` (fixed) | Brand/domain mismatch |
| `context` | `20.0` (fixed) | Role+action conflict |

### 2.6 Recommendations

```python
if prediction == "scam":
    if "registration fee" or "security deposit" in keywords:
        → "CRITICAL: Legitimate internships NEVER ask for money. This is a scam."
    else:
        → "WARNING: This message matches profiles of known student scams. Do not engage."
else:
    → "Looks relatively safe, but always verify the source and never share OTPs."
```

---

## 3. Pattern Engine (Pillar 2)

**File:** `backend/app/services/pattern_service.py`

### 3.1 Data Loading

Loaded from DB on first use (lazy), and immediately after any admin add/update:

```python
def load_from_db(self, db=None):
    # 1. Fetch ThreatPattern table (active only)
    all_patterns = db.query(ThreatPattern).filter(ThreatPattern.is_active == True).all()
    
    # 2. Fetch ScamKeyword table (legacy)
    legacy = db.query(ScamKeyword).all()
    
    # 3. Fallback to settings if both tables are empty
    if not all_patterns and not legacy:
        # loads from config.py SCAM_KEYWORDS + HIGH_RISK_TLDS
```

Stored as in-memory dict: `{"keyword": [...], "regex": [...], "tld": [...], "domain": [...]}`

### 3.2 Text Analysis

**Keyword matching** (case-insensitive substring):
```python
for k in self.patterns["keyword"]:
    if k["value"].lower() in text_lower:
        risk = k["risk"]
        # Context-word reduction: internship, offer, job, scholarship, career
        if is_context_word:
            has_context = True
            risk = risk * 0.5   # 50% reduction for standalone context words
        else:
            has_high_risk = True
        total_risk += risk
```

**Combinatorial cap:** If ONLY context words match and no high-risk words:
```python
if has_context and not has_high_risk:
    total_risk = min(0.2, total_risk)
```

**Regex matching:**
```python
for r in self.patterns["regex"]:
    if re.search(r["value"], text, re.IGNORECASE):
        total_risk += r["risk"]
```

**Intent tagging** (feeds Correlation Engine):
```python
intent_map = {
    "payment": "FINANCIAL", "fee": "FINANCIAL", "paise": "FINANCIAL",
    "urgent": "URGENCY",    "jaldi": "URGENCY",
    "official": "OFFICIAL", "letter": "OFFICIAL",
    "drop your": "DATA_HARVESTING", "gmail below": "DATA_HARVESTING"
}
category_map = {
    "internship": "ACADEMIC", "scholarship": "ACADEMIC",
    "job": "PROFESSIONAL",    "naukri": "PROFESSIONAL"
}
```

### 3.3 URL Analysis

**TLD matching:**
```python
for t in self.patterns["tld"]:
    if domain.endswith(t["value"]):
        total_risk += t["risk"]
```

**Domain blacklist:**
```python
for d in self.patterns["domain"]:
    if d["value"].lower() in domain:
        total_risk += d["risk"]
```

**Path keyword tiered logic:**
```python
context_words = ["internship", "offer", "job", "scholarship", "career", "hiring"]
# Context words in URL get 70% reduction (risk × 0.3)
# If ONLY context words match with no TLD/domain hits: cap at 0.15
if has_context and not has_threat and not any(m['type'] in ['tld','domain'] for m in matches):
    total_risk = min(0.15, total_risk)
```

---

## 4. Shield of Trust (Pillar 3)

**File:** `backend/app/services/trust_service.py`

### 4.1 Domain Trust Check (DB-backed)

```python
def check_domain(self, domain: str) -> dict:
    domain = domain.lower().strip().lstrip("www.")
    
    # 1. Exact match in verified_providers.official_url
    provider = db.query(VerifiedProvider).filter(
        VerifiedProvider.official_url.contains(domain)
    ).first()
    
    # 2. Root domain fallback (strip subdomains)
    if not provider:
        parts = domain.split('.')
        if len(parts) > 2:
            root_domain = ".".join(parts[-2:])
            provider = db.query(VerifiedProvider).filter(
                VerifiedProvider.official_url.contains(root_domain)
            ).first()
    
    if provider:
        return {"name", "category", "security_tips", "verified_at"}
    return None
```

**Trust signal:** A match gives **-0.50** risk score reduction (strongest single signal).

### 4.2 Company Impersonation Detection (Hardcoded)

Brand watchlist (from code):
```python
self.watch_list = {
    "amazon":    ["amazon.com", "amazon.in", "media-amazon.com", "amzn.to"],
    "paypal":    ["paypal.com", "paypal-objects.com", "paypal.me"],
    "google":    ["google.com", "gstatic.com", "googleapis.com", "google.co.in"],
    "microsoft": ["microsoft.com", "office.com", "outlook.com", "live.com", "msn.com"],
    "apple":     ["apple.com", "icloud.com", "me.com"],
    "netflix":   ["netflix.com"],
    "facebook":  ["facebook.com", "fb.com", "messenger.com"],
    "instagram": ["instagram.com", "ig.me"],
    "whatsapp":  ["whatsapp.com", "wa.me"],
    "binance":   ["binance.com", "bnbstatic.com"],
    "coinbase":  ["coinbase.com"],
    "metamask":  ["metamask.io"],
    "ebay":      ["ebay.com", "ebay.in"],
    "fedex":     ["fedex.com"], "ups": ["ups.com"], "dhl": ["dhl.com"],
    "stripe":    ["stripe.com"],
    "university": [".edu", "ac.uk", "edu.au", "edu.pk"],
    "internship": ["lever.co", "greenhouse.io", "internshala.com"]
}
```

Special brand regex patterns:
```python
if brand == "paypal": brand_pat = r"pay[\s-]?pal"
elif brand == "amazon": brand_pat = r"ama[\s-]?zon"
```

**Impersonation detection logic:**
1. Brand name found in text (via regex)
2. A link is present in the text
3. The link's domain does NOT match any of the brand's legitimate domains
4. → Returns `{"brand": "PayPal", "risk": "high", "reason": "CRITICAL IMPERSONATION: ..."}`
5. → `score_details["impersonation"] = 40.0`

---

## 5. URL Detection Engine

**File:** `backend/app/services/url_detector.py`

### 5.1 Shannon Entropy (DGA Detection)

```python
def calculate_entropy(self, domain: str) -> float:
    prob = [float(domain.count(c)) / len(domain) for c in dict.fromkeys(list(domain))]
    entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])
    return entropy
```

Threshold: `entropy > 4.0` → `risk += 0.25`

Reference values:
| Domain | Entropy | Status |
|---|---|---|
| `google` | 2.25 | Normal |
| `paypal` | 2.25 | Normal |
| `kj38xnq9p2m4z` | ~4.2 | Flagged (DGA) |

### 5.2 Typosquatting (Levenshtein Distance)

```python
# Popular domains to protect:
self.popular_domains = ["google.com","facebook.com","amazon.com","apple.com",
                        "microsoft.com","netflix.com","github.com","linkedin.com"]

def check_typosquatting(self, domain: str) -> list:
    clean_domain = domain.split('.')[0]   # "paypa1" from "paypa1-secure.xyz"
    hits = []
    for popular in self.popular_domains:
        pop_main = popular.split('.')[0]  # "paypal"
        if clean_domain == pop_main:
            continue  # Exact match is not typosquatting
        dist = lev_distance(clean_domain, pop_main)
        if 0 < dist <= 2:                 # Within 2 edits
            hits.append(popular)
    return hits
```

If hits found: `risk += 0.40`. Falls back to pure Python implementation if `python-Levenshtein` is not installed.

### 5.3 Homoglyph Attack Detection

14 Cyrillic/Greek → Latin mappings:
```python
self.homoglyph_map = {
    'а':'a', 'с':'c', 'е':'e', 'о':'o', 'р':'p',
    'х':'x', 'у':'y', 'і':'i', 'ј':'j', 'ѕ':'s',
    'ꙅ':'s', 'ԁ':'d', 'ԛ':'q', 'ԝ':'w'
}
```

If any homoglyph character found in domain: `risk += 0.60` (highest single-layer penalty).

### 5.4 IP Masking Detection

```python
def check_ip_masking(self, domain: str) -> bool:
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain): return True
    if re.match(r"^0x[0-9a-fA-F]+$", domain): return True  # Hex-encoded IP
    return False
```

If detected: `risk += 0.50`

### 5.5 Deep Scan (Content AI)

Only runs if:
- Domain is **not** trusted (`is_trusted = False`)
- Current `risk_score < 0.8` (avoids wasting resources on already-confirmed scams)

```python
scan_data = await self.fetch_web_content(url)  # 8s timeout, spoofed UA
# Strips <script>, <style>, <nav>, <footer>, <header>
# Feeds cleaned text to text_detector.analyze()
```

**Redirect chain analysis:**
- Trusted domain (`.edu`/`.gov`) → unverified domain: `risk += 0.35`
- Chain length > 3 hops: `risk += 0.20`

### 5.6 Geo/ASN Forensics

```python
async def _get_geo_and_asn(self, domain: str) -> dict:
    ip_address = await loop.run_in_executor(None, socket.gethostbyname, domain)
    # Queries: http://ip-api.com/json/{ip}?fields=country,city,as,org
    # Generates flag emoji: chr(127397 + ord(c)) for c in country_code
```

Returns: `{geo: {country, city, ip, flag}, asn: {asn, isp}}`

### 5.7 Full Score Table

| Signal | Risk Delta | Condition |
|---|---|---|
| Trust registry match | **-0.50** | Verified provider in DB |
| Pattern engine | Variable | DB-driven rules |
| HTTP protocol | +0.10 | Not HTTPS |
| URL shortener | +0.20 | bit.ly, tinyurl, t.co, etc. |
| Typosquatting | +0.40 | Levenshtein ≤ 2 |
| High entropy | +0.25 | Shannon > 4.0 |
| Homoglyph | +0.60 | Cyrillic/Greek chars |
| IP masking | +0.50 | Raw IPv4 or hex |
| Subdomain abuse | +0.30 | >4 dot-levels |
| External intel | +0.60 | URLScan.io malicious |
| Redirect trust jump | +0.35 | .edu/.gov → unknown |
| Redirect chain | +0.20 | >3 hops |
| Content AI (deep scan) | +0.50 | Scam in page text |

All scores capped: `risk_score = min(1.0, risk_score)`

---

## 6. Image Forensic Engine

**File:** `backend/app/services/image_detector_service.py`

### 6.1 Pipeline (9 Steps)

```
1. Load image → NumPy array (OpenCV) + PIL Image
2. OCR extraction via Tesseract
3. Platform identification (WhatsApp/Telegram/Email)
4. Text AI analysis (TextDetectorService)
5. URL extraction from OCR text → URLDetectorService per URL
6. EXIF metadata extraction
7. Laplacian Variance noise analysis
8. Multi-modal correlation (CorrelationService)
9. Weighted integrity score + final decision
```

### 6.2 Platform Detection

```python
self.platform_patterns = {
    "WhatsApp": [r"whatsapp", r"status", r"last seen", r"message"],
    "Telegram": [r"telegram", r"channel", r"group", r"join"],
    "Email":    [r"from:", r"to:", r"subject:", r"reply"]
}
```

Platform feeds directly into the Correlation Engine.

### 6.3 EXIF AI Signature Detection

Checks EXIF tags (Make=271, Model=272, Software=305, DateTime=306, Orientation=274):

```python
ai_keywords = ["stable diffusion","midjourney","firefly","dalle",
               "civitai","huggingface","generative"]
software_str = str(extracted.get("software","")).lower()
is_ai_gen = any(k in software_str for k in ai_keywords)
```

Missing EXIF entirely → `trust_level: "low"`
Camera Make present → `trust_level: "high"`

### 6.4 Laplacian Variance (Synthetic Detection)

```python
def _calculate_noise_integrity(self, image_np) -> dict:
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    is_suspiciously_smooth = variance < 120.0
    return {
        "texture_variance": float(round(variance, 2)),
        "is_suspiciously_smooth": bool(is_suspiciously_smooth),
        "score": float(1.0 if not is_suspiciously_smooth else 0.4)
    }
```

Threshold: `120.0`. Variance < 120 = "Suspiciously Smooth" = AI-generated signature.

### 6.5 Integrity Score Formula

```python
integrity_score = (
    (0.4 * (1.0 if exif_data.get("trust_level") == "high" else 0.5)) +
    (0.4 * noise_data["score"]) +
    (0.2 * (1.0 if not exif_data.get("is_ai_gen") else 0.0))
)
```

If `integrity_score < 0.7`: adds `score_details["forensics"] = round((1.0 - integrity_score) * 50, 1)`

---

## 7. PDF Forensic Engine

**File:** `backend/app/services/pdf_analyzer.py`

### 7.1 Pipeline (9 Stages)

```
Stage 1: Encryption check
  → pdf.doc.encryption is not None
  → INSTANT return: prediction="scam", confidence=0.8

Stage 2: Metadata extraction
  → pdf.metadata (Author, Creator, Producer, CreationDate)
  → Missing/anonymous author → risk += 0.5

Stage 3: Author trust verification
  → trust_service.check_domain(author)
  → Verified → risk -= 0.3
  → Generic author (admin/user/root/pc) → risk += 0.1

Stage 4: Digital signature detection
  → Raw byte scan: b"/Sig" or b"/ByteRange" in file_content
  → Found → risk -= 0.2
  → Not found → warning added to reasoning

Stage 5: Text extraction
  → pdfplumber page-by-page
  → Empty PDF → risk += 0.3 (image-only or malicious container)

Stage 6: AI content analysis
  → text_detector.analyze(full_text)
  → scam result → risk += 0.4

Stage 7: Keyword scanning
  → settings.SCAM_KEYWORDS matching (only if AI did NOT already flag)
  → hits → risk += 0.2

Stage 8: Ghost link extraction
  → Visible URLs: regex on extracted text
  → Ghost URLs: page.annots annotation structures
  → Priority: ghost URLs first (up to 10 total)
  → Concurrent analysis: asyncio.gather(*tasks, timeout=10.0)
  → Ghost link found → risk += 0.15 each
  → Scam URL found → risk += 0.4 each

Stage 9: Correlation engine
  → correlation_service.evaluate(findings)

Stage 10: Structural anomaly
  → page_count > 10 → risk += 0.1
```

### 7.2 Ghost Link Extraction

```python
# Visible URLs from text
visible_urls = set(re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text))

# Hidden annotation links
for page in pdf.pages:
    if hasattr(page, 'annots') and page.annots:
        for annot in page.annots:
            uri = annot.get('uri')
            if uri and uri.startswith('http'):
                if uri not in visible_urls:
                    ghost_urls.add(uri)

# Queue: ghost URLs first
analysis_queue = [{"url": u, "type": "ghost"} for u in list(ghost_urls)[:10]]
analysis_queue += [{"url": u, "type": "visible"} for u in list(visible_urls)[:max(0,10-len(queue))]]
```

---

## 8. Correlation Engine

**File:** `backend/app/services/correlation_service.py`

Takes findings from all detection services and evaluates 5 named cross-signal patterns:

| Rule ID | Conditions | Boost | Reason |
|---|---|---|---|
| `academic_financial_fraud` | intent=FINANCIAL AND category=ACADEMIC | +0.40 | Academic opportunities rarely demand non-standard payments |
| `social_redirection_scam` | intent=URGENCY AND platform=[WhatsApp,Telegram] | +0.35 | Scammers move to encrypted apps to avoid filters |
| `unverified_official` | metadata_trust=low AND intent=OFFICIAL | +0.30 | Official claim but no digital signatures/trust metadata |
| `high_risk_infrastructure` | url_status=suspicious AND intent=ACADEMIC | +0.25 | Student offers using high-entropy links are high-risk |
| `comment_bait_harvesting` | intent=DATA_HARVESTING | +0.30 | Legitimate employers never ask for contact info in comments |

**Evaluation:** All matching rules are summed (not exclusive). Maximum theoretical boost: `+1.60`.

**Findings structure passed to correlation:**
```python
findings = {
    "intents": ["FINANCIAL", "URGENCY"],   # from PatternService
    "categories": ["ACADEMIC"],             # from PatternService
    "platform": "WhatsApp",                 # from ImageDetector / text patterns
    "url_status": "suspicious",             # from URLDetector
    "metadata_trust": "low"                 # from TrustService / PDF metadata
}
```

---

## 9. Gamification Engine

**File:** `backend/app/utils/gamification.py`

### XP Awards (defined in route handlers)
| Action | XP | Route |
|---|---|---|
| Text scan | 10 | `detect_text.py` |
| URL scan | 15 | `detect_url.py` |
| Quiz completion | 50 | `quiz.py` |

### Level Calculation
```python
new_level = (user.xp // 100) + 1
if new_level > user.level:
    user.level = new_level
    # Level-up logged
```

### Rank Hierarchy
```python
def get_rank_title(self, level: int) -> str:
    if level <= 2:  return "Cyber Scout"
    if level <= 5:  return "Forensic Guardian"
    if level <= 10: return "Cyber Sentinel"
    return "Grand Protector"
```

### Milestone Badges
```python
def check_milestones(self, db, user_id):
    # Badge 1: First Response
    count_all = db.query(ScanRecord).filter(ScanRecord.user_id == user_id).count()
    if count_all >= 1 and "First Response" not in user.badges:
        award_badge(db, user_id, "First Response")

    # Badge 2: Phishing Hunter
    count_url = db.query(ScanRecord).filter(
        ScanRecord.user_id == user_id,
        ScanRecord.scan_type == "url"
    ).count()
    if count_url >= 10 and "Phishing Hunter" not in user.badges:
        award_badge(db, user_id, "Phishing Hunter")
```

Badges stored as JSON array on the `users` table. DB is updated atomically per badge award.

---

*Document reflects CyberShield-EDU v2.0.0 — all algorithms sourced from `backend/app/services/` and `backend/app/utils/`.*
