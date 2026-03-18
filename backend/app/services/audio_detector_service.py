import os
import io
from app.services.text_detector import text_detector
from app.utils.logger import logger

# Note: In a production environment, we'd use whisper or a cloud API.
# For this demo, we'll implement a keyword-based vishing analyzer for transcribed text.

class AudioDetectorService:
    def __init__(self):
        # Mocking transcription for the demo if SpeechRecognition isn't available
        # In real usage: self.recognizer = sr.Recognizer()
        pass

    async def analyze_audio(self, audio_bytes: bytes, filename: str):
        """Transcribes audio and analyzes for vishing patterns."""
        logger.info(f"Analyzing audio file: {filename}")
        
        # simulated transcription for common vishing scenarios
        transcription = self._mock_transcription(filename)
        
        if not transcription:
            return {
                "prediction": "safe",
                "confidence": 0.5,
                "reasoning": ["Could not extract clear speech patterns from audio."],
                "transcription": ""
            }

        # Analyze transcribed text
        result = await text_detector.analyze(transcription)
        
        # Add vishing-specific reasoning
        vishing_keywords = ["bank", "irs", "lawsuit", "arrest", "immediate", "gift card", "social security"]
        vishing_hits = [k for k in vishing_keywords if k in transcription.lower()]
        
        if vishing_hits:
            result["reasoning"].insert(0, f"Detected Vishing (Voice Phishing) keywords: {', '.join(vishing_hits)}")
            result["prediction"] = "scam"
            result["confidence"] = max(result["confidence"], 0.92)

        result["source"] = "audio_vishing_scan"
        result["transcription"] = transcription
        
        return result

    def _mock_transcription(self, filename: str) -> str:
        """Heuristic transcription based on filename for demo purposes."""
        name = filename.lower()
        if "bank" in name or "alert" in name:
            return "This is an automated message from your bank. Your account has been compromised. Please call us immediately to verify your social security number and prevent arrest."
        if "intern" in name or "offer" in name:
            return "Congratulations on your internship offer! We need a security deposit of two hundred dollars for your company laptop. Please pay via gift card."
        return "Hello, I am calling to check if you are available for a meeting tomorrow at ten AM."

audio_detector = AudioDetectorService()
