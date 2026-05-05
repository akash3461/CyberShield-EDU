# Glossary — CyberShield-EDU

> A comprehensive glossary of technical terms, cybersecurity concepts, detection methodologies, and acronyms used throughout the CyberShield-EDU platform and its documentation. Designed for non-technical readers, professors, and students encountering these concepts for the first time.

---

## A

### Adversarial Input
Specially crafted input designed to fool an AI model into making incorrect predictions. For example, a scam message rephrased to avoid keyword detection while maintaining its malicious intent.

### AI (Artificial Intelligence)
The simulation of human intelligence in machines. In CyberShield-EDU, AI refers specifically to the DistilBERT machine learning model used for text classification.

### Annotation (PDF)
A metadata object embedded within a PDF document that can contain hyperlinks, form fields, or interactive elements. Annotations can carry URI targets that are invisible in the document's visible text — these are called "ghost links" in CyberShield-EDU.

### API (Application Programming Interface)
A set of defined rules and protocols for building and interacting with software applications. CyberShield-EDU's RESTful API allows the frontend and external applications to communicate with the detection engines.

### API Key
A unique authentication token used to identify and authorize external applications accessing the CyberShield-EDU Public API. API keys are hashed with SHA-256 before storage.

### ASGI (Asynchronous Server Gateway Interface)
A standard interface between async-capable Python web servers and applications. Uvicorn is the ASGI server that runs the CyberShield-EDU FastAPI backend.

### Async/Await
A programming paradigm for non-blocking I/O operations. CyberShield-EDU uses async functions for URL fetching, external API calls, and database queries to handle multiple requests concurrently.

---

## B

### Badge
A digital achievement award earned by reaching specific milestones in CyberShield-EDU. Examples: "First Response" (first scan), "Phishing Hunter" (10 URL scans).

### BERT (Bidirectional Encoder Representations from Transformers)
A groundbreaking NLP model developed by Google that understands context by processing text bidirectionally. CyberShield-EDU uses DistilBERT, a lighter variant.

### Broker (Message Broker)
A software intermediary that translates messages between systems. Redis serves as the message broker between FastAPI and Celery workers in CyberShield-EDU.

---

## C

### Celery
A distributed task queue system for Python. CyberShield-EDU uses Celery to run PDF and Image analysis tasks in the background, preventing the API from blocking during long-running operations.

### Context Conflict
A social engineering detection technique unique to CyberShield-EDU. It identifies when a claimed authority role (e.g., "Professor") is paired with a suspicious action request (e.g., "share your OTP") — a combination that would never occur in legitimate communication.

### Confidence Score
A numerical value (0.0 to 1.0) indicating how certain the detection engine is about its prediction. Higher values indicate stronger certainty. A confidence of 0.95 means the engine is 95% certain of its verdict.

### CORS (Cross-Origin Resource Sharing)
A security mechanism that restricts web pages from making requests to a different domain than the one serving the page. CyberShield-EDU explicitly whitelists allowed frontend origins.

### CRUD
Create, Read, Update, Delete — the four basic operations for managing data. The admin dashboard provides CRUD operations for keywords and threat patterns.

---

## D

### Deep Scan
An advanced URL analysis technique where CyberShield-EDU actually fetches the target webpage, extracts its textual content using BeautifulSoup, and runs AI classification on the extracted text to detect scam content on the page itself.

### DGA (Domain Generation Algorithm)
A technique used by malware to automatically generate random-looking domain names for command-and-control servers. CyberShield-EDU detects DGA domains using Shannon entropy analysis — high-entropy domains like `kj38xnq9p2m4z.xyz` are flagged.

### Dependency Injection
A design pattern where a function receives its dependencies (like database sessions or authentication tokens) as parameters rather than creating them internally. FastAPI uses this pattern extensively via the `Depends()` mechanism.

### DistilBERT
A distilled (compressed) version of BERT that retains 97% of BERT's language understanding capabilities while being 60% smaller and 60% faster. CyberShield-EDU uses `distilbert-base-multilingual-cased` which supports 104 languages.

---

## E

### Entropy (Shannon Entropy)
A mathematical measure of randomness or unpredictability in a sequence of characters. Formula: `H(X) = -Σ p(xi) × log₂(p(xi))`. In CyberShield-EDU, domains with entropy > 4.0 are flagged as potentially machine-generated (DGA).

### EXIF (Exchangeable Image File Format)
Metadata embedded in image files by cameras and software. EXIF data can reveal the camera model, software used to create/edit the image, GPS coordinates, and timestamps. CyberShield-EDU inspects EXIF tag 305 (Software) for AI generation tool signatures.

---

## F

### FastAPI
A modern, high-performance Python web framework for building APIs. It supports async/await, automatic OpenAPI documentation, and Pydantic-based request validation. FastAPI is the backbone of CyberShield-EDU's backend.

### False Positive
When the detection system incorrectly flags legitimate content as a scam. Minimizing false positives is critical — incorrectly blocking a real scholarship notification would harm student trust.

### False Negative
When the detection system fails to flag actual scam content as malicious. CyberShield-EDU's multi-layered approach reduces false negatives by combining AI with heuristic rules.

