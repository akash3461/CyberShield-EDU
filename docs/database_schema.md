# Database Schema — CyberShield-EDU v2.0.0

> Complete reference for all 9 database tables defined in `backend/app/models/schema.py`. All column types, constraints, and relationships are sourced directly from the SQLAlchemy model definitions.

---

## Overview

| Table | Purpose | Key Relationships |
|---|---|---|
| `users` | User accounts, XP, level, badges | Referenced by most tables |
| `scan_records` | Full audit log of all scans | FK → `users.id` |
| `scam_keywords` | Admin-managed scam keyword list | FK → `users.id` (added_by) |
| `threat_patterns` | Dynamic heuristic rules | FK → `users.id` (added_by) |
| `awareness_content` | Educational content | Standalone |
| `verified_providers` | Trusted institution whitelist | Standalone |
| `quiz_questions` | Forensic quiz library | Standalone |
| `scam_reports` | Community scam reports | FK → `users.id` (optional) |
| `system_config` | Dynamic runtime configuration | Standalone |

---

## Table Definitions

---

### `users`

Stores all user accounts including gamification state (XP, level, badges).

| Column | Type | Constraints | Default | Notes |
|---|---|---|---|---|
| `id` | Integer | PK, Index | Auto | |
| `username` | String(50) | Unique, Index | — | Used for login |
| `email` | String(100) | Unique, Index | — | |
| `hashed_password` | String(255) | — | — | bcrypt hash |
| `role` | String(20) | — | `"student"` | `"student"` or `"admin"` |
| `xp` | Integer | — | `0` | Total experience points |
| `level` | Integer | — | `1` | `floor(xp / 100) + 1` |
| `badges` | JSON | — | `[]` | List of badge name strings |
| `created_at` | DateTime(tz) | — | `func.now()` | Server-side timestamp |

**Level formula:** `level = (xp // 100) + 1`

**Rank mapping (from `gamification.py`):**
| Level | Rank |
|---|---|
| 1–2 | Cyber Scout |
| 3–5 | Forensic Guardian |
| 6–10 | Cyber Sentinel |
| 11+ | Grand Protector |

**Example record:**
```json
{
  "id": 4,
  "username": "student_ali",
  "email": "ali@university.edu",
  "role": "student",
  "xp": 340,
  "level": 4,
  "badges": ["First Response", "Phishing Hunter"],
  "created_at": "2026-04-15T10:22:00+05:30"
}
```

---

### `scan_records`

Immutable audit log. Every scan (text, URL, PDF, image) creates one record. This is the primary analytics data source for the admin dashboard.

| Column | Type | Constraints | Default | Notes |
|---|---|---|---|---|
| `id` | Integer | PK, Index | Auto | |
| `user_id` | Integer | FK(`users.id`), Index, Nullable | — | `null` for guest scans |
| `scan_type` | String(20) | — | — | `"text"`, `"url"`, `"pdf"`, `"image"` |
| `input_data` | Text | — | — | Truncated to 500 chars for privacy |
| `prediction` | String(20) | — | — | `"safe"`, `"suspicious"`, `"scam"`, `"error"` |
| `confidence` | Float | — | — | `0.0` to `1.0` |
| `reasoning` | JSON | — | — | List of reasoning strings |
| `created_at` | DateTime(tz) | — | `func.now()` | Server-side timestamp |

**Notes:**
- `user_id` is nullable — guest users (not logged in) create records with `user_id = null`
- `input_data` is capped at 500 chars to limit PII storage
- `reasoning` is stored as a JSON array of strings for rich result replay

**Example record:**
```json
{
  "id": 201,
  "user_id": 4,
  "scan_type": "url",
  "input_data": "http://paypa1-secure.xyz/login",
  "prediction": "scam",
  "confidence": 0.96,
  "reasoning": ["Possible typosquatting detected for: paypal.com", "Uses insecure HTTP protocol"],
  "created_at": "2026-05-01T14:30:00+05:30"
}
```

---

### `scam_keywords`

Legacy keyword store, pre-dating the `threat_patterns` table. Keywords here are loaded by the PatternService as `type: "keyword"` entries with `desc: "Legacy Scam Keyword"`.

