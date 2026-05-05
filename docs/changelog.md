# Changelog — CyberShield-EDU

> Complete version history documenting the evolution of CyberShield-EDU from initial concept through current release. Each version entry includes new features, improvements, bug fixes, and breaking changes.

---

## Version Naming Convention

```
v{MAJOR}.{MINOR}.{PATCH}

MAJOR — Fundamental architecture changes, new detection pillars
MINOR — Feature additions, engine enhancements
PATCH — Bug fixes, configuration changes, documentation updates
```

---

## [v2.1.0] — April 16, 2026

### 🚀 New Features
- **Multi-Modal Contextual Correlation Engine** — Moves beyond isolated scoring to behavioral pattern analysis.
  - Linked findings (Context + Intent) now boost risk scores non-linearly.
  - Correlation Intelligence section added to the UI for human-readable reasoning.
- **Localized & Transliterated Detection** — optimized for South Asian student populations.
  - Full support for **Roman Urdu and Hindi** detection (e.g., *"fees jama karwaein"*, *"select ho gaye"*).
  - Transliterated intent mapping for financial and urgency markers.
- **Social Engineering Defense Shields** — Specialized detection for modern platform tactics.
  - **Comment Bait Shield** (LinkedIn/FB): Detects patterns like *"Drop your Gmail/WhatsApp below"* to harvest data.
  - **Redirect Chain Forensics**: Improved detection of "Encrypted Redirection" to Telegram/WhatsApp.
- **Dynamic System Configuration** — Real-time detection tuning via the Admin Dashboard.
  - Configurable sensitivity thresholds (`low` and `high`) stored in the database.
  - Sub-second cached configuration management via `ConfigHelper`.

### 🔧 Improvements
- **Admin Dashboard v2.1** — Added real-time category distribution charts and category-based analytics.
- Integrated `CorrelationService` into all forensic pillars (Text, URL, Image, PDF).
- Performance: Optimized `PatternService` with intent-based grouping for faster multi-vector matching.

---

## [v2.0.0] — April 2026

### 🚀 New Features
- **Granular Score Breakdowns** — All detection engines now provide per-layer/per-component score attribution
  - Text detection: `score_explanation` with AI, patterns, impersonation, and context contributions
  - URL detection: `score_explanation` with per-heuristic-layer risk values
  - PDF detection: `score_explanation` with encryption, metadata, signature, AI, keyword, URL, ghost link, and structure scores
  - Image detection: `score_explanation` with OCR content, URL analysis, texture integrity, metadata trust, and AI signature scores
- **Company Impersonation Detection** — TrustService now detects brand-domain mismatches (10+ brands in watchlist)
- **Context-Aware Social Engineering Analysis** — Role-action conflict matrix catches authority-based manipulation
- **Enhanced URL Forensics** — GeoIP/ASN enrichment, redirect chain analysis with reputation jump detection
- **URL Deep Scan** — Fetches target webpage content and runs AI NLP classification
- **Transparent Detection Intelligence** — Frontend renders detailed reasoning, score breakdowns, and forensic insights
- **Quick Tips Removal** — Cleaned up UI by removing quick tips panels for streamlined interface

### 🔧 Improvements
- Enhanced Pattern Engine with URL path keyword scanning ("Bait Shield")
- Improved text detection pipeline with linguistic complexity analysis
- Better error handling across all detection services
- Frontend UI polish and glassmorphism refinements
- Added production-ready fallback for all detection pipeline stages

### 📖 Documentation
- Complete rewrite of all 8 documentation files with in-depth explanations
- Added 7 new documentation files: database schema, detection engines, security whitepaper, testing guide, changelog, glossary, FAQ

---

## [v1.5.0] — April 2026

### 🚀 New Features
- **Gamification v1.5** — Full database persistence for XP, levels, and badges
  - Client-side state machine with sync engine
  - Confetti celebration animations on level-up
  - Toast notification system for achievements
  - Anti-abuse XP cap (150 per reward call)
- **Developer API** — Public endpoint access via managed API keys
  - SHA-256 hashed key storage
  - Daily rate limiting (1,000 requests/key)
  - Sandbox mode for integration testing