---

## G

### Gamification
The application of game-design elements (points, levels, badges, leaderboards) to non-game contexts. CyberShield-EDU uses gamification to incentivize students to actively engage with security scanning and education.

### GeoIP
The process of mapping an IP address to a geographic location. CyberShield-EDU's URL scanner uses GeoIP to identify the hosting country of suspicious domains.

### Ghost Link
A URL embedded in a PDF document's annotation layer that is NOT visible in the rendered text. Users cannot see the link but clicking on an interactive element (button, image) may activate it. CyberShield-EDU's PDF analyzer specifically extracts and flags these hidden URLs.

### Glassmorphism
A UI design trend characterized by frosted-glass-effect backgrounds achieved through `backdrop-filter: blur()`, semi-transparent `rgba()` colors, and subtle border effects. CyberShield-EDU's frontend uses this aesthetic extensively.

---

## H

### Homoglyph
A character that looks visually identical or very similar to another character but has a different Unicode code point. For example, Cyrillic `а` (U+0430) looks identical to Latin `a` (U+0061). Attackers use homoglyphs to create URLs like `pаypal.com` (with a Cyrillic `а`) that appear identical to `paypal.com` in a browser.

### Heuristic
A rule-based approach to problem-solving that uses practical shortcuts and experience-based techniques. CyberShield-EDU's URL scanner uses 9 heuristic layers (protocol check, entropy, typosquatting, etc.) alongside AI classification.

### Hugging Face
An AI company and platform that hosts open-source machine learning models, datasets, and tools. CyberShield-EDU downloads its DistilBERT model from the Hugging Face Model Hub.

---

## I

### Impersonation (Brand Impersonation)
A social engineering technique where scammers pretend to be a well-known company or institution. CyberShield-EDU's Trust Service detects this by comparing brand names mentioned in text against the actual domains of links included in the message.

### Integrity Score (Image)
A composite forensic score (0-100) calculated from three weighted components: metadata trust (40%), texture analysis (40%), and AI signature detection (20%). Lower scores indicate higher likelihood of image manipulation or AI generation.

---

## J

### JWT (JSON Web Token)
A compact, URL-safe token format used for securely transmitting information between parties. CyberShield-EDU uses JWTs for stateless authentication — the token contains the username, role, and user ID, signed with the HS256 algorithm.

---

## L

### Laplacian Variance
A computer vision technique that measures the variance of the Laplacian operator (second-order derivative of pixel intensity) across an image. Real photographs exhibit high variance (natural camera noise), while AI-generated images exhibit suspiciously low variance due to synthetic smoothing. CyberShield-EDU uses a threshold of 120.0 to distinguish natural from synthetic textures.

### Levenshtein Distance
A measure of the minimum number of single-character edits (insertions, deletions, substitutions) required to change one word into another. CyberShield-EDU uses this to detect typosquatting — if a domain is within 2 edits of a popular brand (e.g., "paypa1" → "paypal" = distance 1), it's flagged.

---

## M

### Middleware
Software that sits between the web server and route handlers, processing every request/response. CyberShield-EDU uses middleware for CORS enforcement, request logging, rate limiting, and authentication.

### Multilingual
Supporting multiple languages. CyberShield-EDU's DistilBERT model supports 104 languages simultaneously, enabling scam detection in Hindi, Spanish, Arabic, Mandarin, and virtually any written language.

---

## N

### NLP (Natural Language Processing)
A branch of AI focused on the interaction between computers and human language. CyberShield-EDU uses NLP for text classification (scam vs. safe), sentiment analysis, and keyword extraction.

---

## O

### OCR (Optical Character Recognition)
The conversion of image-based text (in screenshots, photos, scanned documents) into machine-readable text. CyberShield-EDU uses Tesseract OCR to extract text from uploaded images for subsequent NLP analysis.

### ORM (Object-Relational Mapping)
A programming technique that maps database tables to programming language objects. SQLAlchemy is the ORM used by CyberShield-EDU, allowing Python classes (`User`, `ScanRecord`) to represent MySQL tables.

### OWASP (Open Web Application Security Project)
A nonprofit foundation that works to improve web application security. The OWASP Top 10 is a standard awareness document listing the most critical web application security risks. CyberShield-EDU's security whitepaper maps its defenses against all 10 OWASP categories.

---

## P

### Pattern Engine
CyberShield-EDU's Pillar 2 — a database-driven detection system that matches text and URLs against configurable rules. Supports four pattern types: keyword (exact string match), regex (regular expressions), TLD (top-level domain), and domain (full domain blacklist).

### PBKDF2-SHA256
Password-Based Key Derivation Function 2 using SHA-256 hashing. A NIST-recommended algorithm for password hashing that applies thousands of iterations (600,000 by default in passlib) to make brute-force cracking computationally expensive.

### Phishing
A social engineering attack where fraudulent communications (emails, messages, websites) impersonate trustworthy entities to steal sensitive information like passwords, credit card numbers, or personal data.

