-- CyberShield-EDU: Unified Database Setup & Seeding Script
-- Target: MySQL / MariaDB (XAMPP Environment)

CREATE DATABASE IF NOT EXISTS cybershield;
USE cybershield;

-- 1. Users Table (Aligned with app.models.schema.User)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'student',
    xp INT DEFAULT 0,
    level INT DEFAULT 1,
    badges JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Scan Records Table (Aligned with app.models.schema.ScanRecord)
CREATE TABLE IF NOT EXISTS scan_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    scan_type VARCHAR(20) NOT NULL,
    input_data TEXT,
    prediction VARCHAR(20),
    confidence FLOAT,
    reasoning JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Scam Keywords Table (Aligned with app.models.schema.ScamKeyword)
CREATE TABLE IF NOT EXISTS scam_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(100) UNIQUE NOT NULL,
    added_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 4. Awareness Content Table (Aligned with app.models.schema.AwarenessContent)
CREATE TABLE IF NOT EXISTS awareness_content (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty VARCHAR(20),
    link VARCHAR(500),
    examples JSON,
    path_id VARCHAR(50) NULL,
    path_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Verified Providers Table (Aligned with app.models.schema.VerifiedProvider)
CREATE TABLE IF NOT EXISTS verified_providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    official_url VARCHAR(500),
    category VARCHAR(50),
    security_tips TEXT,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Quiz Questions Table (Aligned with app.models.schema.QuizQuestion)
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text',
    is_scam BOOLEAN,
    explanation TEXT,
    difficulty VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Scam Reports Table (Aligned with app.models.schema.ScamReport)
CREATE TABLE IF NOT EXISTS scam_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255),
    description TEXT,
    evidence_path VARCHAR(500),
    is_anonymous BOOLEAN DEFAULT TRUE,
    user_id INT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);


-- ==========================================
-- SEED DATA
-- ==========================================

-- Default Admin (Password: admin123 - PBKDF2 Placeholder)
-- Note: Replace with actual hash from backend during live setup if needed.
-- Placeholder: pbkdf2:sha256:600000$placeholder$admin123hash
INSERT IGNORE INTO users (id, username, email, hashed_password, role) 
VALUES (1, 'admin', 'admin@cybershield.edu', 'pbkdf2:sha256:600000$rOljdJpP8nFp$3e6c0d6b9d6a7a5f6c7a9b8c7d6e5f4g3h2i1j0k9l8m7n6o5p4q3r2s1t0u', 'admin');

-- Seed Awareness Content (Knowledge Modules)
INSERT IGNORE INTO awareness_content (category, title, description, difficulty, link, examples, path_id, path_order) VALUES
('Threat Type', 'Internship Scams', 'Detailed guide on identifying Internship Scams targeting students and graduates.', 'Beginner', '#', '["Unsolicited offers via WhatsApp or Telegram", "High salary for minimal work", "Vague job descriptions", "Pressure to \'secure your seat\' with payment"]', 'scam-0', 0),
('Threat Type', 'Scholarship/Grant Scams', 'Protect your education funding from predatory processing fees and fake winners circles.', 'Beginner', '#', '["Guaranteed winnings for contests you never entered", "Requests for sensitive bank details \'for the trial\'", "Handling fees required for \'tax processing\'"]', 'scam-1', 1),
('Pro Tip', 'Verify Before You Pay', 'No legitimate employer or internship provider will ever ask you to pay a \'registration fee\' or \'security deposit\' before joining.', 'Easy', '#', '["Look for official domains", "Never pay upfront", "Companies don\'t recruit via generic @gmail accounts"]', 'tip-0', 10),
('Pro Tip', 'Check the Email Domain', 'Official recruitment emails usually come from company domains, not from generic providers.', 'Easy', '#', '["Look for @google.com, not @google-hr.gmail.com", "Verify the sender on LinkedIn", "Check the official hiring portal"]', 'tip-1', 11);

-- Seed Verified Providers
INSERT IGNORE INTO verified_providers (name, official_url, category, security_tips) VALUES
('Google Student Careers', 'https://buildyourfuture.withgoogle.com/', 'Internship', 'Google recruiters will ALWAYS use @google.com emails. No registration fees are ever required for interviews.'),
('Chegg Scholarships', 'https://www.chegg.com/scholarships', 'Scholarship', 'Trusted platform for discovering thousands of legitimate student scholarships. Never provide credit card details to apply.'),
('Microsoft Internship Program', 'https://careers.microsoft.com/students', 'Internship', 'Offers come only through microsoft.com portals. Beware of LinkedIn DMs asking for "processing fees".');

-- Seed Quiz Questions
INSERT IGNORE INTO quiz_questions (content, is_scam, explanation, difficulty) VALUES
('You receive a WhatsApp message from a \'HR Manager\' offering a remote internship at Google with a salary of 50,000 INR/month. They ask you to pay 500 INR for processing.', 1, 'Legitimate companies like Google never use WhatsApp for first-contact recruitment and NEVER ask for money.', 'Beginner'),
('A PDF offer letter has no digital signature and was sent from recruitment.google@gmail.com.', 1, 'A generic email address (@gmail, @outlook) for a major corporation is a significant red flag.', 'Beginner');

-- Seed Initial Keywords
INSERT IGNORE INTO scam_keywords (keyword) VALUES
('registration fee'),
('security deposit'),
('processing charge'),
('urgent payment'),
('gift card payment'),
('exclusive offer'),
('guaranteed scholarship'),
('no interview required');
