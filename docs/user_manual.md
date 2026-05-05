# User Manual — CyberShield-EDU

> A comprehensive guide for students and administrators to navigate, utilize, and master every feature of the CyberShield-EDU cybersecurity protection platform. This manual covers every page, every interaction flow, and every gamification mechanic in detail.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Dashboard Navigation](#2-dashboard-navigation)
3. [The Detection Hub — Scanning for Threats](#3-the-detection-hub--scanning-for-threats)
4. [Text Scan — Message Analysis](#4-text-scan--message-analysis)
5. [URL Scan — Link Analysis](#5-url-scan--link-analysis)
6. [PDF Scan — Document Forensics](#6-pdf-scan--document-forensics)
7. [Image Scan — Forensic Image Audit](#7-image-scan--forensic-image-audit)
8. [Understanding Scan Results](#8-understanding-scan-results)
9. [Education Hub — Building Cyber Awareness](#9-education-hub--building-cyber-awareness)
10. [The Academy — Gamification & XP System](#10-the-academy--gamification--xp-system)
11. [Spot the Scam — Interactive Quiz](#11-spot-the-scam--interactive-quiz)
12. [Phishing Simulation — Realistic Scenarios](#12-phishing-simulation--realistic-scenarios)
13. [Scan History — Your Audit Trail](#13-scan-history--your-audit-trail)
14. [Account Settings & Profile](#14-account-settings--profile)
15. [Reporting a Scam — Community Protection](#15-reporting-a-scam--community-protection)
16. [Admin Dashboard — For Administrators](#16-admin-dashboard--for-administrators)
17. [Developer Portal — API Integration](#17-developer-portal--api-integration)
18. [Browser Extension — Quick Scanning](#18-browser-extension--quick-scanning)
19. [Tips for Staying Safe](#19-tips-for-staying-safe)

---

## 1. Getting Started

### 1.1. Creating Your Account

1. Navigate to the CyberShield-EDU platform (default: `http://localhost:8080`)
2. Click **"Sign Up"** on the login page
3. Enter your **username**, **email**, and **password**
4. Click **"Register"**
5. You'll be redirected to the login page with a success message

### 1.2. Logging In

1. Enter your **username** and **password** on the login page
2. Click **"Login"**
3. Upon successful authentication, you'll be redirected to the Detection Hub
4. Your session token is valid for 30 minutes and is automatically included in all subsequent API requests

### 1.3. Guest Mode

You can use the detection features **without logging in** (guest mode), but:
- Your scans will not be saved to your history
- You will not earn XP or badges
- You cannot access the gamification academy or profile features

For the full experience, creating an account is recommended.

---

## 2. Dashboard Navigation

### 2.1. Navigation Header

The top navigation bar provides access to all major sections:

| Button | Destination | Description |
|:---|:---|:---|
| 🏠 **Home** | `index.html` | Landing page and platform overview |
| 🔍 **Detector** | `detector.html` | Multi-tab threat scanning hub |
| 🎓 **Education** | `education.html` | Awareness modules and learning content |
| 📋 **My Scans** | `history.html` | Personal scan history with filtering |
| 🧠 **Quiz** | `quiz.html` | Interactive "Spot the Scam" challenges |
| 📊 **Admin** | `admin.html` | *(Admin only)* System analytics dashboard |

### 2.2. The Command Center Pill

Located on the right side of the header, the **Command Center Pill** displays at-a-glance:
- 🏆 **Current Level** (e.g., Lv. 4)
- ⚡ **Total XP** (e.g., 340 XP)
- 👤 **Username** — Click to access Settings

This pill is updated in real-time whenever XP is earned, providing constant visibility into your security mastery progress.

### 2.3. Theme Toggle

Use the **Light/Dark mode toggle** (typically a sun/moon icon) to switch between:
- **Dark Mode:** Deep navy background with glowing accents — easy on the eyes for extended use
- **Light Mode:** Clean, bright interface for high-contrast readability

Your theme choice is saved automatically and persists across sessions.

---

## 3. The Detection Hub — Scanning for Threats

The Detection Hub (`detector.html`) is your central scanning interface. It presents a **tabbed interface** with 4 active scan types:

| Tab | Icon | Purpose | Input Method |
|:---|:---|:---|:---|
| Text Scan | 📱 | Analyze messages from SMS, WhatsApp, Email | Paste text into textarea |
| URL Scan | 🔗 | Check suspicious links before clicking them | Paste URL into input field |
| PDF Scan | 📄 | Upload and analyze documents | File upload (drag & drop or browse) |
| Image Scan | 📸 | Forensic analysis of screenshots | File upload (JPG, PNG, BMP) |

**Basic workflow for all scan types:**
1. Select the appropriate tab
2. Provide input (text, URL, or file)
3. Click the **"Analyze"** button
4. Wait for the result (text/URL: ~1-3 seconds; PDF/Image: may show a loading spinner while background processing completes)
5. Review the **verdict** (Scam 🔴 / Safe 🟢), **confidence score**, and **detailed reasoning**
6. If logged in, XP is automatically awarded

---

## 4. Text Scan — Message Analysis

### 4.1. What It Does

The Text Scan module analyzes free-text messages using a **Multilingual DistilBERT AI model** that can detect scam patterns in over 100 languages. It performs:
- **AI Sentiment Analysis:** Detects urgency, pressure, and reward-based manipulation
- **Pattern Matching:** Checks against a database of known scam keywords and phrases
- **Context Analysis:** Identifies social engineering conflicts (e.g., a "professor" asking for your OTP)
- **Company Impersonation:** Cross-references brand names mentioned in text against actual link domains

### 4.2. How to Use

1. Click the **"Text Scan"** tab
2. Copy the suspicious message from WhatsApp, SMS, Telegram, or Email
3. Paste it into the large text area
4. Click **"Analyze Message"**

### 4.3. What to Scan

- WhatsApp messages about job offers or internships
- SMS texts with "urgent" account alerts
- Email bodies containing scholarship announcements
- Telegram messages claiming to be from "HR" departments
- Any message asking for personal information, payment, or login credentials

### 4.4. Understanding Text Results

The result panel shows:
- **Verdict:** SCAM (red) or SAFE (green) with confidence percentage
- **Reasoning Trail:** A numbered list of every detection signal that contributed to the verdict
- **Score Breakdown:** Pie/bar chart showing contribution of AI analysis, pattern matching, impersonation detection, and context analysis
- **Insights:** Detected sentiment (Urgency/Pressure, Unexpected Reward), linguistic complexity, and any impersonated brand

**Example scam detection:**
> *"URGENT: You have been selected for a remote data entry position at Google paying $35/hr. Pay $200 equipment fee at http://g00gle-jobs.xyz/apply"*
>
> **Result:** 🔴 SCAM (97% confidence)
> - AI Model: Detected scam intent with high confidence
> - Pattern Hit: "equipment fee" → Direct monetary request
> - Impersonation Alert: Mentions "Google" but link goes to g00gle-jobs.xyz
> - Context: Authority figure ("selected") combined with payment request

---

## 5. URL Scan — Link Analysis

### 5.1. What It Does

The URL Scan module performs **deep 9-layer analysis** of any web link:

| Layer | Detection | What It Catches |
|:---|:---|:---|
| 1 | Protocol check | HTTP (insecure) connections |
| 2 | URL shortener detection | Bit.ly, TinyURL that hide real destinations |
| 3 | Typosquatting | paypa1.com impersonating paypal.com |
| 4 | Shannon entropy | Machine-generated random domain names (DGA) |
| 5 | Homoglyph detection | Cyrillic characters mimicking Latin letters |
| 6 | IP masking | Direct IP addresses instead of domains |
| 7 | Subdomain abuse | login.paypal.com.attacker.net tricks |
| 8 | External intelligence | URLScan.io community reputation |
| 9 | Deep scan | Fetches the page and AI-analyzes its content |

### 5.2. How to Use

1. Click the **"URL Scan"** tab
2. Copy the suspicious link (right-click → "Copy link address")
3. Paste it into the URL input field
4. Click **"Analyze Link"**

### 5.3. Understanding URL Results

- **Scam Score:** A 0-100 scale showing threat level
- **Score Breakdown:** Visual representation of which heuristic layers flagged the URL
- **GeoIP Forensics:** Country, ISP, and data center hosting information with flag emoji
- **Redirect Chain:** Full path from the original URL through any redirects to the final destination
- **Trust Verification:** Whether the domain matches a verified provider in the Shield of Trust database

---

## 6. PDF Scan — Document Forensics

### 6.1. What It Does

The PDF Scan module performs **forensic analysis** on uploaded documents, looking at:
- **Metadata:** Author name, creation tool, PDF producer, version
- **Encryption:** Whether the document is password-protected (evasion tactic)
- **Digital Signatures:** Whether the document is officially signed
- **Content Analysis:** AI reads the document text for scam language
- **Embedded Links:** Extracts and scans ALL URLs found in the document
- **Ghost Links:** Discovers hidden annotation-based URLs invisible to the reader

### 6.2. How to Use

1. Click the **"PDF Scan"** tab
2. Click "Choose File" or drag and drop your PDF
3. Click **"Analyze Document"**
4. A loading indicator appears — PDF analysis runs in the background (typically 10-30 seconds)
5. Results appear automatically when processing completes

### 6.3. What to Upload

- Job offer letters you received via email
- Scholarship award notifications
- University admission documents from unofficial sources
- Financial documents requesting payment
- Any PDF you received from an unverified source

### 6.4. Understanding PDF Results

- **Forensic Metadata:** Author, creator tool, and PDF version flags
- **Signature Status:** ✅ Digitally signed (trustworthy) or ❌ No signature (warning)
- **Embedded URL Report:** Each URL found in the PDF with its individual scam analysis
- **Ghost Link Alerts:** Any hidden URLs receive special HIGH priority warnings

---

## 7. Image Scan — Forensic Image Audit

### 7.1. What It Does

The Image Scan module performs the most comprehensive analysis, combining:

| Analysis | Technology | Purpose |
|:---|:---|:---|
| **OCR** | Tesseract | Extracts readable text from screenshots |
| **Platform Detection** | Text patterns | Identifies WhatsApp, Telegram, Email origin |
| **EXIF Metadata** | PIL/Pillow | Detects AI generation tool signatures |
| **Texture Analysis** | OpenCV Laplacian | Identifies synthetically smooth AI-generated images |
| **QR Code Scan** | OpenCV | Detects and scans QR codes embedded in images |
| **Content AI** | DistilBERT | Analyzes extracted text for scam language |
| **URL Scan** | URL Detector | Scans any URLs found in the image text |

### 7.2. How to Use

1. Click the **"Image Scan"** tab
2. Upload a screenshot (JPG, PNG, or BMP)
3. Click **"Analyze Image"**
4. Wait for the forensic report (may take 5-15 seconds)
5. Review the multi-layered forensic dossier

### 7.3. What to Upload

- Screenshots of WhatsApp messages about job offers
- Screenshots of Instagram DMs with suspicious proposals
- Screenshots of SMS messages claiming urgent account action
- Images of QR codes you received
- Photos of ID cards or documents that may be AI-generated
- Profile pictures of suspected fake accounts

### 7.4. Understanding Image Results

- **Forensic Report:** Comprehensive breakdown including:
  - **Integrity Score (0-100):** Weighted composite of all forensic signals
  - **Texture Verdict:** "Natural" (real photo) or "Suspiciously Smooth" (potential AI generation)
  - **Metadata Trust Level:** High (has camera data) / Low (missing or shows AI tool)
  - **AI Generation Alert:** If EXIF data contains Stable Diffusion, Midjourney, DALL-E signatures
  - **Platform Origin:** Where the screenshot came from (WhatsApp, Telegram, etc.)
  - **Extracted Text:** Full OCR output from the image
  - **URL Analysis:** Any links found in the image text, individually analyzed

---

## 8. Understanding Scan Results

### 8.1. Verdict Colors

| Color | Verdict | Meaning | Action |
|:---|:---|:---|:---|
| 🔴 Red | SCAM | Content classified as fraudulent | Do not interact, block sender |
| 🟢 Green | SAFE | No threat indicators detected | Proceed with normal caution |

### 8.2. Confidence Score

The confidence percentage indicates how certain the system is about its verdict:
- **90-100%:** Very high confidence — strong detection signals
- **70-89%:** High confidence — multiple indicators present
- **50-69%:** Moderate confidence — some suspicious elements
- **Below 50%:** Low confidence — minimal threat signals

### 8.3. Reasoning Trail

Every scan provides a numbered list of human-readable reasons explaining WHY the content was flagged. These are educational — they teach you what specific patterns to watch for:

- *"AI Model: Detected urgency/pressure language"* → The message uses time pressure tactics
- *"Typosquatting Detected: 'paypa1' closely resembles 'paypal' (Distance: 1)"* → The domain is a fake look-alike
- *"Context Alert: Detected social engineering pattern — 'Professor' requesting 'OTP'"* → Authority figures would never ask for this
- *"Ghost Link Found: Hidden annotation URI not visible in document text"* → The PDF contains hidden malicious links

### 8.4. Score Breakdown

For advanced users, the score breakdown shows the numerical contribution of each analysis component:
- **AI Analysis:** Raw machine learning model confidence
- **Patterns:** Heuristic keyword and regex pattern matches
- **Impersonation:** Company brand-domain mismatch detection
- **Context:** Social engineering role-action conflict detection

---

## 9. Education Hub — Building Cyber Awareness

### 9.1. Knowledge Modules

The Education Hub presents structured learning content organized by category:
- **Threat Types:** Detailed guides on specific scam categories (Internship Scams, Scholarship Fraud, etc.)
- **Pro Tips:** Quick, actionable security advice (Verify Before You Pay, Check the Email Domain, etc.)

Each module includes:
- 📝 **Description:** Detailed explanation of the threat
- 📋 **Red Flags:** Specific indicators to watch for (bullet list of real-world examples)
- 🎯 **Difficulty Level:** Beginner, Easy, Intermediate
- ⚡ **XP Reward:** Complete the module to earn educational XP

### 9.2. Scam of the Week

A rotating featured scam highlighting the latest trending threat, currently featuring social engineering scams like the "Instagram Task" scam.

### 9.3. Wellness Support

CyberShield-EDU includes mental health guidance for students who have been targeted:
- **Key Message:** "Being targeted by a scam is NOT your fault."
- **Grounding Exercises:** 5-4-3-2-1 technique, Box Breathing, Physical Movement
- **Support Resources:** University counseling services, peer support guidance

### 9.4. Emergency Contacts

Direct links to official reporting channels:
- 🇮🇳 **India:** Cyber Crime Helpline 1930, cybercrime.gov.in
- 🌍 **Global:** Google Phishing Report, FTC Fraud Report

---

## 10. The Academy — Gamification & XP System

### 10.1. How XP Works

Every interaction with CyberShield-EDU earns you Experience Points:

| Activity | XP Earned | Notes |
|:---|:---|:---|
| Text scan | +10 XP | Must be logged in |
| URL scan | +15 XP | Must be logged in |
| PDF scan | Variable | Awarded via background task |
| Image scan | Variable | Awarded via background task |
| Quiz completion | +50 XP | Per quiz session |
| Education module | Up to +150 XP | Capped per request |
| Phishing simulation | Up to +150 XP | Capped per request |

### 10.2. Level System

Your level is calculated from your total XP:

| XP | Level | Rank Title |
|:---|:---|:---|
| 0-99 | Level 1 | **Cyber Scout** — Just beginning your journey |
| 100-199 | Level 2 | **Cyber Scout** — Getting familiar with threats |
| 200-499 | Level 3-5 | **Forensic Guardian** — Active scanner with growing skills |
| 500-999 | Level 6-10 | **Cyber Sentinel** — Experienced defender |
| 1000+ | Level 11+ | **Grand Protector** — Master-level security expert |

### 10.3. Badges

Badges are achievement-based awards for reaching specific milestones:

| Badge | Icon | Condition | Meaning |
|:---|:---|:---|:---|
| First Response | 🛡️ | Complete your first scan | You've started your security journey |
| Phishing Hunter | 🎣 | Complete 10 URL scans | You're actively checking suspicious links |

### 10.4. Level-Up Celebrations

When you reach a new level, the system triggers:
1. A 🏆 **toast notification** displaying your new rank
2. A full-screen **confetti animation** in your brand colors
3. Updated display in the Command Center pill

### 10.5. Academy Dashboard

The Academy page (`academy.html`) shows your complete dossier:
- **XP Progress Bar:** Visual representation of progress toward next level
- **XP to Next Level:** Exact points needed
- **Badge Grid:** Visual display of all earned badges with glow effects
- **Rank Display:** Your current title and level

---

## 11. Spot the Scam — Interactive Quiz

### 11.1. How It Works

1. Navigate to the **Quiz** page
2. You receive 5 randomized questions from the database
3. Each question presents a realistic scenario (message, email, document situation)
4. Determine whether the scenario is a **SCAM** or **SAFE**
5. After answering, the correct answer is revealed with a detailed **explanation**
6. Completing the quiz awards **50 XP**

### 11.2. Example Question

> *"You receive a WhatsApp message from a 'HR Manager' offering a remote internship at Google with a salary of 50,000 INR/month. They ask you to pay 500 INR for processing."*
>
> **Answer:** 🔴 SCAM
>
> **Explanation:** *"Legitimate companies like Google never use WhatsApp for first-contact recruitment and NEVER ask for money."*

---

## 12. Phishing Simulation — Realistic Scenarios

The Phishing Simulation pages (`phish-sim.html`, `scenarios.html`) present extended, multi-step scenarios where you roleplay receiving and evaluating suspicious communications. These simulations are more detailed than quiz questions and walk you through:

1. Recognizing initial red flags in a message
2. Investigating the sender's identity
3. Analyzing embedded links and attachments
4. Making a decision: Interact or Block?
5. Learning the correct response with expert breakdown

Completing simulations earns educational XP (up to 150 XP per session).

---

## 13. Scan History — Your Audit Trail

### 13.1. Accessing History

Navigate to **"My Scans"** from the navigation header. This page shows your complete scan history, ordered by most recent first.

### 13.2. History Entry Fields

Each entry displays:
- **Type:** Text / URL / PDF / Image
- **Input:** What you scanned (first 50 characters)
- **Verdict:** Scam / Safe with confidence
- **Reasoning:** Detection signals from that scan
- **Timestamp:** When the scan was performed

### 13.3. Requirements

- You must be **logged in** for scans to be recorded
- Guest scans are processed but not saved to history
- History is personal — each user only sees their own scans

---

## 14. Account Settings & Profile

### 14.1. Accessing Settings

Click your **username** in the Command Center pill or navigate to `settings.html`.

### 14.2. Profile Information

- **Username:** Your display name
- **Email:** Your registered email
- **Role:** Student or Admin
- **Member Since:** Account creation date

### 14.3. Security Statistics

View your scanning activity breakdown:
- Total scans across all categories
- URL scans completed
- Image scans completed
- PDF scans completed

### 14.4. Theme Preference

Toggle between Light and Dark modes. Your choice persists across sessions.

### 14.5. Developer Mode

Advanced users can access the Developer Portal to:
- Generate API keys for external integration
- View API documentation
- Test sandbox endpoints

---

## 15. Reporting a Scam — Community Protection

### 15.1. How to Report

1. Navigate to the **Report** section
2. Enter the **company or entity name** being impersonated
3. Provide a **detailed description** of the scam
4. Optionally upload **evidence** (screenshot, document)
5. Choose whether to submit **anonymously**
6. Click **"Submit Report"**

### 15.2. What Happens Next

- Your report is created with status **"Pending"**
- Administrators can review and process reports through the admin dashboard
- Recent reports appear in the community ticker visible to other users
- Evidence files are stored securely on the server

### 15.3. Rate Limiting

To prevent abuse, scam reporting is limited to **3 submissions per minute** per IP address.

---

## 16. Admin Dashboard — For Administrators

### 16.1. Access Requirements

Only users with the **admin** role can access the admin dashboard. The default admin account is:
- **Username:** `admin`
- **Password:** `admin123`

### 16.2. System Analytics

The dashboard displays real-time metrics:
- **Total Scans:** Aggregate count of all detection operations
- **Scams Detected:** Count and percentage of threats found
- **Active Models:** Number of operational AI models
- **Active Rules:** Count of configured detection patterns and keywords
- **7-Day Trend Chart:** Daily scan volume over the past week
- **Distribution Chart:** Breakdown by scan type (text, URL, PDF, image)

### 16.3. Keyword Management

- View all configured scam keywords
- Add new keywords that immediately activate in the detection engine
- Keywords added through the admin panel take effect instantly — no restart required

### 16.4. Pattern Management

- Create new detection patterns (keyword, regex, TLD, domain types)
- Set risk scores for each pattern (0.0 to 1.0)
- Enable/disable patterns without deleting them
- All changes are immediately synced to the in-memory Pattern Engine cache

---

## 17. Developer Portal — API Integration

### 17.1. Getting an API Key

1. Navigate to the **Developer** page
2. Provide a name for your key (e.g., "My Mobile App")
3. Click **"Generate Key"**
4. **Copy and save the key immediately** — it is shown only once

### 17.2. Using the API

Include the key in the `X-API-Key` header:
```bash
curl -X POST http://localhost:8000/api/v1/public/detect/text \
  -H "X-API-Key: cs_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"text": "Suspicious message to analyze"}'
```

### 17.3. Sandbox Mode

For testing without consuming your daily quota, add the sandbox header:
```bash
-H "X-Sandbox: true"
```
This returns simulated results without actual AI analysis.

### 17.4. Rate Limits

Each API key has a daily limit of **1,000 requests**. The counter resets every 24 hours. When the limit is reached, the API returns `429 Too Many Requests`.

---

## 18. Browser Extension — Quick Scanning

### 18.1. Installation

See [Browser Extension Setup](./setup_guide.md#10-browser-extension-setup) in the Setup Guide.

### 18.2. Usage

1. Click the **CyberShield EDU Protector** icon in your Chrome toolbar
2. A popup appears with a text area
3. Paste any suspicious text
4. Click **"Analyze Text"**
5. Results appear directly in the popup:
   - 🚨 **Red:** Scam detected with confidence and top reason
   - ✅ **Green:** Content appears safe

### 18.3. Requirements

- The CyberShield-EDU backend must be running on `localhost:8000`
- The extension communicates directly with the backend API

---

## 19. Tips for Staying Safe

### 🛡️ The Golden Rules

1. **Never pay upfront** for jobs, internships, or scholarships — legitimate organizations never require "registration fees" or "security deposits"
2. **Check the email domain** — Official recruitment emails come from `@company.com`, not `@gmail.com`
3. **Verify before you click** — Use CyberShield's URL scanner before clicking any link
4. **Look for digital signatures** — Official documents (offer letters, admissions) should be digitally signed
5. **Trust your instincts** — If something seems too good to be true, it probably is
6. **Use strong, unique passwords** — Never reuse passwords across different services
7. **Enable 2FA everywhere** — Two-factor authentication adds a critical security layer
8. **Report suspicious content** — Use CyberShield's reporting feature to protect other students
9. **Never share OTPs** — No legitimate entity will ever ask for your verification codes
10. **Stay educated** — Complete the CyberShield academy modules to build lasting cyber awareness

---

*Stay vigilant. Trust but verify. Your security mastery journey starts here.*

*CyberShield-EDU — Built for students, by students. 🛡️*
