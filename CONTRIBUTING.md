# Contributing to CyberShield-EDU

Thank you for considering contributing to CyberShield-EDU! This document outlines everything you need to know to contribute effectively.

---

## 1. Project Structure Overview

Before contributing, familiarise yourself with the key directories:

```
backend/app/
├── routes/       # FastAPI route modules (one file per feature domain)
├── services/     # Detection & support services (core logic lives here)
├── models/       # SQLAlchemy ORM schema (schema.py — 9 tables)
├── utils/        # Auth, gamification, logger, sanitizer, rate limiter
├── config.py     # All settings — edit defaults here, override via .env
├── main.py       # App entrypoint — register new routers here
├── tasks.py      # Celery background tasks (PDF/Image processing)
└── celery_app.py # Celery + Redis configuration

frontend/
├── js/app.js         # Main controller (~916 lines) — scan logic & result rendering
├── js/api.js         # API client — all fetch() calls go through here
├── js/admin.js       # Admin dashboard logic
└── js/gamification.js # XP/badge state engine
```

---

## 2. Setting Up Your Environment

Please refer to [`docs/setup_guide.md`](docs/setup_guide.md) for full installation instructions including:
- Python virtual environment setup
- MySQL/XAMPP database initialization
- Tesseract OCR installation
- Redis and Celery worker startup
- `.env` configuration template

---

## 3. Contribution Areas

### 🧠 AI / Detection Engines
Detection services live in `backend/app/services/`. Key files:
- `text_detector.py` — NLP pipeline (DistilBERT / fine-tuned model)
- `url_detector.py` — 9-layer URL heuristic engine
- `pdf_analyzer.py` — Recursive forensic PDF audit
- `image_detector_service.py` — OCR + EXIF + texture analysis
- `pattern_service.py` — Dynamic pattern engine (loaded from DB)
- `correlation_service.py` — Multi-modal cross-engine correlation rules

**Rules for detection contributions:**
- New detection signals should be additive (increase `risk_score` additively; never override)
- All risk scores must be clamped to `[0.0, 1.0]` using `min(1.0, score)`
- Add a clear `reasoning.append(...)` string for every new signal
- New `ThreatPattern` types (`regex`, `keyword`, `tld`, `domain`) can be added directly through the Admin Panel at runtime — no code change needed

### 📊 Database / Schema Changes
- Schema is defined in `backend/app/models/schema.py`
- All schema changes **must** have a corresponding Alembic migration: `alembic revision --autogenerate -m "description"`
- Do not rely solely on `Base.metadata.create_all()` for production schema changes

### 🌐 API Routes
- Each route module in `backend/app/routes/` handles one domain
- New routes must be registered in `backend/app/main.py` with `app.include_router(...)`
- Rate-limit sensitive endpoints using `@limiter.limit("N/minute")`
- Award XP after successful scans using `gamification_service.award_xp(db, user_id, xp_amount)`

### 🖥️ Frontend
- All API calls must go through `js/api.js` — never add raw `fetch()` calls directly in HTML pages
- Scan result rendering is centralised in `renderScanResult()` in `js/app.js`
- Guest scan limit (3 free scans) is tracked via `localStorage: cs_guest_scans` — preserve this behaviour

### 🎓 Gamification
- XP milestones and badge logic live in `backend/app/utils/gamification.py`
- New badges: add a new block in `check_milestones()` with a unique badge name string
- XP awards by action type: text scan = 10 XP, URL scan = 15 XP, quiz = 50 XP

---

## 4. Scam Datasets & AI Training Data

If contributing to detection datasets or model training:
- Scam text samples go in `data/` — ensure any real examples are anonymized (remove names, phone numbers, account details)
- Do **not** commit live malicious URLs or executable files to the repository
- Roman Urdu/Hindi scam phrases are explicitly supported — contributions in these languages are welcome
- New keywords/patterns can be added via the Admin Panel (no code changes required) and are loaded from the DB at runtime

---

## 5. Pull Request Process

1. Ensure Python code is **PEP 8 compliant**
2. If changing the API interface, update `docs/api_documentation.md`
3. If changing the database schema, include the Alembic migration
4. If changing detection logic, describe the rationale (false positive impact, tested examples)
5. Submit your Pull Request targeting the `main` branch
6. At least one other developer must review and approve before merging

---

## 6. Environment Variables

The backend reads configuration from a `.env` file. Required variables:

```env
SECRET_KEY=your-jwt-signing-secret
DATABASE_URL=mysql+mysqlconnector://root:password@localhost/cybershield
REDIS_URL=redis://localhost:6379/0
URLSCAN_API_KEY=your-urlscan-api-key  # Optional — external intel is skipped if missing
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

---

## 7. Running Tests

```bash
cd backend
pytest                        # Run all tests
pytest tests/ -v              # Verbose output
python verify_api.py          # Manual API smoke test
python check_db_content.py    # Inspect database records
```