| Column | Type | Constraints | Default | Notes |
|---|---|---|---|---|
| `id` | Integer | PK, Index | Auto | |
| `keyword` | String(100) | Unique, Index | — | Case-insensitive match at runtime |
| `weight` | Float | — | `0.1` | Impact on risk score (`0.0`–`1.0`) |
| `added_by` | Integer | FK(`users.id`), Nullable | — | Admin who added it |
| `created_at` | DateTime(tz) | — | `func.now()` | |

**Initial keywords (from `config.py` — loaded as fallback if table is empty):**

High-risk (direct threat):
- `registration fee`, `security deposit`, `processing fee`
- `pay for internship`, `urgent payment`, `bank transfer`
- `send money`, `crypto payment`
- Roman Urdu: `fees jama`, `jama karwaein`, `paise bhejein`, `advans`, `security jama`

Medium-risk (suspicious indicators):
- `whatsapp`, `telegram`, `limited seats`, `selected`, `immediate joining`
- `congratulations`, `mubarak ho`, `inam mila`, `select ho gaye`, `jeeti hai`
- `inbox aayein`, `jaldi karein`

Context-only (reduced weight when seen alone):
- `internship`, `job`, `offer`, `scholarship`, `recruitment`, `career`, `hiring`, `student`, `naukri`, `mulazmat`

---

### `threat_patterns`

The primary dynamic rule store. Supports four pattern types: `regex`, `keyword`, `tld`, `domain`. Loaded into in-memory cache by `PatternService` on first use and refreshed on every admin add/edit.

| Column | Type | Constraints | Default | Notes |
|---|---|---|---|---|
| `id` | Integer | PK, Index | Auto | |
| `pattern_type` | String(20) | Index | — | `"regex"`, `"keyword"`, `"tld"`, `"domain"` |
| `value` | String(500) | Unique, Index | — | The rule value |
| `risk_score` | Float | — | `0.2` | Risk contribution (`0.0`–`1.0`) |
| `description` | String(255) | Nullable | — | Human-readable explanation |
| `is_active` | Boolean | — | `True` | Inactive patterns are not loaded |
| `added_by` | Integer | FK(`users.id`), Nullable | — | |
| `created_at` | DateTime(tz) | — | `func.now()` | |

**Pattern types explained:**
| Type | Matching Method | Used By |
|---|---|---|
| `keyword` | Case-insensitive substring match | Text + URL analysis |
| `regex` | `re.search(pattern, text, re.IGNORECASE)` | Text analysis |
| `tld` | `domain.endswith(tld_value)` | URL analysis |
| `domain` | `domain_value in domain` | URL analysis |

**Initial TLDs (from `config.py`):**
`.xyz`, `.top`, `.pw`, `.zip`, `.click`, `.link`, `.bid`, `.loan`

**Admin hot-reload:** Adding a pattern via `POST /api/v1/admin/patterns` immediately calls `pattern_service.load_from_db()` — changes take effect on the next scan with no restart.

---

### `awareness_content`

Stores educational content for the Learning Academy. Content is organized into learning paths with ordering.

| Column | Type | Constraints | Default | Notes |
|---|---|---|---|---|
| `id` | Integer | PK, Index | Auto | |
| `category` | String(50) | — | — | e.g., `"phishing"`, `"internship-scams"` |
| `title` | String(255) | — | — | Module title |
| `description` | Text | — | — | Full content body |
| `difficulty` | String(20) | — | — | e.g., `"beginner"`, `"intermediate"` |
| `link` | String(500) | — | — | External resource URL |
| `examples` | JSON | — | — | Example scam scenarios |
| `path_id` | String(50) | Nullable | — | Learning path identifier e.g., `"phishing-101"` |
| `path_order` | Integer | — | `0` | Order within the learning path |
| `created_at` | DateTime(tz) | — | `func.now()` | |

**Admin update:** `POST /api/v1/admin/resources` overwrites `data/educational_resources.json` and reloads `awareness_service.content`.

---

### `verified_providers`

The "Shield of Trust" whitelist. Domains matched here receive a **-0.50 risk score offset** — the strongest trust signal in the system.

| Column | Type | Constraints | Default | Notes |
|---|---|---|---|---|
| `id` | Integer | PK, Index | Auto | |
| `name` | String(255) | Index | — | Institution name |
| `official_url` | String(500) | — | — | Official domain |
| `category` | String(50) | — | — | `"internship"`, `"scholarship"`, `"academic"`, etc. |
| `security_tips` | Text | Nullable | — | Tips shown when trust is verified |
| `verified_at` | DateTime(tz) | — | `func.now()` | |

