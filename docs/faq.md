# Frequently Asked Questions (FAQ) — CyberShield-EDU

> Answers to common questions about the CyberShield-EDU platform, covering technical details, usage guidance, security considerations, and academic context. Organized by audience: General, Student Users, Technical/Developer, and Academic/Evaluator.

---

## Table of Contents

1. [General Questions](#general-questions)
2. [Student User Questions](#student-user-questions)
3. [Technical / Developer Questions](#technical--developer-questions)
4. [Academic / Evaluator Questions](#academic--evaluator-questions)

---

## General Questions

### Q: What is CyberShield-EDU?
**A:** CyberShield-EDU is an AI-powered cybersecurity awareness platform designed specifically for university students. It combines multi-vector threat detection (text, URL, PDF, image analysis) with gamified education to help students identify and understand digital threats like phishing, fake internships, scholarship fraud, and AI-generated scams.

---

### Q: Is CyberShield-EDU free to use?
**A:** Yes. CyberShield-EDU is released under the **MIT License**, making it completely free for academic, personal, and commercial use. There are no subscription fees, no premium tiers, and no data monetization.

---

### Q: What languages does it support?
**A:** The AI detection engine uses `distilbert-base-multilingual-cased`, which supports **104 languages** including English, Hindi, Spanish, Arabic, Mandarin, French, German, Portuguese, Russian, Japanese, Korean, and many more. No configuration change is needed — the model automatically processes text in any supported language.

---

### Q: Does it work offline?
**A:** Mostly yes. After the first run (which downloads the AI model), the core detection engines work completely offline:
- ✅ Text detection (AI + patterns + context) — fully offline
- ✅ URL heuristic analysis (9 layers) — fully offline
- ✅ PDF forensics — fully offline
- ✅ Image OCR + texture analysis — fully offline
- ⚠️ URL deep scan (webpage fetching) — requires internet
- ⚠️ URLScan.io threat intelligence — requires internet + API key

---

### Q: What operating systems does it support?
**A:** CyberShield-EDU is developed and tested on **Windows 10/11**. The backend (Python/FastAPI) is cross-platform and should work on macOS and Linux with minor adjustments:
- Replace XAMPP with native MySQL
- Use standard Redis packages
- Celery's `-P solo` flag (Windows-specific) can be removed on Linux

---

### Q: Is my data safe?
**A:** Yes. Your data is processed and stored locally on the machine running the platform. No data is sent to external servers except:
1. **URLScan.io** (only if configured with an API key, and only for URL reputation lookups)
2. **Hugging Face** (only for initial model download on first run)

Passwords are hashed with PBKDF2-SHA256 (irreversible). API keys are stored as SHA-256 hashes.

---

## Student User Questions

### Q: Do I need to create an account?
**A:** No, you can use the detection features in **guest mode** without creating an account. However, creating an account provides:
- 📊 Scan history — review your past analyses
- ⚡ XP and leveling — earn Experience Points for every scan
- 🏆 Badges — unlock achievement badges
- 🎓 Academy progress — track your security learning journey

---

### Q: How much XP do I earn per activity?
| Activity | XP Earned |
|:---|:---|
| Text scan | +10 XP |
| URL scan | +15 XP |
| Quiz completion | +50 XP |
| Educational module | Up to +150 XP |
| Phishing simulation | Up to +150 XP |

Your level is calculated as: **Level = (Total XP ÷ 100) + 1**

---

### Q: What do the rank titles mean?
| Level Range | Rank | Meaning |
|:---|:---|:---|
| 1-2 | **Cyber Scout** | Beginning your security awareness journey |
| 3-5 | **Forensic Guardian** | Actively scanning and learning |
| 6-10 | **Cyber Sentinel** | Experienced threat identifier |
| 11+ | **Grand Protector** | Master-level cyber awareness |

---

### Q: Can I scan a WhatsApp message?
**A:** Yes! Two methods:
1. **Text Scan:** Copy the message text and paste it into the Text Scan tab
2. **Image Scan:** Take a screenshot of the WhatsApp conversation and upload it to the Image Scan tab — the OCR engine will extract the text and analyze it

Method 2 also performs forensic analysis (texture analysis, metadata check, platform detection) in addition to text analysis.

---

### Q: What should I do if something is flagged as a scam?
**A:**
1. **Do not click any links** in the message/document
2. **Do not share personal information** (OTP, password, bank details)
3. **Do not send any money** (registration fees, processing charges)
4. **Block the sender** on the platform where you received the message
5. **Report it** using CyberShield-EDU's reporting feature
6. **Inform your university's IT security team** if it targets campus systems
7. **File a complaint** at [cybercrime.gov.in](https://cybercrime.gov.in) (India) or your local cybercrime portal

---

### Q: Why was my scan marked "safe" even though it looks suspicious?
**A:** No detection system is 100% perfect. A "safe" verdict with low confidence (40-50%) indicates borderline content. Possible reasons:
- The message uses novel language not yet in the pattern database
- The URL is too new for reputation databases
- The scam technique is sophisticated enough to evade current heuristics

**Always trust your instincts.** If something seems too good to be true, it probably is — regardless of what any tool says.

---

### Q: Can I undo or delete my scan history?
**A:** Currently, scan history cannot be individually deleted through the UI. Deleting your account removes all associated scan records (CASCADE delete). For data privacy requests, contact the platform administrator.

---

## Technical / Developer Questions

### Q: What AI model does CyberShield-EDU use?
**A:** The platform uses **`distilbert-base-multilingual-cased`** — a knowledge-distilled version of Google's BERT model from Hugging Face. Key specifications:
- 66 million parameters (60% fewer than BERT)
- 104 languages supported
- 97% accuracy retention compared to full BERT
- ~250MB model size
- 200-500ms inference latency on CPU

The system first checks for a fine-tuned model at `backend/app/ai_models/scam_detector_v1/` and falls back to the base multilingual model.

---

### Q: Why FastAPI instead of Django or Flask?
**A:**
1. **Native async support** — Critical for concurrent URL fetching, external API calls, and database queries
2. **Automatic OpenAPI documentation** — Swagger UI generated from type hints with zero configuration
3. **Pydantic validation** — Request/response schema validation at the API boundary
4. **Performance** — One of the fastest Python web frameworks, comparable to Node.js/Go
5. **Dependency injection** — Clean composition of auth guards, database sessions, and rate limiters

---

### Q: Why Vanilla JavaScript instead of React/Vue/Angular?
**A:** This was a conscious design decision for several reasons:
1. **Zero build step** — The frontend works by opening HTML files directly. No `npm install`, no webpack, no build process
2. **Smaller bundle** — No framework overhead means faster loading on slower connections
3. **Accessibility** — Students without framework experience can read and modify the code
4. **Deployment simplicity** — Any static file server works. No Node.js server required
5. **Educational value** — Demonstrates strong vanilla JS competence for academic evaluation

---

### Q: How does the background task system work?
**A:** CyberShield-EDU uses **Celery with Redis** for asynchronous processing:
1. **FastAPI** receives a file upload (PDF or image)
2. A **Celery task** is dispatched to the Redis message broker
3. The API immediately returns a `task_id` to the client
4. A **Celery worker** picks up the task from Redis and processes it
5. The worker stores the result back in Redis
6. The **frontend polls** `GET /tasks/status/{task_id}` every 2 seconds
7. When `status: "SUCCESS"`, the result is returned and rendered

This prevents the API from blocking during long-running analysis (PDF scanning can take 10-30 seconds with recursive URL analysis).

---

### Q: Can I add new detection patterns without modifying code?
**A:** Yes! CyberShield-EDU's Pattern Engine is **database-driven**:
1. Log in as admin (`admin` / `admin123`)
2. Navigate to the Admin Dashboard
3. Add a new keyword or pattern with its risk score
4. The change takes effect **immediately** — no restart needed

The Pattern Engine's in-memory cache is automatically invalidated and reloaded when admin operations modify patterns.

---

### Q: How do I integrate CyberShield-EDU into my own application?
**A:**
1. Navigate to the Developer Portal
2. Generate an API key
3. Include the key in your requests:
```bash
curl -X POST http://localhost:8000/api/v1/public/detect/text \
  -H "X-API-Key: cs_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"text": "Suspicious message to check"}'
```
4. Each key has a daily limit of 1,000 requests
5. Use `X-Sandbox: true` header for testing without consuming quota

---

### Q: Why is Tesseract OCR required? Can I use a different OCR engine?
**A:** Tesseract is the industry-standard open-source OCR engine with 100+ language support. CyberShield-EDU uses it via the `pytesseract` Python wrapper. The image service includes **self-healing path detection** that automatically finds Tesseract at common Windows installation paths.

Replacing Tesseract would require modifying `image_ocr.py` to use an alternative OCR library (e.g., EasyOCR, PaddleOCR). The OCR output is just a text string, so the rest of the pipeline would work unchanged.

---

### Q: What happens if the AI model gives a wrong prediction?
**A:** CyberShield-EDU is designed with **defense in depth** — the AI model is just one of multiple detection layers:

1. **AI Model** (DistilBERT) — Base classification
2. **Pattern Engine** — Keyword and regex matching (independent of AI)
3. **Context Analysis** — Social engineering role-action conflicts (independent of AI)
4. **Trust Service** — Brand impersonation detection (independent of AI)
5. **Heuristic Layers** (URLs) — 9 independent checks (completely independent of AI)

Even if the AI model is fooled by adversarial input, the other layers can still catch the threat. This multi-layered approach significantly reduces both false positives and false negatives.

---

## Academic / Evaluator Questions

### Q: What makes this project technically sophisticated?
**A:** CyberShield-EDU demonstrates several advanced computer science concepts:

| Concept | Implementation |
|:---|:---|
| **NLP / Transfer Learning** | Fine-tunable multilingual transformer model (DistilBERT) |
| **Computer Vision** | OpenCV Laplacian Variance for AI-generated image detection |
| **Information Theory** | Shannon entropy for DGA domain classification |
| **String Algorithms** | Levenshtein distance for typosquatting detection |
| **Async Programming** | Python async/await with `asyncio.gather` for parallel URL scanning |
| **Message Queues** | Celery/Redis for distributed background task processing |
| **Security Engineering** | JWT auth, PBKDF2 hashing, RBAC, rate limiting, CORS |
| **ORM / Database Design** | SQLAlchemy models with foreign keys, indexes, and JSON columns |
| **Cross-Service Orchestration** | PDF → URL → Text recursive analysis pipeline |
| **Design Patterns** | Singleton (models), Dependency Injection (FastAPI), Strategy (pattern types) |

---

### Q: How does this compare to commercial solutions?
| Feature | CyberShield-EDU | PhishTank | VirusTotal | Google Safe Browsing |
|:---|:---|:---|:---|:---|
| Text NLP Analysis | ✅ 104 languages | ❌ | ❌ | ❌ |
| URL Phishing | ✅ 9 layers + deep scan | ✅ Community DB | ✅ 70+ engines | ✅ Blacklist |
| PDF Forensics | ✅ Ghost links + metadata | ❌ | ✅ File scanning | ❌ |
| Image Forensics | ✅ EXIF + texture + OCR | ❌ | ❌ | ❌ |
| AI Generation Detection | ✅ Laplacian + EXIF | ❌ | ❌ | ❌ |
| Company Impersonation | ✅ Brand-domain matching | ❌ | ❌ | ❌ |
| Context Conflict (SE) | ✅ Role-action matrix | ❌ | ❌ | ❌ |
| Educational Component | ✅ Full academy + gamification | ❌ | ❌ | ❌ |
| Cost | Free (MIT) | Free | Freemium | Free (limited) |
| Student-Focused | ✅ | ❌ | ❌ | ❌ |

---

### Q: What are the known limitations?
**A:**
1. **AI accuracy depends on training data** — The base model may not catch highly novel or sophisticated scam language
2. **No real-time email integration** — Students must manually copy/paste or screenshot content for analysis
3. **Single-machine deployment** — Currently designed for localhost/academic environments, not multi-tenant cloud
4. **Tesseract dependency** — Image OCR requires a separate Tesseract installation
5. **No audio analysis** — Voice phishing (vishing) detection is planned but not yet implemented
6. **JWT stateless limitation** — Tokens cannot be invalidated before expiry (no logout blacklist)
7. **LLM Explainer paused** — The AI-powered explanation feature is coded but deactivated due to resource requirements

---

### Q: What is the total codebase size?
| Component | Metric |
|:---|:---|
| Backend Python | ~2,500 lines across 25+ modules |
| Frontend JavaScript | ~77,000 bytes across 4 modules |
| Frontend CSS | ~33,000 bytes across 2 stylesheets |
| HTML Pages | 19 distinct pages |
| Database Schema | 9 tables, 142 lines of SQL |
| Test Suite | 3 async test cases |
| Documentation | 15 comprehensive markdown files |
| Dependencies | 30+ Python packages |

---

### Q: Is this project suitable for publication/extension?
**A:** Yes. Several aspects are novel enough for academic publication:
1. **Ghost link detection in PDFs** — Extracting hidden annotation URIs is not commonly implemented in student-facing tools
2. **Context conflict matrix** — The role-action social engineering detection is a novel heuristic approach
3. **Laplacian variance for AI image detection** — Applying forensic texture analysis in an educational context
4. **Gamified security education** — Combining detection with persistent learning incentives
5. **Cross-service orchestration** — The recursive PDF → URL → Text pipeline demonstrates sophisticated service composition

Potential publication venues: IEEE Education Technology, ACM SIGCSE, Journal of Cybersecurity Education, USENIX Security Symposium (education track).

---

### Q: Can this be deployed at a real university?
**A:** Yes, with the production hardening steps outlined in the [Security Whitepaper](./security_whitepaper.md#11-security-recommendations-for-production):
1. Generate a cryptographically random `SECRET_KEY`
2. Enable HTTPS via Nginx reverse proxy
3. Change default admin password
4. Set MySQL root password
5. Disable Swagger UI
6. Add SSRF protection for URL deep scan
7. Configure Redis authentication

The architecture is designed for institutional deployment — the database-driven pattern engine allows campus IT teams to customize detection rules for their specific threat landscape without code changes.

---

*Didn't find your question? Refer to the [User Manual](./user_manual.md), [Setup Guide](./setup_guide.md), or [Architecture](./architecture.md) documentation for deeper technical details.*
