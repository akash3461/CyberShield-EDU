# Complete Deployment Guide — CyberShield-EDU

> Step-by-step instructions for deploying the full CyberShield-EDU platform on a Windows machine, from scratch. This guide covers every prerequisite, configuration file, database setup, model initialization, background worker launch, and verification step in detail.

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Prerequisites Installation](#2-prerequisites-installation)
3. [Database Setup (XAMPP MySQL)](#3-database-setup-xampp-mysql)
4. [Backend Setup](#4-backend-setup)
5. [Environment Configuration (.env)](#5-environment-configuration-env)
6. [AI Model Initialization](#6-ai-model-initialization)
7. [Running the Backend Server](#7-running-the-backend-server)
8. [Background Workers (Celery + Redis)](#8-background-workers-celery--redis)
9. [Frontend Setup](#9-frontend-setup)
10. [Browser Extension Setup](#10-browser-extension-setup)
11. [Verification Checklist](#11-verification-checklist)
12. [Troubleshooting Guide](#12-troubleshooting-guide)

---

## 1. System Requirements

### 1.1. Hardware Requirements

| Component | Minimum | Recommended |
|:---|:---|:---|
| **RAM** | 4 GB | 8 GB (for concurrent model loading) |
| **Disk Space** | 3 GB | 5 GB (includes models + datasets) |
| **CPU** | Quad-core (x64) | 8+ cores (for parallel analysis) |
| **GPU** | Not required | CUDA-compatible NVIDIA GPU (for accelerated AI inference) |

### 1.2. Software Requirements

| Software | Version | Purpose | Required? |
|:---|:---|:---|:---|
| **Python** | 3.10+ | Backend runtime | ✅ Required |
| **XAMPP** | Latest | MySQL database server | ✅ Required |
| **Redis** | Latest (Windows build) | Celery message broker | ✅ Required (for PDF/Image scanning) |
| **Tesseract OCR** | 4.0+ | Image text extraction | ⚠️ Required for image analysis |
| **Git** | Latest | Version control | Optional |
| **VS Code / IDE** | Any | Development environment | Optional |
| **CUDA Toolkit** | 11.x+ | GPU acceleration | Optional |

### 1.3. Network Requirements
- **Internet access** is required for the first run to download the DistilBERT AI model (~250MB from Hugging Face).
- **URLScan.io API key** (optional) enables external threat intelligence lookups for URL analysis.

---

## 2. Prerequisites Installation

### 2.1. Python 3.10+

1. Download from [python.org/downloads](https://www.python.org/downloads/)
2. During installation, **check "Add Python to PATH"**
3. Verify:
   ```bash
   python --version
   # Expected: Python 3.10.x or higher
   ```

### 2.2. XAMPP (MySQL)

1. Download from [apachefriends.org](https://www.apachefriends.org/)
2. Install with **MySQL** and **phpMyAdmin** selected
3. Open XAMPP Control Panel

### 2.3. Redis for Windows

1. Download the latest Windows build from [github.com/tporadowski/redis/releases](https://github.com/tporadowski/redis/releases)
2. Extract to a convenient location (e.g., `C:\Redis`)
3. Verify:
   ```bash
   redis-server --version
   # Expected: Redis server v=X.X.X
   ```

### 2.4. Tesseract OCR

1. Download the Windows installer from [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and note the installation path (default: `C:\Program Files\Tesseract-OCR\`)
3. CyberShield-EDU's image service includes **self-healing path detection** that automatically discovers Tesseract at common Windows paths:
   - `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
   - `%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe`
   - System `PATH`
4. If Tesseract is installed in a non-standard location, the image analysis module will return a diagnostic error message with instructions rather than crashing.

### 2.5. C++ Redistributable (if needed)

Some Python packages (`opencv-python`, `numpy`) require Microsoft C++ Redistributable. If you encounter DLL errors:
- Download [Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

---

## 3. Database Setup (XAMPP MySQL)

### 3.1. Start MySQL

1. Open **XAMPP Control Panel**
2. Click **Start** next to **MySQL**
3. Wait for the status to turn **green**
4. Click the **Admin** button next to MySQL to open **phpMyAdmin** in your browser

### 3.2. Create Database

**Option A: Via phpMyAdmin (GUI)**
1. In phpMyAdmin, click the **"New"** button in the left sidebar
2. Enter database name: `cybershield`
3. Set collation to `utf8mb4_general_ci`
4. Click **"Create"**

**Option B: Via SQL command**
```sql
CREATE DATABASE IF NOT EXISTS cybershield CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 3.3. Import Schema and Seed Data

1. Click on the newly created `cybershield` database
2. Go to the **"Import"** tab
3. Click **"Choose File"** and select: `backend/setup_xampp.sql`
4. Click **"Go"** to execute

This script automatically creates all 8 tables and seeds the database with:

| Seed Data | Contents |
|:---|:---|
| **Admin User** | `admin` / `admin123` (role: admin) |
| **Awareness Content** | 4 educational modules (Internship Scams, Scholarship Scams, Pro Tips) |
| **Verified Providers** | 3 trusted organizations (Google, Chegg, Microsoft) |
| **Quiz Questions** | 2 starter phishing quiz questions |
| **Scam Keywords** | 8 initial detection keywords (registration fee, security deposit, etc.) |

### 3.4. Verify Tables

After import, verify that 8 tables exist in the `cybershield` database:
1. `users`
2. `scan_records`
3. `scam_keywords`
4. `awareness_content`
5. `verified_providers`
6. `quiz_questions`
7. `scam_reports`
8. `api_keys`

> **Note:** `threat_patterns` and `system_config` are created automatically by SQLAlchemy on first backend startup. They are not included in the SQL seed script.

### 3.4. Verify Tables

After import and first server startup, verify that **9 tables** exist in the `cybershield` database:
1. `users`
2. `scan_records`
3. `scam_keywords`
4. `threat_patterns`  *(created by SQLAlchemy on first run)*
5. `awareness_content`
6. `verified_providers`
7. `quiz_questions`
8. `scam_reports`
9. `system_config`  *(created by SQLAlchemy on first run)*

---

## 4. Backend Setup

### 4.1. Navigate to the Backend Directory
```bash
cd "d:\AI Projects\CyeberShield-EDU\backend"
```

### 4.2. Create and Activate a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows CMD
# OR
.\venv\Scripts\Activate.ps1  # PowerShell
```

### 4.3. Install Dependencies
```bash
pip install -r requirements.txt
```

Key packages: `fastapi`, `uvicorn`, `transformers`, `torch`, `opencv-python`, `pytesseract`, `pdfplumber`, `sqlalchemy`, `pymysql`, `celery`, `redis`, `python-jose`, `passlib`, `slowapi`, `python-Levenshtein`, `aiohttp`, `beautifulsoup4`, `python-dotenv`

> **Note:** `torch` is ~2GB. For CPU-only deployment: `pip install torch --index-url https://download.pytorch.org/whl/cpu`

---

## 5. Environment Configuration (.env)

Create `.env` in the **project root** (`CyeberShield-EDU/.env`):

```env
DEBUG=True
APP_NAME="CyberShield EDU"
API_V1_STR="/api/v1"
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8081,http://127.0.0.1:8081
SECRET_KEY="cyeber-shield-dev-secret-!@#"
DATABASE_URL=mysql+pymysql://root@127.0.0.1/cybershield
REDIS_URL=redis://localhost:6379/0
URLSCAN_API_KEY=""
```

> **⚠️ If MySQL has a root password:** `DATABASE_URL=mysql+pymysql://root:PASSWORD@127.0.0.1/cybershield`

---

## 6. AI Model Initialization

On **first startup**, the system downloads `distilbert-base-multilingual-cased` (~250MB) from Hugging Face. This is cached at `~/.cache/huggingface/hub/` and is not re-downloaded on subsequent starts.

If you have a fine-tuned model (`scam_detector_v1`), place it at:
```
backend/app/ai_models/scam_detector_v1/
```

CUDA/GPU is auto-detected — no manual configuration required.

---

## 7. Running the Backend Server

```bash
cd backend
python main.py
```

**Expected output:**
```
INFO | CyberShield - 🚀 Pre-loading AI models...
INFO | CyberShield - Model loaded: distilbert-base-multilingual-cased
INFO | CyberShield - CUDA Available: False, Using: CPU
INFO | Uvicorn running on http://0.0.0.0:8000
```

**Verify:** Visit `http://localhost:8000/docs` — Swagger UI should load.

---

## 8. Background Workers (Celery + Redis)

Background workers are required for **PDF analysis** and **Image forensics** (these are asynchronous operations). Text and URL scans work without workers.

### 8.1. Start Redis Server

Open a **new terminal window** and run:
```bash
redis-server
```

Or if Redis is installed as a Windows service, it may already be running. Verify:
```bash
redis-cli ping
# Expected response: PONG
```

### 8.2. Start Celery Worker

Open another **new terminal window**:
```bash
cd backend
venv\Scripts\activate
celery -A app.tasks worker --loglevel=info -P solo
```

### 8.3. Expected Celery Output

```
 -------------- celery@DESKTOP-XXX v5.x.x (dawn-chorus)
--- ***** -----
-- ******* ---- Windows-10
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         worker:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 1 (solo)
-- ******* ---- .> task events: OFF (enable -E)
--- ***** -----
 -------------- [queues]
                .> celery       exchange=celery(direct) key=celery

[tasks]
  . process_image_task
  . process_pdf_task

[2026-04-11 14:35:00] Connected to redis://localhost:6379/0
[2026-04-11 14:35:00] celery@DESKTOP-XXX ready.
```

> **⚠️ Windows Note:** The `-P solo` flag is **required** on Windows. Celery's default `prefork` pool uses `os.fork()` which is not supported on Windows. The `solo` pool runs tasks in a single-threaded mode that is fully compatible.

---

## 9. Frontend Setup

### 9.1. Option A: HTTP Server (Recommended)

Open a **new terminal window**:
```bash
cd frontend
python -m http.server 8080
```

Navigate to: `http://localhost:8080`

### 9.2. Option B: Direct File Open

Simply double-click `frontend/index.html` in your file explorer. Note: Some browsers may block API requests from `file://` origins due to CORS restrictions.

### 9.3. Option C: VS Code Live Server

If using VS Code with the Live Server extension, right-click `index.html` → **"Open with Live Server"** (typically serves on port 5500).

> **CORS Note:** Ensure the URL your frontend is served from (e.g., `http://localhost:8080`) is listed in the `ALLOWED_ORIGINS` environment variable. The default configuration includes common development ports.

---

## 10. Browser Extension Setup

1. Open **Chrome** and navigate to `chrome://extensions/`
2. Enable **"Developer mode"** (toggle in top-right corner)
3. Click **"Load unpacked"**
4. Select the `extension/` directory from the project root
5. The CyberShield EDU Protector icon will appear in your toolbar
6. Click the icon to paste and analyze suspicious text

> **Note:** The extension communicates with `http://localhost:8000` — the backend must be running for the extension to function.

---

## 11. Verification Checklist

After completing all setup steps, verify each component:

| # | Component | Test | Expected Result |
|:---|:---|:---|:---|
| 1 | **MySQL** | Open phpMyAdmin, check `cybershield` DB | 8 tables visible |
| 2 | **Backend** | Visit `http://localhost:8000/docs` | Swagger UI loads |
| 3 | **Redis** | Run `redis-cli ping` | Response: `PONG` |
| 4 | **Celery** | Check Celery terminal | "celery@... ready" |
| 5 | **Frontend** | Visit `http://localhost:8080` | Landing page loads |
| 6 | **Login** | Login with `admin` / `admin123` | Token received, dashboard loads |
| 7 | **Text Scan** | Analyze: "Pay $50 fee immediately" | Prediction: "scam" |
| 8 | **URL Scan** | Analyze: `http://paypa1.com` | Typosquatting detected |
| 9 | **PDF Scan** | Upload any PDF | Task ID returned, result via polling |
| 10 | **Image Scan** | Upload any screenshot | OCR + forensic results returned |
| 11 | **API Docs** | Visit `http://localhost:8000/docs` | All endpoints documented |

---

## 12. Troubleshooting Guide

### 12.1. Common Errors

| Error | Cause | Solution |
|:---|:---|:---|
| `ModuleNotFoundError: No module named 'app'` | Terminal not in `backend/` directory | `cd backend` before running commands |
| `Connection refused: port 3306` | MySQL not running | Start MySQL in XAMPP Control Panel |
| `Connection refused: port 6379` | Redis not running | Start `redis-server.exe` |
| `No module named 'torch'` | PyTorch not installed | `pip install torch` (re-run requirements) |
| `TesseractNotFoundError` | Tesseract not installed | Install from UB-Mannheim link above |
| `CORS error in browser` | Frontend origin not whitelisted | Add your frontend URL to `ALLOWED_ORIGINS` in `.env` |
| `bcrypt error` | bcrypt C extension issue on Windows | Already mitigated — system uses PBKDF2-SHA256 as primary |
| `celery: command not found` | Virtual env not activated | Run `venv\Scripts\activate` first |
| `FileNotFoundError: .env` | Missing .env file | Create `.env` in project root per section 5 |
| `OperationalError: Access denied for user 'root'` | MySQL has a password set | Update `DATABASE_URL` in `.env` with password |
| `OSError: [WinError 10048] port already in use` | Another process on port 8000 | Kill the process or change port in `main.py` |

### 12.2. Performance Issues

- **Slow first request:** This is normal — the AI model loads on first inference if not pre-loaded. Subsequent requests are fast (~200-500ms).
- **High memory usage (~2-3GB):** Expected when PyTorch + DistilBERT + OpenCV are loaded. Close other applications if RAM is constrained.
- **PDF scan timeout:** Ensure Redis and Celery worker are running. PDF scans are background tasks that require the full Celery stack.

### 12.3. Resetting the Database

If you need to reset all data and start fresh:
1. In phpMyAdmin, drop the `cybershield` database
2. Re-create it and re-import `backend/setup_xampp.sql`
3. Restart the backend server

### 12.4. Refreshing Educational Content

To reload educational resources from the JSON data file:
```bash
cd backend
python fix_awareness_db.py
```

---

*For questions or issues, refer to the [CONTRIBUTING.md](../CONTRIBUTING.md) guide or the [architecture documentation](./architecture.md).*