**Trust service lookup logic:**
1. Exact domain match in `official_url`
2. Root domain match (strips subdomains)
3. If matched: returns `{name, category, security_tips, verified_at}`
4. URL detector applies **-0.50** to risk score on match

**Hardcoded brand watchlist (in `trust_service.py`, separate from DB):**
Amazon, PayPal, Google, Microsoft, Apple, Netflix, Facebook, Instagram, WhatsApp, Binance, Coinbase, MetaMask, eBay, FedEx, UPS, DHL, Stripe, and generic `.edu`/`.ac.in`/`.edu.pk` domains.

---

### `quiz_questions`

Forensic quiz library used by the "Spot the Scam" module.

| Column | Type | Constraints | Default | Notes |
|---|---|---|---|---|
| `id` | Integer | PK, Index | Auto | |
| `content` | Text | — | — | Question text or image URL |
| `content_type` | String(20) | — | — | `"text"` or `"image"` |
| `is_scam` | Boolean | — | — | Correct answer |
| `explanation` | Text | — | — | Shown after answering |
| `difficulty` | String(20) | — | — | `"easy"`, `"medium"`, `"hard"` |
| `created_at` | DateTime(tz) | — | `func.now()` | |

**Population:** Seed with `backend/scripts/seed_quiz.py`. The API returns a **random sample** of `limit` questions (default 5) per request.

---

### `scam_reports`

Community-submitted scam reports with optional file evidence.

| Column | Type | Constraints | Default | Notes |
|---|---|---|---|---|
| `id` | Integer | PK, Index | Auto | |
| `company_name` | String(255) | Index | — | Reported entity name |
| `description` | Text | — | — | Scam description |
| `evidence_path` | String(500) | Nullable | — | Relative path to uploaded file |
| `is_anonymous` | Boolean | — | `True` | Hides user identity |
| `user_id` | Integer | FK(`users.id`), Nullable | — | Optional link to registered user |
| `status` | String(20) | — | `"pending"` | `"pending"`, `"reviewed"`, `"resolved"` |
| `created_at` | DateTime(tz) | — | `func.now()` | |

**File storage:** Evidence files are saved to `uploads/reports/` with filename format `YYYYMMDD_HHMMSS_originalname`. If DB save fails after upload, the file is automatically deleted.

**Status lifecycle:** Reports start as `"pending"`. Status update endpoints are not yet implemented — this is a known gap.

---

### `system_config`

Dynamic runtime configuration store. Allows admins to adjust detection thresholds and other system settings without restarting the server.

| Column | Type | Constraints | Default | Notes |
|---|---|---|---|---|
| `id` | Integer | PK, Index | Auto | |
| `key` | String(50) | Unique, Index | — | Config key identifier |
| `value` | JSON | — | — | Config value (number, string, or object) |
| `description` | String(255) | Nullable | — | Human-readable description |
| `updated_at` | DateTime(tz) | `onupdate=func.now()` | — | Auto-updated on change |

**Known config keys:**

| Key | Value Format | Default | Description |
|---|---|---|---|
| `analysis_thresholds` | `{"low": float, "high": float}` | `{"low": 0.3, "high": 0.7}` | Tri-state prediction cutoffs |

**How thresholds work:**
- Score `>= high` → `"scam"`
- Score `>= low` and `< high` → `"suspicious"`
- Score `< low` → `"safe"`

All four detection services (text, URL, PDF, image) query these thresholds at runtime via `config_helper.get_thresholds()`. Changes via the Admin API take effect immediately.

---

## Entity-Relationship Summary

```
users (1) ──────────────── (N) scan_records
users (1) ──────────────── (N) scam_keywords      [added_by]
users (1) ──────────────── (N) threat_patterns     [added_by]
users (1) ──────────────── (N) scam_reports        [user_id, optional]

awareness_content ────────── (standalone)
verified_providers ─────────── (standalone)
quiz_questions ─────────────── (standalone)
system_config ──────────────── (standalone)
```

---

## Schema Initialization

Tables are created automatically on startup via:
```python
Base.metadata.create_all(bind=engine)  # in main.py
```

For production migrations, use Alembic:
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

The SQL setup script for XAMPP is at `backend/setup_xampp.sql`.

---

*Document reflects `backend/app/models/schema.py` in CyberShield-EDU v2.0.0.*
