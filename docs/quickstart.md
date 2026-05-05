# CyberShield-EDU: Quick Start Guide 🚀

> Get the full CyberShield-EDU platform running in under 10 minutes on any Windows machine. This condensed guide covers the essential steps — for detailed explanations and troubleshooting, refer to the full [Setup Guide](./setup_guide.md).

---

## Prerequisites

| Requirement | Download |
|:---|:---|
| Python 3.10+ | [python.org/downloads](https://www.python.org/downloads/) |
| XAMPP (MySQL) | [apachefriends.org](https://www.apachefriends.org/) |
| Redis for Windows | [github.com/tporadowski/redis/releases](https://github.com/tporadowski/redis/releases) |
| Tesseract OCR | [github.com/UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) |

---

## Step 1: Database Setup

1. Open **XAMPP Control Panel** → Start **MySQL**
2. Open [phpMyAdmin](http://localhost/phpmyadmin)
3. Create a new database named **`cybershield`** (collation: `utf8mb4_general_ci`)
4. Go to **Import** tab → upload `backend/setup_xampp.sql` → click **Go**
5. Verify: You should see 8 tables created with seed data

---

## Step 2: Backend Setup

Open a terminal in the `backend/` folder:

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install all dependencies (~30 packages)
pip install -r requirements.txt

# Start the backend server
python main.py
```

**Wait for:** `🚀 Pre-loading AI models...` → `Uvicorn running on http://0.0.0.0:8000`

> **First Run Note:** The AI model (~250MB) downloads automatically on first startup. This requires internet access and may take 2-10 minutes.

---

## Step 3: Background Workers (Required for PDF + Image scans)

### Terminal 2 — Redis:
```bash
redis-server
```

### Terminal 3 — Celery Worker:
```bash
cd backend
venv\Scripts\activate
celery -A app.tasks worker --loglevel=info -P solo
```

**Wait for:** `celery@... ready.`

---

## Step 4: Frontend Launch

### Terminal 4 — Web Server:
```bash
cd frontend
python -m http.server 8080
```

Navigate to: **http://localhost:8080**

---

## Step 5: Verify Everything Works

| Check | Action | Expected |
|:---|:---|:---|
| ✅ Backend | Visit `http://localhost:8000/docs` | Swagger UI loads |
| ✅ Frontend | Visit `http://localhost:8080` | Landing page loads |
| ✅ Login | `admin` / `admin123` | Dashboard loads with user profile |
| ✅ Text Scan | Analyze: *"Pay ₹500 registration fee immediately"* | Detected as **SCAM** |
| ✅ URL Scan | Analyze: `http://paypa1.com` | **Typosquatting** detected |
| ✅ Redis | Run `redis-cli ping` | Response: **PONG** |
| ✅ PDF Scan | Upload any PDF | Task ID assigned, results via polling |

---

## Environment Configuration

The `.env` file in the project root should contain:

```env
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500
SECRET_KEY="cyeber-shield-dev-secret-!@#"
DATABASE_URL=mysql+pymysql://root@127.0.0.1/cybershield
REDIS_URL=redis://localhost:6379/0
URLSCAN_API_KEY=""
```

---

## Component Summary

| Terminal | Service | Port | Purpose |
|:---|:---|:---|:---|
| Terminal 1 | `python main.py` | 8000 | FastAPI Backend + AI Models |
| Terminal 2 | `redis-server` | 6379 | Message Broker |
| Terminal 3 | `celery -A app.tasks worker` | — | Background PDF/Image Tasks |
| Terminal 4 | `python -m http.server 8080` | 8080 | Frontend Web Server |

---

## Common Fixes

| Problem | Solution |
|:---|:---|
| `Connection refused: 3306` | Start MySQL in XAMPP Control Panel |
| `Connection refused: 6379` | Start `redis-server` |
| `ModuleNotFoundError` | Activate venv: `venv\Scripts\activate` |
| CORS error in browser | Add your URL to `ALLOWED_ORIGINS` in `.env` |
| PDF scan hangs forever | Ensure both Redis AND Celery are running |

---

**Done! 🎉** Login with `admin` / `admin123` or register a new student account to begin your cyber-security journey.

For detailed documentation, see:
- [Full Setup Guide](./setup_guide.md) — Comprehensive installation instructions
- [User Manual](./user_manual.md) — Complete feature guide
- [API Documentation](./api_documentation.md) — Endpoint reference
- [Architecture](./architecture.md) — Technical deep-dive
