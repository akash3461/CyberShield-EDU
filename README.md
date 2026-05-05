# CyberShield-EDU 🛡️

**An advanced, AI-powered cybersecurity protection platform designed specifically to help students detect and avoid online scams, phishing links, and fraudulent documents.**

![Status](https://img.shields.io/badge/Status-v2.0.0--Stable-brightgreen)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![ML](https://img.shields.io/badge/AI-Multilingual--NLP-FF9900)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## 📌 Executive Summary

Students are frequently targeted by sophisticated cyber scams involving fake internships, fraudulent scholarships, and phishing links. **CyberShield-EDU** provides a unified, AI-powered digital safety dashboard. It analyzes suspicious content across four media types — text, URLs, PDFs, and images — using a layered detection architecture that combines machine learning, heuristic pattern matching, external threat intelligence, and multi-modal correlation logic. Beyond detection, the platform includes a gamified security academy, phishing simulations, community scam reporting, and a real-time admin dashboard.

---

## ✨ Core Capabilities & Features (v2.0.0)

### 1. 🧠 Multi-Modal Scam Detection
Four independent detection engines, each with a dedicated API endpoint:
- **Text Engine** — Fine-tuned `scam_detector_v1` model (with `distilbert-base-multilingual-cased` as fallback). Detects urgency/pressure, unexpected reward, and impersonation patterns.
- **URL Engine** — 9-layer heuristic analysis: typosquatting (Levenshtein distance), Shannon entropy (DGA detection), homoglyph attacks, IP masking, subdomain abuse, redirect chain tracking, and AI-powered deep content scan.
- **PDF Engine** — Forensic audit: encryption detection, ghost link extraction (hidden annotations), recursive URL scanning, metadata inspection, and digital signature verification.
- **Image Engine** — OCR text extraction via Tesseract, EXIF AI-signature detection (Stable Diffusion, MidJourney, DALL-E, etc.), and Laplacian Variance texture analysis for synthetic image detection.

### 2. 🌍 Bilingual Detection (English + Roman Urdu/Hindi)
Scam keywords and intent maps cover both English and regional transliterations:
- English: `"registration fee"`, `"send money"`, `"security deposit"`
- Roman Urdu/Hindi: `"fees jama karwaein"`, `"paise bhejein"`, `"jaldi karein"`, `"mubarak ho"`, `"select ho gaye"`

### 3. 🔗 Multi-Modal Correlation Engine
The `CorrelationService` detects compound threat patterns that no single engine catches alone:
- **Academic Financial Fraud** — Financial intent + Academic category → +0.40 boost
- **Social Redirection Scam** — Urgency + WhatsApp/Telegram platform → +0.35 boost
- **Unverified Official Document** — Low metadata trust + Official intent → +0.30 boost
- **Data Harvesting Bait** — Detected "drop your Gmail/WhatsApp" patterns → +0.30 boost
- **High-Risk Link Infrastructure** — Suspicious URL + Academic context → +0.25 boost

### 4. 🛡️ Shield of Trust (Whitelist Engine)
- **Domain Trust Registry** — Verified providers database grants a **-0.50 risk score** offset to known institutions and career portals.
- **Company Impersonation Detection** — Detects if text claims to be from Amazon, PayPal, Google, Microsoft etc. while the embedded link points to an unrelated domain.

### 5. 🎓 Gamified Security Academy
- **XP & Leveling** — Earn XP through scans (10–15 XP each) and quiz completion (50 XP). `level = floor(XP / 100) + 1`.
- **Rank Hierarchy** — Cyber Scout → Forensic Guardian → Cyber Sentinel → Grand Protector.
- **Badges** — First Response (1st scan), Phishing Hunter (10 URL scans).
- **Interactive Quizzes** — "Spot the Scam" modules from the forensic quiz library.

### 6. 📊 Admin Command Center
- Real-time platform analytics: total scans, scam rate, 7-day trend data, scan type distribution.
- Live keyword and threat-pattern management with hot-reload (no restart required).
- **Dynamic Thresholds** — Adjustable `safe/suspicious/scam` cutoff points stored in the DB.

### 7. 🌐 Community Scam Reporting
- Anonymous or identified scam reports with file evidence upload.
- Live "Scam Ticker" on the homepage displaying recent community reports.
- Rate-limited (3/minute) to prevent abuse.

### 8. 🔌 Browser Extension
- Chrome Manifest V3 extension for real-time text analysis directly from the browser.

---

## 🏗️ System Architecture

CyberShield-EDU uses a decoupled frontend-backend architecture:

```
Frontend (Vanilla HTML/JS/CSS)  ←→  FastAPI Backend (Python)
         19 HTML Pages                    ↓
         4 JS Modules              MySQL Database (SQLAlchemy)
         Chrome Extension                 ↓
                                   Celery + Redis (Async Tasks)
                                         ↓
                                  AI Models (HuggingFace)
```

For a full deep-dive, see [Architecture Overview](./docs/architecture.md).

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **MySQL / XAMPP** — Database backend
- **Redis** — Celery message broker (for PDF/Image background tasks)
- **Tesseract OCR** — Required for image scanning (`C:\Program Files\Tesseract-OCR\`)

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
# Create .env file (see docs/setup_guide.md for template)
python main.py                 # Starts on http://localhost:8000
```

### Start Celery Worker (required for PDF/Image scans)
```bash
cd backend
celery -A app.celery_app worker --loglevel=info -P solo
```

### Frontend
```bash
cd frontend
python -m http.server 5500
# Access at http://localhost:5500
```

### Database Initialization
```sql
-- Import the setup script in phpMyAdmin or MySQL CLI:
SOURCE backend/setup_xampp.sql;
```

Tables are also auto-created on first startup via `Base.metadata.create_all()`.

---

## 📁 Project Structure

```
CyberShield-EDU/
├── backend/
│   ├── app/
│   │   ├── ai_models/scam_detector_v1/   # Fine-tuned NLP model
│   │   ├── api/                          # (Reserved)
│   │   ├── models/schema.py              # 9 SQLAlchemy table definitions
│   │   ├── routes/                       # 15 FastAPI route modules
│   │   ├── services/                     # 13 detection & support services
│   │   ├── utils/                        # Auth, gamification, limiter, logger
│   │   ├── config.py                     # Centralized settings (env + defaults)
│   │   ├── database.py                   # SQLAlchemy engine & session
│   │   ├── main.py                       # FastAPI app entry point
│   │   ├── celery_app.py                 # Celery + Redis configuration
│   │   └── tasks.py                      # Background task definitions
│   ├── requirements.txt
│   └── setup_xampp.sql
├── frontend/
│   ├── *.html                            # 19 application pages
│   ├── js/                              # app.js, api.js, admin.js, gamification.js
│   └── css/                             # main.css, gamification.css
├── extension/
│   ├── manifest.json                    # Chrome MV3 manifest
│   ├── popup.html
│   └── popup.js
├── docs/                                # 15 documentation files
├── alembic/                             # Database migrations
└── tests/
```

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Backend Framework | FastAPI + Uvicorn (ASGI) |
| AI/NLP | HuggingFace Transformers, PyTorch (`scam_detector_v1` / DistilBERT) |
| OCR | Tesseract (pytesseract) |
| Computer Vision | OpenCV, Pillow |
| PDF Processing | pdfplumber |
| Database | MySQL + SQLAlchemy ORM + Alembic |
| Background Tasks | Celery + Redis |
| Authentication | JWT (python-jose, HS256) + bcrypt (passlib) |
| Rate Limiting | SlowAPI |
| External Intel | URLScan.io API (httpx) |
| Geo/ASN Lookup | ip-api.com (aiohttp) |
| Typosquatting | python-Levenshtein |
| Web Scraping | aiohttp + BeautifulSoup4 |
| Frontend | Vanilla HTML5 / CSS3 / JavaScript (ES6+) |
| Browser Extension | Chrome Manifest V3 |

---

## 📚 Documentation

| Document | Description |
|---|---|
| [Setup Guide](./docs/setup_guide.md) | Full installation, environment variables, and troubleshooting |
| [Architecture](./docs/architecture.md) | System design, data flow, and deployment topology |
| [API Documentation](./docs/api_documentation.md) | Complete REST API reference with request/response schemas |
| [Detection Engines](./docs/detection_engines.md) | Technical deep-dive into all detection algorithms |
| [Database Schema](./docs/database_schema.md) | All 9 tables, columns, and relationships |
| [User Manual](./docs/user_manual.md) | End-user guide for all platform features |
| [Admin Guide](./docs/admin_guide.md) | Admin dashboard and system configuration |
| [Security Whitepaper](./docs/security_whitepaper.md) | Security architecture and threat model |
| [Testing Guide](./docs/testing_guide.md) | Running tests and validation scripts |
| [Changelog](./docs/changelog.md) | Version history and release notes |
| [Roadmap](./docs/roadmap.md) | Planned features and future development |
| [FAQ](./docs/faq.md) | Frequently asked questions |

---

## ⚠️ Known Limitations

| Area | Status |
|---|---|
| **LLM Cyber-Tutor** | Paused — commented out pending GPU infrastructure upgrade |
| **Audio Vishing Detection** | Stub only — route exists but service is not implemented |
| **Browser Extension** | Targets `localhost:8000` only — requires update for production use |
| **Badges** | Only 2 milestones implemented (First Response, Phishing Hunter) |
| **Report Status Workflow** | No admin endpoint to update report status (pending/reviewed/resolved) |

---

## 📄 License & Disclaimer

This software is distributed under the [MIT License](LICENSE).

**Disclaimer:** *CyberShield-EDU is developed for educational purposes to enhance cybersecurity awareness among student populations. It does not replace professional antivirus or endpoint protection software.*