- **Chrome Browser Extension** — Manifest V3 text analysis popup
- **Administrative Dashboard** — System stats, keyword CRUD, pattern management
- **Scam Reporting** — Community-submitted reports with evidence upload
- **Scan History** — Persistent per-user audit trail

### 🔧 Improvements
- Database seeding with educational content, verified providers, and quiz questions
- Expanded quiz question library
- Rate limiting implementation via SlowAPI

---

## [v1.0.0] — March 2026

### 🚀 Core Platform Launch
- **Pillar 1: Text Detection** — DistilBERT multilingual NLP scam classifier (104 languages)
- **Pillar 2: Pattern Engine** — Dynamic keyword, regex, TLD, and domain matching
- **Pillar 3: Shield of Trust** — Verified provider whitelist and domain verification
- **Pillar 4: URL Detection** — 9-layer heuristic phishing scanner
  - Protocol analysis, URL shortener detection, typosquatting (Levenshtein distance)
  - Shannon entropy (DGA detection), homoglyph detection (14 Cyrillic characters)
  - IP masking, subdomain abuse, external intelligence (URLScan.io)
- **Pillar 5: Image Detection** — OCR text extraction + AI content analysis
  - Tesseract OCR with adaptive preprocessing
  - EXIF metadata auditing for AI generation tool signatures
  - Laplacian Variance texture analysis for synthetic image detection
  - QR code detection and URL scanning
  - Platform identification (WhatsApp, Telegram, Email)
- **Pillar 7: PDF Analysis** — Forensic document analysis
  - Metadata inspection (author, creator, producer)
  - Encryption and digital signature detection
  - Visible and ghost URL extraction
  - Recursive URL analysis via URL Detector (parallel, capped at 10)

### 🏗️ Infrastructure
- FastAPI backend with async route handlers
- SQLAlchemy ORM with MySQL/MariaDB (XAMPP)
- Celery background task processing with Redis broker
- JWT authentication with PBKDF2-SHA256 password hashing
- Role-based access control (student/admin)
- CORS middleware with explicit origin whitelist
- Request logging middleware with RotatingFileHandler
- Global exception handler with context logging

### 🎨 Frontend
- 19-page vanilla HTML/CSS/JS frontend
- Glassmorphism design system with CSS Custom Properties
- Light/Dark theme support with runtime toggle
- Google Fonts (Inter/Outfit) typography
- Responsive layouts for desktop use

---

## [v0.5.0] — March 2026

### 🚀 Prototype Phase
- Initial FastAPI project structure
- Basic text classification endpoint
- MySQL database schema design
- User registration and login
- Initial Hugging Face model integration

---

## [v0.1.0] — February 2026

### 🎯 Concept Phase
- Project ideation and threat landscape research
- 10-pillar strategic framework defined
- Technology stack selection
- Repository initialization

---

## Deprecated / Paused Features

### Pillar 1: Security Tutor (LLM Scam Explainer)
- **Status:** ⏸️ PAUSED since v1.5.0
- **Reason:** Resource requirements exceed typical student laptop capabilities
- **Code:** Preserved in `explainer_service.py` and `routes/explainer.py` (commented out in `main.py`)
- **Future:** Will be activated when deployed on servers with adequate GPU resources

### Audio Vishing Detection
- **Status:** ❌ REMOVED from platform
- **Reason:** Feature was a research-only placeholder; navigation links removed in v2.0.0 final release to ensure a polished user experience.

---

## Migration Notes

### v1.x → v2.0
- **No breaking API changes** — All v1.x API endpoints remain compatible
- **New response fields** — `score_explanation`, `forensics`, and enhanced `reasoning` are additive (non-breaking)
- **Frontend updates** — Scan result rendering updated to display new forensic data
- **Database** — No schema migrations required. New columns (`weight` on `scam_keywords`) are handled gracefully by SQLAlchemy defaults

### v0.x → v1.0
- **Breaking:** Complete API restructure from prototype to production routes
- **Breaking:** Database schema finalized — requires fresh `setup_xampp.sql` import
- **Breaking:** Frontend rewired for new endpoint structure

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/) conventions.*
