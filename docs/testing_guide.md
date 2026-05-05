# Testing Guide — CyberShield-EDU

> Comprehensive testing strategy, test suite documentation, instructions for running tests, coverage analysis, and guidance for writing new tests. This guide covers unit tests, integration tests, manual verification, and browser-based testing.

---

## Table of Contents

1. [Testing Philosophy](#1-testing-philosophy)
2. [Test Environment Setup](#2-test-environment-setup)
3. [Running Tests](#3-running-tests)
4. [Existing Test Suite](#4-existing-test-suite)
5. [Test Coverage Map](#5-test-coverage-map)
6. [Manual Verification Procedures](#6-manual-verification-procedures)
7. [Writing New Tests](#7-writing-new-tests)
8. [Testing Anti-Patterns to Avoid](#8-testing-anti-patterns-to-avoid)
9. [CI/CD Integration](#9-cicd-integration)

---

## 1. Testing Philosophy

CyberShield-EDU follows a **pragmatic testing strategy** that prioritizes:

1. **Detection Accuracy:** The most critical tests verify that the AI and heuristic engines correctly classify known scam/safe inputs
2. **False Positive Prevention:** Tests ensure legitimate content is not incorrectly flagged
3. **Integration Integrity:** Verify cross-service orchestration (e.g., PDF → URL → Text pipeline)
4. **Regression Prevention:** When a new pattern or keyword is added, existing tests must continue passing

### Testing Pyramid

```
        ╱ Manual Testing ╲           ← Browser-based, end-to-end
       ╱   (Verification)  ╲
      ╱─────────────────────╲
     ╱  Integration Tests    ╲       ← Cross-service, API-level
    ╱─────────────────────────╲
   ╱     Unit Tests            ╲     ← Detection engine logic
  ╱─────────────────────────────╲
```

---

## 2. Test Environment Setup

### 2.1. Prerequisites

Ensure the following are running before executing tests:
- ✅ **XAMPP MySQL** with `cybershield` database
- ✅ Backend **virtual environment activated**
- ✅ **Redis server** (required for Celery task tests)
- ⚠️ **Internet connection** (required for first-run model download)

### 2.2. Test Directory Structure

```
CyeberShield-EDU/
├── tests/
│   ├── test_detectors.py       # Detection engine unit tests
│   └── conftest.py             # Pytest configuration and path setup
├── backend/
│   └── app/
│       └── services/           # Modules under test
└── pytest.ini / pyproject.toml # (Optional) Pytest configuration
```

### 2.3. Configuration

The `conftest.py` file at the project root handles Python path configuration, ensuring that `from app.services.xxx import xxx` works correctly from the test directory.

---

## 3. Running Tests

### 3.1. Basic Test Execution

```bash
# Navigate to project root
cd "d:\AI Projects\CyeberShield-EDU"

# Activate virtual environment
backend\venv\Scripts\activate

# Run all tests
pytest tests/ -v
```

### 3.2. Run Specific Test File

```bash
pytest tests/test_detectors.py -v
```

### 3.3. Run Specific Test Function

```bash
pytest tests/test_detectors.py::test_text_scam_detection -v
```

### 3.4. Run with Detailed Output

```bash
# Show print statements and full assertion details
pytest tests/ -v -s --tb=long
```

### 3.5. Run Async Tests

CyberShield-EDU's detection services are `async`, so tests require `pytest-asyncio`:

```bash
pip install pytest-asyncio
pytest tests/ -v
```

All async test functions must be decorated with `@pytest.mark.asyncio`:
```python
@pytest.mark.asyncio
async def test_text_scam_detection():
    result = await text_detector.analyze("Pay $50 fee")
    assert result["prediction"] == "scam"
```

---

## 4. Existing Test Suite

### 4.1. `test_detectors.py` — Detection Engine Tests

#### Test 1: `test_text_scam_detection`
**Purpose:** Verify that high-urgency financial scam text is correctly classified.

```python
@pytest.mark.asyncio
async def test_text_scam_detection():
    """Verify that high-urgency financial text is flagged correctly."""
    scam_text = "CONGRATULATIONS! You must pay a $50 registration fee immediately to secure your internship."
    result = await text_detector.analyze(scam_text)

    assert result["prediction"] == "scam"
    assert result["confidence"] > 0.9
    assert any("Direct monetary request" in hit for hit in result["highlights"])
```

**What This Validates:**
- ✅ DistilBERT correctly classifies urgency + financial request as scam
- ✅ AI confidence exceeds 90% threshold for high-signal input
- ✅ Pattern Engine detects "registration fee" keyword and produces correct highlight description

---

#### Test 2: `test_url_homoglyph_detection`
**Purpose:** Verify that Cyrillic character substitution attacks are detected.

```python
@pytest.mark.asyncio
async def test_url_homoglyph_detection():
    """Verify that homoglyph spoofing is detected."""
    homoglyph_url = "http://pаypal.com"  # Cyrillic 'а' (U+0430)
    result = await url_detector.analyze(homoglyph_url)

    assert result["prediction"] == "scam"
    assert any("Homoglyph" in reason for reason in result["reasoning"])
```

**What This Validates:**
- ✅ Layer 6 (Homoglyph Detection) correctly identifies the Cyrillic `а` character
- ✅ The substitution pushes the confidence above the scam threshold
- ✅ Reasoning trail includes the "Homoglyph" alert message

---

#### Test 3: `test_url_entropy_logic`
**Purpose:** Verify that machine-generated (DGA) domains produce high entropy scores.

```python
@pytest.mark.asyncio
async def test_url_entropy_logic():
    """Verify that machine-generated (DGA) domains are flagged."""
    dga_url = "http://axv12-z99-phish-portal.xyz"
    result = await url_detector.analyze(dga_url)

    assert result["metadata"]["entropy"] > 3.5
```

**What This Validates:**
- ✅ Shannon entropy calculation produces correct values for random-looking domains
- ✅ Entropy exceeds the 3.5 threshold indicating high randomness
- ✅ Metadata correctly reports the computed entropy value

---

## 5. Test Coverage Map

### 5.1. What's Covered

| Component | Tests Exist | Coverage Level |
|:---|:---|:---|
| Text Detection — Scam classification | ✅ | **Core Logic** |
| Text Detection — Keyword highlights | ✅ | **Core Logic** |
| URL Detection — Homoglyph detection | ✅ | **Specific Layer** |
| URL Detection — Entropy calculation | ✅ | **Specific Layer** |

### 5.2. What Needs Coverage (Recommended New Tests)

| Component | Priority | Suggested Test |
|:---|:---|:---|
| **Text Detection — Safe content** | High | Verify benign text returns `prediction: "safe"` |
| **Text Detection — Multilingual** | High | Test Hindi/Spanish scam text detection |
| **Text Detection — Impersonation** | High | Test brand name + mismatched URL detection |
| **Text Detection — Context conflicts** | Medium | Test role + action social engineering patterns |
| **URL Detection — Typosquatting** | High | Test `paypa1.com` → Levenshtein match |
| **URL Detection — Protocol check** | Medium | Test HTTP vs HTTPS risk difference |
| **URL Detection — Safe URL** | High | Verify `https://google.com` returns safe |
| **URL Detection — IP masking** | Medium | Test `http://192.168.1.1/login` |
| **URL Detection — Subdomain abuse** | Medium | Test deeply nested subdomains |
| **Pattern Engine — Keyword match** | High | Test dynamic keyword matching from DB |
| **Pattern Engine — Regex match** | Medium | Test compiled regex pattern execution |
| **Pattern Engine — TLD match** | Medium | Test `.xyz` TLD detection |
| **Trust Service — Whitelist** | High | Test verified domain returns badge |
| **Trust Service — Impersonation** | High | Test brand-domain mismatch detection |
| **PDF Analyzer — Ghost links** | Medium | Test hidden annotation URL extraction |
| **PDF Analyzer — Signature check** | Medium | Test `/Sig` byte marker detection |
| **Image Detector — Texture** | Medium | Test Laplacian variance calculation |
| **Gamification — XP award** | Medium | Test level calculation formula |
| **Gamification — Badge check** | Medium | Test milestone badge triggers |
| **Auth — Password hash** | High | Roundtrip hash → verify test |
| **Auth — JWT** | High | Encode → decode → verify payload integrity |
| **Sanitizer — HTML strip** | Medium | Test `<script>` tag removal |
| **Sanitizer — JS protocol** | Medium | Test `javascript:` blocking |
| **Rate Limiter** | Low | Test 429 response after limit exceeded |

---

## 6. Manual Verification Procedures

### 6.1. End-to-End Detection Verification

| # | Test Scenario | Input | Expected Output |
|:---|:---|:---|:---|
| 1 | English scam text | "Pay $50 registration fee immediately" | Prediction: scam, Confidence > 0.80 |
| 2 | Hindi scam text | "तुरंत अपना OTP भेजें" | Prediction: scam |
| 3 | Safe text | "Meeting is scheduled for tomorrow at 10am" | Prediction: safe |
| 4 | Typosquatting URL | `http://paypa1.com` | Typosquatting detected |
| 5 | Safe URL | `https://www.google.com` | Prediction: safe, Shield of Trust badge |
| 6 | Homoglyph URL | `http://pаypal.com` (Cyrillic а) | Homoglyph alert |
| 7 | High entropy URL | `http://xk39z-phish.xyz` | High entropy flagged |
| 8 | IP masking URL | `http://192.168.1.1/login` | IP masking detected |
| 9 | PDF with hidden links | Upload PDF with annotation URIs | Ghost links detected |
| 10 | Image with text | Screenshot of WhatsApp scam | OCR extracts text, NLP classifies |

### 6.2. Authentication Testing

| # | Test | Expected |
|:---|:---|:---|
| 1 | Register new user | 200 OK, user created |
| 2 | Login with valid credentials | JWT token returned |
| 3 | Login with invalid password | 401 Unauthorized |
| 4 | Access admin route as student | 403 Forbidden |
| 5 | Access history without token | 401 / empty result |
| 6 | Expired token | 401 Unauthorized |

### 6.3. Gamification Testing

| # | Test | Expected |
|:---|:---|:---|
| 1 | Scan as authenticated user | XP increases by 10-15 |
| 2 | Reach 100 XP | Level changes from 1 → 2 |
| 3 | First scan ever | "First Response" badge awarded |
| 4 | Complete quiz | +50 XP awarded |
| 5 | Award > 150 XP | 400 error "exceeds forensic ceiling" |

### 6.4. Admin Operation Testing

| # | Test | Expected |
|:---|:---|:---|
| 1 | Add new keyword as admin | Keyword appears in list, takes immediate effect |
| 2 | Add new pattern as admin | Pattern activates, next scan uses it |
| 3 | View system stats as admin | Accurate counts returned |
| 4 | Access admin as student | 403 Forbidden |

---

## 7. Writing New Tests

### 7.1. Test File Convention

```python
# tests/test_<module_name>.py

import pytest
from app.services.<service> import <service_instance>

@pytest.mark.asyncio
async def test_<specific_behavior>():
    """Human-readable description of what this test verifies."""
    # Arrange
    input_data = "..."

    # Act
    result = await service_instance.analyze(input_data)

    # Assert
    assert result["prediction"] == "expected"
    assert result["confidence"] > 0.XX
    assert any("Expected Reason" in r for r in result["reasoning"])
```

### 7.2. Example: New Text Detection Test

```python
@pytest.mark.asyncio
async def test_text_safe_content():
    """Verify that benign everyday text is not falsely flagged."""
    safe_text = "Hey, are we still meeting for the group project at the library tomorrow at 3pm?"
    result = await text_detector.analyze(safe_text)

    assert result["prediction"] == "safe"
    assert result["confidence"] < 0.50
    assert len(result["highlights"]) == 0
```

### 7.3. Example: New URL Detection Test

```python
@pytest.mark.asyncio
async def test_url_typosquatting_detection():
    """Verify Levenshtein distance catches 'amaz0n' typosquatting."""
    typo_url = "http://amaz0n.com/deals"
    result = await url_detector.analyze(typo_url)

    assert result["prediction"] == "scam"
    assert any("Typosquatting" in reason for reason in result["reasoning"])
    assert "amazon" in str(result["reasoning"]).lower()  # References the real brand
```

### 7.4. Example: Authentication Utility Test

```python
from app.utils.auth import get_password_hash, verify_password, create_access_token, decode_access_token

def test_password_hash_roundtrip():
    """Verify password hashing and verification work correctly."""
    password = "TestPassw0rd!"
    hashed = get_password_hash(password)

    assert hashed != password  # Hash is not plaintext
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_roundtrip():
    """Verify JWT encode/decode preserves payload data."""
    payload = {"sub": "testuser", "role": "student", "id": 42}
    token = create_access_token(payload)
    decoded = decode_access_token(token)

    assert decoded["sub"] == "testuser"
    assert decoded["role"] == "student"
    assert decoded["id"] == 42
    assert "exp" in decoded  # Expiry was added
```

### 7.5. Example: Sanitizer Test

```python
from app.utils.sanitizer import sanitizer

def test_html_tag_removal():
    """Verify HTML tags are stripped from user input."""
    malicious = '<script>alert("XSS")</script>Hello World'
    clean = sanitizer.clean_text(malicious)
    assert "<script>" not in clean
    assert "Hello World" in clean

def test_javascript_protocol_blocking():
    """Verify javascript: URLs are blocked."""
    result = sanitizer.sanitize_url("javascript:alert(1)")
    assert result == "blocked:unsafe-protocol"

def test_safe_url_passes():
    """Verify normal URLs pass through unmodified."""
    url = "https://www.google.com/search?q=test"
    result = sanitizer.sanitize_url(url)
    assert result == url
```

---

## 8. Testing Anti-Patterns to Avoid

| Anti-Pattern | Why It's Problematic | Better Approach |
|:---|:---|:---|
| Testing AI model accuracy to exact decimal | Model outputs may vary slightly across environments | Use threshold assertions (`> 0.80`) |
| Hardcoding reasoning text exactly | Reasoning strings may evolve | Use `any("keyword" in r for r in reasoning)` |
| Testing against live external APIs | URLScan.io may be unavailable, rate-limited, or slow | Mock external calls for unit tests |
| Testing file I/O with fixed paths | Paths differ across machines | Use `tempfile` or relative paths |
| Skipping async test markers | Tests will fail silently or hang | Always use `@pytest.mark.asyncio` |
| Testing the database state directly | Couples tests to DB state | Test service return values, not DB contents |

---

## 9. CI/CD Integration

### 9.1. GitHub Actions Configuration (Recommended)

```yaml
# .github/workflows/test.yml
name: CyberShield Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: cybershield
        ports:
          - 3306:3306
      redis:
        image: redis
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-asyncio

      - name: Import database schema
        run: mysql -h 127.0.0.1 -u root -proot cybershield < backend/setup_xampp.sql

      - name: Run tests
        env:
          DATABASE_URL: mysql+pymysql://root:root@127.0.0.1/cybershield
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: ci-test-secret-key
        run: pytest tests/ -v
```

### 9.2. Pre-Commit Hook (Optional)

```bash
# .git/hooks/pre-commit
#!/bin/sh
pytest tests/ -v --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

*Good tests don't just verify code works — they document how it's supposed to work. Every test is a living specification.*
