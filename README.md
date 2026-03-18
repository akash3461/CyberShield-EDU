# CyberShield-EDU 🛡️

**An advanced, AI-powered cybersecurity protection platform designed specifically to help students detect and avoid online scams, phishing links, and fraudulent documents.**

![CyberShield Overview](https://img.shields.io/badge/Status-Active-brightgreen)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![ML](https://img.shields.io/badge/AI-Multilingual--NLP-FF9900)
![API](https://img.shields.io/badge/Developer--API-v1.0-blueviolet)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## 📌 Executive Summary

Students globally are frequently targeted by sophisticated cyber scams involving fake internships, fraudulent scholarships, housing deposit theft, and phishing links. **CyberShield-EDU** provides a comprehensive, unified, and easy-to-use digital safety dashboard powered by Machine Learning and heuristic analysis. By proactively analyzing suspicious content at the source, CyberShield-EDU aims to elevate digital literacy and prevent financial and data loss among student populations.

## ✨ Core Capabilities & Features

Our platform employs a multi-layered approach to threat detection, ensuring users are protected across various digital communication channels:

### 1. 🌍 Multilingual & Context-Aware NLP
Analyzes SMS, WhatsApp messages, or emails using an advanced **Multilingual DistilBERT** model. 
- **Language Detection:** Scans threats in Hindi, Spanish, English, and more.
- **Context Engine:** Detects "Social Engineering" (e.g., a "Professor" asking for an OTP).
- **Sentiment Analysis:** Flags artificial urgency and psychological pressure.

### 2. 🎙️ Audio Vishing Detector
Protection against "Voice Phishing" (Vishing).
- Transcribes audio recordings or voice notes.
- Analyzes voice patterns for high-risk financial or arrest threats.

- Extracts text, metadata, and embedded artifacts.
- Scans for known fraudulent signatures and malicious patterns.

### 4. 🔗 URL Phishing Scanner
Proactively checks raw URLs for malicious intent:
- **Typosquatting Check:** Detects impersonated brands (e.g., `paypa1.com`).
- **Domain Analysis:** Flags suspicious TLDs and entropy levels.

### 5. 📸 Image OCR Scanner
Scans screenshots of DMs or Instagram/WhatsApp chats.
- Uses **Optical Character Recognition** to extract text from images.
- Feeds extracted data directly into the Multilingual AI engine.

### 6. 🎓 Education & Awareness Hub
Prevention is better than cure. The platform includes an interactive learning center:
- **Knowledge Modules**: Multi-path educational guides on specific threats.
- **"Spot the Scam" Quizzes**: Interactive learning modules.
- **Progress Tracking**: Earn **+30 XP** for each completed module.

### 7. ⚙️ User Settings & Gamification
Personalized experience with persistent progress.
- **Profile Management**: View your role, email, and security stats.
- **XP & Leveling System**: Track your security mastery through scans and learning.
- **Theme Engine**: Seamless toggle between premium Light and Dark modes.

### 8. 🔌 Developer API
Open infrastructure for the student ecosystem.
- **X-API-Key**: Secure access for job boards and campus platforms.
- **Developer Mode**: Toggle API access and documentation directly from your settings.

### 9. 📊 Admin & Analytics Dashboard
For university IT administrators and researchers:
- Real-time threat analytics and scan statistics.
- Interactive charts and dynamic threat-signature management.
- **User Management**: Monitor user progress and engagement.

---

## 🏗️ System Architecture

CyberShield-EDU is engineered with a modern, decoupled frontend-backend architecture to ensure scalability, responsiveness, and clean separation of concerns.

- **Frontend Configuration:** The primary client interface is a premium Vanilla HTML/JS/CSS implementation located in `frontend`. It features a sleek, Glassmorphism-inspired UI with full responsive support and a multi-theme system. It communicates securely with the backend via RESTful APIs.
- **Backend Configuration:** A high-performance Python server built on the FastAPI framework. It handles asynchronous requests, orchestrates machine learning inference using Hugging Face Transformers, validates schemas with Pydantic, and generates automated OpenAPI documentation.

For a deep dive, see the [Architecture Overview](./docs/architecture.md).

---

## 🚀 Quick Start Guide

Follow these steps to get a local instance of CyberShield-EDU running on your machine.

### 1. Prerequisites
Ensure you have the following installed on your system:
- **Python 3.10+** (Required for the FastAPI backend and AI models)
- **XAMPP / MySQL**: For persistent data storage.
- **Redis**: Essential for background task orchestration.
- **Tesseract OCR engine**: Crucial for the Image Scanner module.

### 2. Setup the Backend Environment
1.  **Database**: Start MySQL in XAMPP and import `backend/setup_xampp.sql`.
2.  **Environment**: Create and activate a virtual environment in the `backend` folder.
3.  **Install**: `pip install -r requirements.txt`.
4.  **Configure**: Create a `.env` file (see `docs/setup_guide.md` for template).
5.  **Run**: `python main.py` (Server starts on port 8000).

### 3. Setup the Frontend Environment
The frontend is integrated and served via the internal server, or can be served independently:
```bash
# To serve independently:
cd frontend
python -m http.server 8081
```
*Access the platform at `http://localhost:8081`.*

---

## � Project Structure

```text
CyberShield-EDU/
├── backend/                  # FastAPI Python Server & ML Logic
│   ├── app/                  # Main application code (routes, models, utils)
│   ├── venv/                 # Local Python environment
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Premium Vanilla JS Implementation
├── docs/                     # Comprehensive Project Documentation
├── data/                     # Static JSON datasets (e.g., educational info)
└── README.md                 # Project Overview (You are here)
```

---

## 🛠️ Technology Stack

CyberShield-EDU leverages industry-standard open-source technologies:

### Client-Side (Frontend)
- **Primary:** Vanilla JavaScript, HTML5, CSS3, Google Fonts.

### Server-Side (Backend)
- **Framework:** Python 3, FastAPI, Pydantic, Uvicorn, Celery.
- **AI & Data Processing Engine:**
  - `distilbert-base-multilingual-cased` (NLP Inference)
  - `SpeechRecognition` / `pydub` (Audio Analysis)
  - `pytesseract` (OCR Engine)
  - `SQLAlchemy` & `MySQL` (Permanent Data Storage)
  - `Redis` (Task Queue & Caching)

---

## 📚 Detailed Documentation

Expand your knowledge regarding the platform's inner workings by exploring the `/docs` directory:

- 📖 **[Setup & Installation Guide](./docs/setup_guide.md)**: Deep dive into environment variables and troubleshooting.
- 🏗️ **[Architecture Overview](./docs/architecture.md)**: Explore the Mermaid diagrams and system design principles.
- 🔌 **[API Documentation](./docs/api_documentation.md)**: A complete reference for the RESTful endpoints available.

---

## 📄 License & Disclaimer

This software is distributed under the [MIT License](LICENSE).

**Disclaimer:** *CyberShield-EDU is developed purely for educational purposes to enhance cybersecurity awareness among student populations. It does not replace professional anti-virus or endpoint protection software. The creators assume no liability for any reliance on this tool.*
