# API Documentation — CyberShield-EDU v2.0.0

> Complete reference for every RESTful API endpoint exposed by the CyberShield-EDU FastAPI backend. All data here is derived directly from the source code.

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Authentication & Session Management](#2-authentication--session-management)
3. [Detection Endpoints](#3-detection-endpoints)
4. [Background Task Endpoints](#4-background-task-endpoints)
5. [Gamification & Progress Endpoints](#5-gamification--progress-endpoints)
6. [Awareness & Education Endpoints](#6-awareness--education-endpoints)
7. [Community Reporting Endpoints](#7-community-reporting-endpoints)
8. [Administrative Endpoints](#8-administrative-endpoints)
9. [Error Handling & Response Codes](#9-error-handling--response-codes)

---

## 1. API Overview

### 1.1 Base URL
```
http://localhost:8000
```

### 1.2 API Versioning
All core endpoints are versioned under the `/api/v1/` prefix, configured via `API_V1_STR` in `config.py`.

### 1.3 Content Types
- **Request:** `application/json` for text/URL, `multipart/form-data` for file uploads, `application/x-www-form-urlencoded` for OAuth2 login
- **Response:** All responses are `application/json`

### 1.4 Authentication
Protected endpoints require a JWT Bearer token:
```
Authorization: Bearer <token>
```
Tokens expire after **30 minutes** (`ACCESS_TOKEN_EXPIRE_MINUTES = 30`). The JWT payload contains:
```json
{ "sub": "username", "role": "student|admin", "id": 4, "exp": 1744393200 }
```

### 1.5 Rate Limiting (SlowAPI)
| Endpoint Group | Limit |
|---|---|
| Text / URL / PDF / Image detection | **5 requests/minute** per IP |
| Scam report submission | **3 requests/minute** per IP |
| Auth, Admin, Gamification | No limit |

**429 Response:**
```json
{ "error": "Rate limit exceeded", "detail": "5 per 1 minute" }
```

### 1.6 Interactive Documentation
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/api/v1/openapi.json`

### 1.7 Health Check
```
GET /
→ { "message": "CyberShield EDU API is running", "version": "2.0.0" }
```

---

## 2. Authentication & Session Management

### 2.1 Register

| Property | Value |
|---|---|
| **Endpoint** | `POST /api/v1/auth/register` |
| **Auth Required** | No |
| **Content-Type** | `application/json` |
| **HTTP Status** | `201 Created` |

**Request Body:**
```json
{
    "username": "student_ali",
    "email": "ali@university.edu",
    "password": "mypassword123"
}
```

**Success Response:**
```json
{ "message": "User created successfully", "username": "student_ali" }
```

**Error Responses:**
| Status | Detail |
|---|---|
| `400` | `"Username already registered"` |
| `400` | `"Email already registered"` |
| `500` | `"Database error: ..."` |

**Notes:**
- Password is hashed with **bcrypt** via `passlib`
- New users default to `role: "student"`, `xp: 0`, `level: 1`, `badges: []`

---

### 2.2 Login

| Property | Value |
|---|---|
| **Endpoint** | `POST /api/v1/auth/login` |
| **Auth Required** | No |
| **Content-Type** | `application/x-www-form-urlencoded` (OAuth2 form, NOT JSON) |

**Request (Form Data):**
```
username=student_ali&password=mypassword123
```

**Success Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "username": "student_ali",
        "role": "student",
        "id": 4
    }
}
```

**Error Response:**
| Status | Detail |
|---|---|
| `401` | `"Incorrect username or password"` |

**Notes:**
- JWT signed with **HS256** using `SECRET_KEY` env variable
- The `user` object is returned immediately for UI initialization

---

### 2.3 Get Current User

| Property | Value |
|---|---|
| **Endpoint** | `GET /api/v1/auth/me` |
| **Auth Required** | Yes |

**Success Response:**
```json
{
    "id": 4,
    "username": "student_ali",
    "email": "ali@university.edu",
    "role": "student",
    "xp": 340,
    "level": 4,
    "badges": ["First Response", "Phishing Hunter"]
}
```

---

## 3. Detection Endpoints

All detection endpoints log results to the `scan_records` table and award XP to authenticated users.

---

### 3.1 Text Analysis

| Property | Value |
|---|---|
| **Endpoint** | `POST /api/v1/detect/text` |
| **Auth Required** | Optional (XP awarded if authenticated: **+10 XP**) |
| **Rate Limit** | 5/minute |
| **Content-Type** | `application/json` |
| **Processing** | Synchronous |

**Request:**
```json
{ "text": "Urgent! Pay registration fee of Rs. 500 to confirm your internship." }
```

**Input sanitization:** HTML tags stripped, control characters removed, truncated to 3,000 characters before AI inference.

**Success Response:**
```json
{
    "prediction": "scam",
    "confidence": 0.85,
    "reasoning": [
        "AI Model detected Urgency/Pressure sentiment (Confidence: 0.90)",
        "Detected heuristic threat patterns: registration fee (Legacy Scam Keyword)",
        "CONTEXT ALERT: A 'recruiter' would typically never ask for 'payment' via message."
    ],
    "score_explanation": {
        "ai_analysis": 36.0,
        "patterns": 10.0,
        "context": 20.0
    },
    "metadata": {
        "has_link": false,
        "has_phone": false
    },
    "insights": {
        "sentiment": "LABEL_1",
        "complexity": "Low (Casual/Slang)",
        "is_context_flagged": true,
        "impersonated_brand": null
    },
    "recommendation": "CRITICAL: Legitimate internships NEVER ask for money. This is a scam."
}
```

**Tri-State Prediction Logic (from DB config):**
| Score Range | Prediction | Default Thresholds |
|---|---|---|
| `>= 0.7` | `"scam"` | `high = 0.7` |
| `>= 0.3 and < 0.7` | `"suspicious"` | `low = 0.3` |
| `< 0.3` | `"safe"` | — |

> Thresholds are configurable via `PUT /api/v1/admin/config/thresholds` without restart.

---

### 3.2 URL Analysis

| Property | Value |
|---|---|
| **Endpoint** | `POST /api/v1/detect/url` |
| **Auth Required** | Optional (XP: **+15 XP**) |
| **Rate Limit** | 5/minute |
| **Content-Type** | `application/json` |
| **Processing** | Synchronous (includes async external calls) |

**Request:**
```json
{ "url": "http://paypa1-secure.xyz/login/verify" }
```

**Input validation:** `javascript:`, `data:`, `file:` protocol schemes are blocked before processing. `http://` is prepended if no scheme is present.

**Success Response:**
```json
{
    "prediction": "scam",
    "confidence": 1.0,
    "scam_score": 1.0,
    "reasoning": [
        "Possible typosquatting detected for: paypal.com",
        "Uses insecure HTTP protocol",
        "Dynamic Threat Match: Detected suspicious infrastructure or bait (.xyz — Initial Config TLD)",
        "High domain entropy detected (3.85), possible machine-generated domain",
        "DEEP SCAN: AI model detected scam-like intent in the webpage's content (Confidence: 88.0%)"
    ],
    "score_explanation": {
        "patterns": 30.0,
        "protocol": 10.0,
        "typosquatting": 40.0,
        "entropy": 25.0,
        "content_ai": 50.0
    },
    "forensics": {
        "domain": "paypa1-secure.xyz",
        "geo_location": {
            "country": "United States",
            "city": "Los Angeles",
            "ip": "104.21.3.2",
            "flag": "🇺🇸"
        },
        "asn_info": {
            "asn": "AS13335",
            "isp": "Cloudflare, Inc."
        },
        "trust_info": null
    },
    "metadata": {
        "entropy": 3.85,
        "is_trusted": false,
        "deep_scan_executed": true,
        "redirect_chain": ["http://paypa1-secure.xyz/login/verify"]
    },
    "redirect_chain": ["http://paypa1-secure.xyz/login/verify"]
}
```

**Risk Score Contributions:**
| Check | Risk Delta | Trigger |
|---|---|---|
| Trust Registry match | **-0.50** | Verified provider in DB |
| Pattern Engine (TLD/domain/keyword) | Variable | DB-driven pattern match |
| HTTP protocol | +0.10 | Not HTTPS |
| URL shortener (bit.ly, tinyurl, etc.) | +0.20 | Shortener in domain |
| Typosquatting (Levenshtein ≤ 2) | +0.40 | Close match to popular domain |
| High entropy (DGA, >4.0) | +0.25 | Shannon entropy threshold |
| Homoglyph attack (Cyrillic chars) | +0.60 | Foreign lookalike characters |
| IP masking (raw IP or hex) | +0.50 | IP address as domain |
| Subdomain abuse (>4 levels) | +0.30 | Excessive nesting |
| External intel (URLScan.io malicious) | +0.60 | API verdict |
| Redirect: trusted→untrusted jump | +0.35 | .edu/.gov to unknown TLD |
| Long redirect chain (>3 hops) | +0.20 | Hop count |
| Deep content AI (scam on page) | +0.50 | AI result on fetched HTML |

All scores are capped at `min(1.0, risk_score)`.

---

### 3.3 PDF Analysis

| Property | Value |
|---|---|
| **Endpoint** | `POST /api/v1/detect/pdf` |
| **Auth Required** | Optional |
| **Rate Limit** | 5/minute |
| **Content-Type** | `multipart/form-data` |
| **Processing** | **Asynchronous** — returns `task_id`, poll `/tasks/{id}` |
| **File Field** | `file` |
| **Validation** | Must end in `.pdf` |

**Initial Response (202):**
```json
{
    "task_id": "a3f9c2b1-...",
    "status": "processing",
    "message": "Analysis started in background"
}
```

**Final Result (via task polling):**
```json
{
    "prediction": "scam",
    "confidence": 0.75,
    "scam_score": 0.75,
    "reasoning": [
        "No digital signature found. Use caution with official-looking offer letters.",
        "Suspicious document author: admin",
        "AI Analysis: AI Model detected Urgency/Pressure sentiment (Confidence: 0.88)",
        "Detected suspicious keywords: registration fee, bank transfer",
        "Ghost-Link Detected: Hidden structural URI identified (http://hidden-scam.xyz/track)",
        "High-Risk URL detected inside PDF: http://hidden-scam.xyz/track"
    ],
    "correlation_report": {
        "boost": 0.3,
        "reasons": ["🔍 Pattern Match: This document claims to be an official offer but lacks verifying digital signatures or trusted metadata."]
    },
    "ai_analysis": {
        "prediction": "scam",
        "confidence": 0.88,
        "reasoning": ["AI Model detected Urgency/Pressure sentiment (Confidence: 0.88)"]
    },
    "metadata": {
        "filename": "offer_letter.pdf",
        "forensics": {
            "author": "admin",
            "creator_tool": "Microsoft Word",
            "producer": "macOS Quartz PDFContext",
            "creation_date": "D:20260415",
            "is_encrypted": false,
            "is_digitally_signed": false,
            "trust_info": null
        },
        "page_count": 3,
        "found_urls_count": 2
    },
    "url_analysis": [
        {
            "url": "http://hidden-scam.xyz/track",
            "type": "ghost",
            "prediction": "scam",
            "score": 0.95,
            "forensics": { "geo_location": {...} },
            "redirect_chain": ["http://hidden-scam.xyz/track"]
        }
    ]
}
```

**Analysis Pipeline (in order):**
1. Encryption check → instant `scam` verdict (confidence: 0.8) if encrypted
2. Metadata inspection (Author, Creator, Producer)
3. Author trust verification against `verified_providers` DB table
4. Digital signature detection (raw byte scan for `/Sig`, `/ByteRange`)
5. Full text extraction (all pages via pdfplumber)
6. AI content analysis (TextDetectorService)
7. Scam keyword scanning (from settings + DB keywords)
8. Ghost link extraction (PDF annotation structures)
9. Recursive concurrent URL analysis (up to 10 URLs, 10s timeout)
10. Multi-modal correlation analysis
11. Structural anomaly check (>10 pages: +0.1)

---

### 3.4 Image Analysis

| Property | Value |
|---|---|
| **Endpoint** | `POST /api/v1/detect/image` |
| **Auth Required** | Optional |
| **Rate Limit** | 5/minute |
| **Content-Type** | `multipart/form-data` |
| **Processing** | Asynchronous (Celery) |
| **File Field** | `file` |

**Final Result:**
```json
{
    "prediction": "suspicious",
    "confidence": 0.62,
    "scam_score": 0.62,
    "reasoning": [
        "Visual artifacts suggest origin: WhatsApp",
        "AI Model detected Urgency/Pressure sentiment (Confidence: 0.78)"
    ],
    "score_explanation": {
        "content_ai": 40.0,
        "forensics": 15.0
    },
    "correlation_report": {
        "boost": 0.35,
        "reasons": ["🔍 Pattern Match: Scammers often move conversations to encrypted apps to avoid corporate security filters."]
    },
    "ai_analysis": {
        "prediction": "scam",
        "confidence": 0.78,
        "reasoning": [...]
    },
    "forensic_report": {
        "integrity_score": 42.0,
        "metadata_trust": "low",
        "texture_analysis": "Suspiciously Smooth",
        "is_synthetic": true
    },
    "metadata": {
        "filename": "screenshot.png",
        "forensics": {
            "exif": {
                "tags": {},
                "status": "Suspicious: No Metadata Found",
                "is_ai_gen": false,
                "trust_level": "low"
            },
            "noise": {
                "texture_variance": 84.3,
                "is_suspiciously_smooth": true,
                "score": 0.4
            },
            "platform": "WhatsApp"
        }
    },
    "url_analysis": []
}
```

**Integrity Score Formula:**
```
integrity = (0.4 × exif_trust) + (0.4 × noise_score) + (0.2 × not_ai_gen)
```
Where `noise_score = 1.0` if variance ≥ 120, else `0.4` (Laplacian Variance threshold).

---

### 3.5 Scan History

| Property | Value |
|---|---|
| **Endpoint** | `GET /api/v1/detect/history` |
| **Auth Required** | Yes |

**Response:**
```json
[
    {
        "id": 42,
        "scan_type": "text",
        "input_data": "Urgent! Pay registration fee...",
        "prediction": "scam",
        "confidence": 0.85,
        "reasoning": ["AI Model detected Urgency/Pressure sentiment..."],
        "created_at": "2026-05-01T14:30:00"
    }
]
```

---

## 4. Background Task Endpoints

### 4.1 Get Task Status

| Property | Value |
|---|---|
| **Endpoint** | `GET /api/v1/tasks/status/{task_id}` |
| **Auth Required** | No |

**Response — Pending:**
```json
{ "task_id": "a3f9c2b1-...", "status": "PENDING" }
```

**Response — Success:**
```json
{
    "task_id": "a3f9c2b1-...",
    "status": "SUCCESS",
    "result": { "prediction": "scam", "confidence": 0.85, ... }
}
```

**Response — Failure:**
```json
{ "task_id": "a3f9c2b1-...", "status": "FAILURE", "error": "..." }
```

**Polling:** The frontend (`api.js`) polls every 2 seconds via `pollUntilFinished(task_id)` until status is `SUCCESS` or `FAILURE`.

---

## 5. Gamification & Progress Endpoints

### 5.1 Get Student Profile

| Property | Value |
|---|---|
| **Endpoint** | `GET /api/v1/gamification/profile` |
| **Auth Required** | Yes |

**Response:**
```json
{
    "username": "student_ali",
    "email": "ali@university.edu",
    "xp": 340,
    "level": 4,
    "rank": "Forensic Guardian",
    "badges": ["First Response", "Phishing Hunter"],
    "stats": {
        "total_scans": 25,
        "url_scans": 12,
        "image_scans": 8,
        "pdf_scans": 5
    },
    "next_level_xp": 400,
    "progress_percent": 40.0
}
```

**Level formula:** `level = (xp // 100) + 1`

**Level progress:**
```
next_level_xp = level × 100
points_in_level = xp - (level - 1) × 100
progress_percent = (points_in_level / 100) × 100
```

**Rank Hierarchy:**
| Level | Rank |
|---|---|
| 1–2 | Cyber Scout |
| 3–5 | Forensic Guardian |
| 6–10 | Cyber Sentinel |
| 11+ | Grand Protector |

**XP Awards by action:**
| Action | XP |
|---|---|
| Text scan | 10 |
| URL scan | 15 |
| Quiz completion | 50 |

**Badge Milestones:**
| Badge | Condition |
|---|---|
| First Response | 1st scan of any type |
| Phishing Hunter | 10 URL scans completed |

---

## 6. Awareness & Education Endpoints

### 6.1 Get All Awareness Content

| Property | Value |
|---|---|
| **Endpoint** | `GET /awareness` (root level) |
| **Auth Required** | No |

Returns all records from the `awareness_content` DB table (category, title, description, difficulty, link, examples, path_id, path_order).

---

### 6.2 Get Quiz Questions

| Property | Value |
|---|---|
| **Endpoint** | `GET /api/v1/awareness/questions?limit=5` |
| **Auth Required** | No |

Returns a **random sample** of `limit` quiz questions from the `quiz_questions` table.

**Response:**
```json
[
    {
        "id": 1,
        "content": "You receive a WhatsApp message offering a Rs. 50,000/month internship at Google but they ask for Rs. 500 processing fee.",
        "content_type": "text",
        "is_scam": true,
        "explanation": "Legitimate employers never ask for money. This is a classic advance-fee scam."
    }
]
```

**Error:** `404` if the `quiz_questions` table is empty — seed it with `backend/scripts/seed_quiz.py`.

---

### 6.3 Submit Quiz Completion

| Property | Value |
|---|---|
| **Endpoint** | `POST /api/v1/awareness/submit` |
| **Auth Required** | Yes |

Awards **50 XP** to the authenticated user.

**Response:**
```json
{ "message": "Quiz completed, XP awarded!", "xp_gained": 50 }
```

---

## 7. Community Reporting Endpoints

### 7.1 Submit Scam Report

| Property | Value |
|---|---|
| **Endpoint** | `POST /api/v1/report/reports` |
| **Auth Required** | No |
| **Rate Limit** | 3/minute |
| **Content-Type** | `multipart/form-data` |

**Form Fields:**
| Field | Type | Required | Description |
|---|---|---|---|
| `company_name` | string | Yes | Name of the fraudulent company/entity |
| `description` | string | Yes | Description of the scam |
| `is_anonymous` | boolean | No (default: `true`) | Whether to link to user account |
| `evidence` | file | No | Screenshot or document evidence |

**Response:**
```json
{ "status": "success", "message": "Scam report submitted successfully", "report_id": 15 }
```

**Notes:**
- Evidence files saved to `uploads/reports/` with timestamped filenames (`YYYYMMDD_HHMMSS_filename`)
- If DB save fails after file upload, the orphaned file is deleted automatically
- Reports are created with `status: "pending"` — no admin endpoint exists yet to update status

---

### 7.2 Get Recent Reports (Ticker)

| Property | Value |
|---|---|
| **Endpoint** | `GET /api/v1/report/recent` |
| **Auth Required** | No |

Returns the 5 most recent reports, used to populate the homepage scam ticker.

**Response:**
```json
[
    { "company_name": "FakeTech Ltd", "description": "Offered job but asked for Rs. 1000 processing fee..." }
]
```

---

## 8. Administrative Endpoints

> **All admin endpoints require `role: "admin"` in the JWT.** Non-admin requests receive `403 Forbidden`.

### 8.1 System Statistics

| Endpoint | `GET /api/v1/admin/system/stats` |
|---|---|

**Response:**
```json
{
    "total_scans": 1250,
    "scams_detected": 487,
    "scam_rate": "38.9%",
    "total_users": 84,
    "active_users": 12,
    "active_rules": 42,
    "uptime": "5h 20m",
    "health": "99.9%",
    "growth_24h": "+23",
    "trends": [
        { "date": "2026-05-01", "count": 45 },
        { "date": "2026-05-02", "count": 68 }
    ],
    "distribution": { "text": 600, "url": 400, "pdf": 150, "image": 100 }
}
```

**Notes:**
- `active_users` = distinct users who scanned in last 24h
- `trends` = daily scan counts for last 7 days
- `uptime` calculated from server process start time

---

### 8.2 Scan Logs

| Endpoint | `GET /api/v1/admin/logs?limit=50` |
|---|---|

**Response:**
```json
{
    "logs": [
        {
            "time": "02:30 PM",
            "type": "Text",
            "preview": "Urgent! Pay registration fee...",
            "prediction": "scam",
            "confidence": "85%",
            "status": "scam"
        }
    ]
}
```

---

### 8.3 User List

| Endpoint | `GET /api/v1/admin/users?limit=20` |
|---|---|

**Response:**
```json
{
    "users": [
        {
            "name": "student_ali",
            "email": "ali@university.edu",
            "role": "student",
            "joined": "May 2026",
            "status": "Online",
            "count": 25
        }
    ]
}
```

Note: `status` is hardcoded to `"Online"` (real-time status tracking is not yet implemented).

---

### 8.4 Threat Pattern Management

**Get all patterns:**
```
GET /api/v1/admin/patterns
→ { "patterns": [ {id, pattern_type, value, risk_score, description, is_active} ] }
```

**Add a new pattern (hot-reloads immediately):**
```
POST /api/v1/admin/patterns
Body: { "type": "regex|keyword|tld|domain", "value": "...", "risk": 0.2, "description": "..." }
→ { "message": "Dynamic pattern added and deployed." }
```

---

### 8.5 Keyword Management

```
GET  /api/v1/admin/keywords     → { "keywords": ["registration fee", ...] }
POST /api/v1/admin/keywords     → Body: { "keyword": "new phrase" }
```

Both pattern and keyword changes immediately call `pattern_service.load_from_db()` — no restart needed.

---

### 8.6 Detection Thresholds

**Get thresholds:**
```
GET /api/v1/admin/config/thresholds
→ { "low": 0.3, "high": 0.7 }
```

**Update thresholds:**
```
PUT /api/v1/admin/config/thresholds
Body: { "low": 0.25, "high": 0.65 }
→ { "message": "Thresholds updated successfully", "config": { "low": 0.25, "high": 0.65 } }
```

Changes take effect immediately on all subsequent scans via `config_helper.get_thresholds()`.

---

### 8.7 Update Educational Resources

```
POST /api/v1/admin/resources
Body: { "content": [ { "title": "...", "category": "..." } ] }
```

Writes to `data/educational_resources.json` and hot-reloads `awareness_service.content`.

---

## 9. Error Handling & Response Codes

### Standard Error Format
All errors return:
```json
{ "detail": "Human-readable error message" }
```

### HTTP Status Code Reference

| Code | Meaning | When Used |
|---|---|---|
| `200` | OK | Successful request |
| `201` | Created | User registration |
| `400` | Bad Request | Validation failure, duplicate username/email, non-PDF file |
| `401` | Unauthorized | Missing/expired/invalid JWT |
| `403` | Forbidden | Non-admin accessing admin endpoint |
| `404` | Not Found | User not found, empty quiz library |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unhandled exception (logged, details hidden from response) |

### Global Exception Handler
All unhandled exceptions are caught by the global handler in `main.py`:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global Error: {exc} | Path: {request.url.path}")
    return JSONResponse(status_code=500, content={
        "detail": "An internal server error occurred. Our team has been notified."
    })
```
Stack traces are **never** exposed to clients.

---

*Document reflects CyberShield-EDU v2.0.0 — derived from direct source code analysis of `backend/app/routes/` and `backend/app/services/`.*
