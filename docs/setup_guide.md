# CyberShield-EDU: Complete Deployment Guide

Follow these steps to set up the full CyberShield-EDU platform on a new Windows machine.

## 1. Prerequisites
Ensure the following are installed:
- **Python 3.10 or higher**: [Download here](https://www.python.org/downloads/)
- **XAMPP**: For MySQL database. [Download here](https://www.apachefriends.org/index.html)
- **Redis for Windows**: Essential for background tasks. [Download here](https://github.com/tporadowski/redis/releases)
- **Git** (Optional): For cloning the repository.
- **Tesseract OCR**: Required for the Image Scanner module. [Download here](https://github.com/UB-Mannheim/tesseract/wiki).

---

## 2. Database Setup (XAMPP)
1.  Open the **XAMPP Control Panel**.
2.  Start **MySQL**.
3.  Click the **Admin** button next to MySQL to open phpMyAdmin.
4.  Create a new database named `cybershield`.
5.  Import the SQL file located at: `backend/setup_xampp.sql`.
    - *This script automatically creates all tables and seeds the database with initial educational modules, quiz questions, and verified partners.*
    - *Alternatively, run the SQL script via the terminal in the MySQL bin folder.*

---

## 3. Backend Setup
1.  Open a terminal in the `backend` folder.
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    ```
3.  **Activate the Environment**:
    ```bash
    venv\Scripts\activate
    ```
4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configure Environment Variables**:
    Create a file named `.env` in the `backend` folder with the following content:
    ```env
    DEBUG=True
    APP_NAME="CyberShield EDU"
    SECRET_KEY="cyeber-shield-dev-secret-!@#"
    DATABASE_URL=mysql+mysqlconnector://root@localhost/cybershield
    REDIS_URL=redis://localhost:6379/0
    URLSCAN_API_KEY="your-api-key-here"
    ```
6.  **Download AI Models**:
    Upon first run, the system will automatically download the `distilbert-base-multilingual-cased` model (~250MB). Ensure you have a stable internet connection.
7.  **Run the Server**:
    ```bash
    python main.py
    ```
    *The API will be available at `http://localhost:8000`.*

8.  **Seed/Refresh Content (Optional)**:
    If you need to manually refresh the educational content from `data/educational_resources.json`, run:
    ```bash
    python fix_awareness_db.py
    ```

---

## 4. Background Workers (Celery)
1.  Ensure **Redis** is running (Start `redis-server.exe`).
2.  Open a **new** terminal in the `backend` folder.
3.  **Activate the Environment**:
    ```bash
    venv\Scripts\activate
    ```
4.  **Start the Worker**:
    ```bash
    celery -A app.tasks worker --loglevel=info -P solo
    ```
    *Note: The `-P solo` flag is required for stability on Windows.*

---

## 5. Frontend Setup
The project primarily uses the premium Vanilla implementation.
1.  **Option A (Direct)**: Simply open `frontend/index.html` in any modern browser.
2.  **Option B (Served)**: In a new terminal in the `frontend` folder, run:
    ```bash
    python -m http.server 8080
    ```
    *Then navigate to `http://localhost:8080`.*

---

## 6. Verification
- **Audio Scan**: Visit `audio-scan.html` and upload a mock .wav file to trigger the vishing analysis.
- **Developer API**: Use Postman to send a request to `http://localhost:8000/api/v1/public/detect/text` with an `X-API-Key` header.
