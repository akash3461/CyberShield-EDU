from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Boolean, Text, ForeignKey, func

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(20), default="student")
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    badges = Column(JSON, default=list) # List of badge names
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScanRecord(Base):
    __tablename__ = "scan_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    scan_type = Column(String(20)) # text, url, pdf, image
    input_data = Column(Text)
    prediction = Column(String(20))
    confidence = Column(Float)
    reasoning = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScamKeyword(Base):
    __tablename__ = "scam_keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(100), unique=True, index=True)
    weight = Column(Float, default=0.1) # New: impact on risk score
    added_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ThreatPattern(Base):
    """
    Pillar 2: Dynamic Pattern Engine.
    Allows for Regex, TLD, and DOM-specific structural matching.
    """
    __tablename__ = "threat_patterns"

    id = Column(Integer, primary_key=True, index=True)
    pattern_type = Column(String(20), index=True) # 'regex', 'keyword', 'tld', 'domain'
    value = Column(String(500), unique=True, index=True)
    risk_score = Column(Float, default=0.2) # Impact on the 0.0-1.0 scale
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    added_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AwarenessContent(Base):
    __tablename__ = "awareness_content"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50))
    title = Column(String(255))
    description = Column(Text)
    difficulty = Column(String(20))
    link = Column(String(500))
    examples = Column(JSON)
    path_id = Column(String(50), nullable=True) # e.g. "phishing-101"
    path_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VerifiedProvider(Base):
    __tablename__ = "verified_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    official_url = Column(String(500))
    category = Column(String(50)) # internship, scholarship
    security_tips = Column(Text)
    verified_at = Column(DateTime(timezone=True), server_default=func.now())
class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text) # Text or image URL
    content_type = Column(String(20)) # text, image
    is_scam = Column(Boolean)
    explanation = Column(Text)
    difficulty = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScamReport(Base):
    __tablename__ = "scam_reports"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), index=True)
    description = Column(Text)
    evidence_path = Column(String(500), nullable=True) # Path to uploaded file
    is_anonymous = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Optional link to registered user
    status = Column(String(20), default="pending") # pending, reviewed, resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemConfig(Base):
    """
    Dynamic system configuration for analysis thresholds, weights, and maintenance mode.
    """
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, index=True)
    value = Column(JSON) # Stores numbers, strings, or structured config
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