### Pillar
CyberShield-EDU's organizational framework for features. Each "Pillar" represents a distinct capability area (e.g., Pillar 1: Text Detection, Pillar 4: URL Detection, Pillar 8: Gamification). There are 10 pillars in total.

---

## Q

### QR Code
A two-dimensional barcode that can encode URLs, text, or other data. CyberShield-EDU's image detector scans for QR codes in uploaded images, decodes them, and runs the extracted URL through the URL detection engine.

---

## R

### RBAC (Role-Based Access Control)
A security model that restricts system access based on the roles assigned to users. CyberShield-EDU has two roles: `student` (default) and `admin` (elevated access to analytics and configuration).

### Rate Limiting
A technique for controlling the rate of requests a client can make to an API. CyberShield-EDU limits detection endpoints to 5 requests per minute per IP address using the SlowAPI library.

### Reasoning Trail
A human-readable list of explanations provided by CyberShield-EDU with every scan result, detailing WHY the content was classified as scam or safe. This is the educational core of the platform — teaching users to recognize threat patterns.

### Redirect Chain
The sequence of HTTP redirects a URL goes through before reaching its final destination. Scam URLs often use multiple redirects to obscure the true destination. CyberShield-EDU tracks and displays the complete chain.

### Redis
An in-memory data store used as a message broker and result backend for Celery task queuing. Redis enables CyberShield-EDU's asynchronous PDF and image processing.

---

## S

### Sanitization
The process of cleaning user input to remove potentially malicious content (HTML tags, scripts, control characters) before processing. CyberShield-EDU sanitizes all text and URL inputs using the `Sanitizer` utility class.

### Shannon Entropy
See [Entropy](#entropy-shannon-entropy).

### Shield of Trust
CyberShield-EDU's Pillar 3 — a whitelist-based verification system that confirms whether a URL belongs to a known, verified organization (stored in the `verified_providers` database table). Verified domains receive a visual "Shield of Trust" badge.

### Singleton
A design pattern where only one instance of a class exists throughout the application lifecycle. CyberShield-EDU uses singletons for detection services and AI models, ensuring the 250MB DistilBERT model is loaded only once during startup.

### Social Engineering
Psychological manipulation techniques used to trick individuals into performing actions or divulging confidential information. Common tactics include impersonating authority figures, creating urgency, and offering unexpected rewards.

### SSRF (Server-Side Request Forgery)
An attack where an attacker can induce the server to make HTTP requests to arbitrary domains, potentially accessing internal resources. CyberShield-EDU's URL deep scan feature involves outbound HTTP requests and should be hardened against SSRF in production.

### SQLAlchemy
A Python SQL toolkit and Object-Relational Mapping (ORM) library. CyberShield-EDU uses SQLAlchemy to define database models and execute queries against MySQL.

---

## T

### TLD (Top-Level Domain)
The last segment of a domain name (e.g., `.com`, `.org`, `.xyz`). Certain TLDs like `.xyz`, `.top`, `.pw`, `.zip`, `.click` are statistically associated with higher rates of phishing and malicious activity.

### Token (JWT)
See [JWT](#jwt-json-web-token).

### Transformer
A neural network architecture based on self-attention mechanisms, introduced in the "Attention Is All You Need" paper (2017). BERT and DistilBERT are transformer-based models used by CyberShield-EDU for text understanding.

### Typosquatting
A form of cybersquatting where attackers register domain names that are slight misspellings of popular websites (e.g., `googlr.com`, `paypa1.com`, `microsoftt.com`). CyberShield-EDU detects typosquatting using Levenshtein distance comparison against a watchlist of popular domains.

---

## U

### Uvicorn
A lightning-fast ASGI server implementation in Python. CyberShield-EDU runs on Uvicorn, which handles HTTP request parsing and async event loop management for the FastAPI application.

### URLScan.io
An external threat intelligence service that scans and analyzes URLs for malicious content. CyberShield-EDU optionally integrates with URLScan.io's API to enrich URL analysis with community reputation data.

---

## V

### Vishing (Voice Phishing)
A social engineering attack conducted over phone calls or voice messages. The attacker impersonates a trusted entity (bank, government, employer) to extract sensitive information. CyberShield-EDU has a planned (not yet implemented) audio detection module for vishing.

---

## W

### Whitelist
A list of explicitly approved entities. CyberShield-EDU's `verified_providers` table serves as a whitelist of legitimate organizations. URLs matching whitelisted domains receive a "Shield of Trust" badge indicating verified authenticity.

---

## X

### XP (Experience Points)
The unit of progress measurement in CyberShield-EDU's gamification system. Students earn XP by performing scans (+10-15), completing quizzes (+50), and finishing educational modules (up to +150). XP determines the user's level: `level = (XP ÷ 100) + 1`.

### XSS (Cross-Site Scripting)
A web security vulnerability that allows attackers to inject malicious scripts into web pages viewed by other users. CyberShield-EDU prevents XSS through input sanitization (HTML tag stripping and entity escaping).

---

*This glossary covers 75+ terms across cybersecurity, AI/ML, web development, and platform-specific concepts. For deeper exploration of any topic, refer to the corresponding technical documentation.*
