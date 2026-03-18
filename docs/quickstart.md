# CyberShield-EDU: 5-Minute Quickstart 🚀

Get the platform running on any Windows laptop with these few steps.

## 1. Turbo Database Setup
1.  Start **XAMPP Control Panel** and run **MySQL**.
2.  Go to [http://localhost/phpmyadmin](http://localhost/phpmyadmin).
3.  Create a new DB named `cybershield`.
4.  Import `backend/setup_xampp.sql`.

## 2. Backend in 3 Commands
Open terminal in `backend/` folder:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 3. Background Processing
Start **Redis Server**. Open a **new** terminal in `backend/` and run:
```bash
venv\Scripts\activate
celery -A app.tasks worker --loglevel=info -P solo
```

## 4. Launch Frontend
1.  Go to the `frontend/` folder.
2.  Double-click `index.html` (or run `python -m http.server 8080`).

---
**Done!** Login with `admin` / `admin123` or register a new student account.
