import pytest
# Pathing is handled by conftest.py at the root
from app.services.text_detector import text_detector

from app.services.url_detector import url_detector


@pytest.mark.asyncio
async def test_text_scam_detection():
    """Verify that high-urgency financial text is flagged correctly."""
    scam_text = "CONGRATULATIONS! You must pay a $50 registration fee immediately to secure your internship."
    result = await text_detector.analyze(scam_text)
    assert result["prediction"] == "scam"
    # Verify AI Confidence (Now > 0.9 after fine-tuning)
    assert result["confidence"] > 0.9 
    # Verify Pattern Engine highlights (Check for our specific seed description)
    assert any("Direct monetary request" in hit for hit in result["highlights"])


@pytest.mark.asyncio
async def test_url_homoglyph_detection():
    """Verify that homoglyph spoofing is detected."""
    # Using a Cyrillic 'а' (U+0430) instead of Latin 'a'
    homoglyph_url = "http://pаypal.com" 
    result = await url_detector.analyze(homoglyph_url)
    assert result["prediction"] == "scam"
    assert any("Homoglyph" in reason for reason in result["reasoning"])

@pytest.mark.asyncio
async def test_url_entropy_logic():
    """Verify that machine-generated (DGA) domains are flagged."""
    dga_url = "http://axv12-z99-phish-portal.xyz"
    result = await url_detector.analyze(dga_url)
    assert result["metadata"]["entropy"] > 3.5

