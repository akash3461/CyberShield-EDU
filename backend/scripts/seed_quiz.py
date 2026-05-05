import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.schema import QuizQuestion, Base
from app.config import settings

# Database setup
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_quiz():
    db = SessionLocal()
    try:
        # Clear existing questions to prevent duplicates
        db.query(QuizQuestion).delete()
        
        questions = [
            # --- Financial & Scholarship Fraud ---
            {
                "content": "CONGRATS! You are a finalist for the 'Academic Excellence' scholarship. Pay a $5 handling fee here to claim your $2,000 award: http://univ-awards-claim.com",
                "content_type": "text", "is_scam": True, "difficulty": "easy",
                "explanation": "Legitimate scholarships NEVER charge a fee to award money. This is a common 'advance fee' scam."
            },
            {
                "content": "University Financial Aid: We detected a discrepancy in your FAFSA filing. Please re-enter your SSN for verification: http://official-fafsa-verify.org",
                "content_type": "text", "is_scam": True, "difficulty": "medium",
                "explanation": "Official financial aid offices will never ask for your full SSN via an unencrypted or third-party .org link."
            },
            {
                "content": "Hey! I'm from the student grant office. We have an extra $500 for students this month. Dm me for more info!",
                "content_type": "text", "is_scam": True, "difficulty": "easy",
                "explanation": "Grants are never distributed via social media DMs from anonymous individual accounts."
            },

            # --- Urgency & Account Hijacking ---
            {
                "content": "URGENT: Your student portal password expires in 12 hours. Click here to keep your current password: http://portal-security-update.net",
                "content_type": "text", "is_scam": True, "difficulty": "easy",
                "explanation": "Creating an artificial sense of urgency to force a quick, unvetted action is a hallmark of phishing."
            },
            {
                "content": "Someone just tried to log into your account from Nigeria. If this was not you, send us the 6-digit code you just received to verify your identity.",
                "content_type": "text", "is_scam": True, "difficulty": "hard",
                "explanation": "This is a 2-Factor Authentication (MFA) bypass attempt. NEVER share verification codes with anyone."
            },
            {
                "content": "Google: A new device signed in to your account. If this was you, you can ignore this alert.",
                "content_type": "text", "is_scam": False, "difficulty": "medium",
                "explanation": "This is a standard informative alert from a legitimate provider with no urgent call to action or suspicious link."
            },

            # --- Social Engineering & Impersonation ---
            {
                "content": "Hey! This is Professor Miller from CS101. I'm locked out of my gradebook. Can you send me your login info so I can verify a student's grade?",
                "content_type": "text", "is_scam": True, "difficulty": "medium",
                "explanation": "Authority impersonation is used to exploit your trust. Professors have administrative access and will never need your credentials."
            },
            {
                "content": "Warning from IT: Your mailbox is full and you will stop receiving emails in 1 hour. Upgrade your storage here: http://mail-storage-upgrade.com",
                "content_type": "text", "is_scam": True, "difficulty": "easy",
                "explanation": "Fake mailbox storage warnings are common technical social engineering tactics."
            },

            # --- Job & Career Scams ---
            {
                "content": "WE ARE HIRING: Remote Assistant role. $40/hr. No experience needed. Use this link to apply: http://entry-level-career.site",
                "content_type": "text", "is_scam": True, "difficulty": "easy",
                "explanation": "Exaggerated salaries for remote work with no experience on untrusted TLDs (.site) are high-risk indicators."
            },
            {
                "content": "Your resume was selected for an interview at Tesla! Please download the 'Interview-Prep.zip' to preview the technical assessment.",
                "content_type": "text", "is_scam": True, "difficulty": "hard",
                "explanation": "Zip files in unsolicited job alerts often contain malware. Real companies use official candidate portals."
            },

            # --- High-Fidelity Forensic Expansion (New Questions) ---
            {
                "content": "Instagram Security: Your account is violating our copyright guidelines. Review the violation here or your account will be deleted: bit.ly/ig-security-check",
                "content_type": "text", "is_scam": True, "difficulty": "medium",
                "explanation": "Copyright violation DMs on social media often use shortened URLs (bit.ly) to hide phishing sites."
            },
            {
                "content": "Wait! You have an unclaimed $25 Starbucks Gift Card from your University Orientation survey. Claim it here: university-rewards.tk/claim",
                "content_type": "text", "is_scam": True, "difficulty": "easy",
                "explanation": "The TLD '.tk' is a high-risk Top-Level Domain frequently used for free hosting of malicious sites."
            },
            {
                "content": "Microsoft: Multiple failed login attempts on your account. Secure your account now: https://account.microsoft.com/security",
                "content_type": "text", "is_scam": False, "difficulty": "medium",
                "explanation": "This leads to an official, encrypted Microsoft domain. It's a legitimate security notification."
            },
            {
                "content": "Dear Student, your COVID-19 vaccination record needs to be updated for campus access. Upload your card to this student portal: http://campus-health-portal.info",
                "content_type": "text", "is_scam": True, "difficulty": "medium",
                "explanation": "Medical info is highly sensitive. Official university health portals usually end in .edu, not .info."
            },
            {
                "content": "Adobe Subscription: Your payment was declined. Please update your billing info to continue using Photoshop.",
                "content_type": "text", "is_scam": False, "difficulty": "medium",
                "explanation": "Standard billing notification with no suspicious links or urgent 'Account will be deleted' threats."
            },
            {
                "content": "Bank of America: Someone added a new recipient 'Z. Smith' to your account. If this was not you, call us immediately at 1-800-BANK-SAFE.",
                "content_type": "text", "is_scam": True, "difficulty": "hard",
                "explanation": "Voice Phishing (Vishing) often provides a fake support number to steal your bank credentials over the phone."
            },
            {
                "content": "Your Apple ID was used to purchase 'Fortnite: vBucks Bundle' for $99.99. If you did not make this purchase, click here to cancel: http://apple-support-cancel.com",
                "content_type": "text", "is_scam": True, "difficulty": "medium",
                "explanation": "Invoiced-based phishing uses shock value (unauthorized spending) to make you click without thinking."
            },
            {
                "content": "Hey! I missed the lecture today. Can you send me the PDF of the notes? Here's my WhatsApp: +1 555-0102",
                "content_type": "text", "is_scam": False, "difficulty": "easy",
                "explanation": "A simple request for notes with no malicious payload or suspicious data-gathering motive."
            },
            {
                "content": "Campus Police: A suspicious vehicle was seen in the North Parking lot. Stay vigilant and call 911 if you see anything.",
                "content_type": "text", "is_scam": False, "difficulty": "easy",
                "explanation": "General safety alert with no suspect link or request for user credentials."
            },
            {
                "content": "Zoom: Your meeting 'Quarterly Review' is starting now. Join here: https://zoom.us/j/123456789",
                "content_type": "text", "is_scam": False, "difficulty": "easy",
                "explanation": "Standard zoom link on the official zoom.us domain."
            },
            {
                "content": "Free Netflix for 1 year! Because of the pandemic, everyone gets free access. Claim here: netflix-free.com/student",
                "content_type": "text", "is_scam": True, "difficulty": "easy",
                "explanation": "The 'Free for everyone' promise is a classic social engineering hook for high-volume phishing."
            },
            {
                "content": "Your Amazon Prime membership is expiring. To continue your student discount, verify your .edu email at: amazon.com/student/verify",
                "content_type": "text", "is_scam": False, "difficulty": "medium",
                "explanation": "Legitimate verification flow on an official, trusted domain."
            },
            {
                "content": "IT Support: We are upgrading the Wi-Fi on campus. Please install this security certificate: WiFi-Security.crt.exe",
                "content_type": "text", "is_scam": True, "difficulty": "hard",
                "explanation": "A file named .crt.exe is a double-extension malware payload. Security certificates are never .exe files."
            },
            {
                "content": "Dropbox: 'Professor_Jones' shared a folder with you: 'Final-Exam-Prep'. Click to view.",
                "content_type": "text", "is_scam": False, "difficulty": "medium",
                "explanation": "Standard collaboration notification. However, always verify the sender's email address in the actual email header."
            },
            {
                "content": "ATTENTION: You won the Mega-Millions lottery! Send your address and bank account to facilitate the $500,000,000 transfer.",
                "content_type": "text", "is_scam": True, "difficulty": "easy",
                "explanation": "You cannot win a lottery you did not enter. This is a classic Nigerian 419 scam."
            },
            {
                "content": "Your PayPal account has been limited due to suspicious activity. Log in at: http://paypal-security-center.cn to resolve.",
                "content_type": "text", "is_scam": True, "difficulty": "medium",
                "explanation": "Legitimate financial services rarely use .cn (China) TLDs for their global security centers."
            },
            {
                "content": "Google: We blocked a suspicious login attempt on your account from London, UK. Check activity: https://myaccount.google.com/notifications",
                "content_type": "text", "is_scam": False, "difficulty": "medium",
                "explanation": "Links to the official google.com/notifications page for user verification."
            },
            {
                "content": "Hi! I'm from the University Career Center. We're looking for students for a $15/hr on-campus library job. Apply at the physical office in Hall 4.",
                "content_type": "text", "is_scam": False, "difficulty": "easy",
                "explanation": "Directs the user to a physical, verified location on campus."
            },
            {
                "content": "DHL: Your parcel is on hold due to missing duty fees. Please pay $2.50 to release the package: dhl-parcel-delivery.pw",
                "content_type": "text", "is_scam": True, "difficulty": "medium",
                "explanation": "The .pw TLD and 'small fee' hook are common indicators of delivery service phishing."
            },
            {
                "content": "Venmo: You just received $20 from 'Lunch Buddy'. View transaction in the Venmo App.",
                "content_type": "text", "is_scam": False, "difficulty": "easy",
                "explanation": "A standard notification directing you to use the official app rather than an external link."
            },
            {
                "content": "Your LinkedIn account was accessed from a new IP: 192.168.1.5. If this wasn't you, reset your password.",
                "content_type": "text", "is_scam": False, "difficulty": "medium",
                "explanation": "Standard security alert with no suspicious payload or data request."
            },
            {
                "content": "Facebook: Someone tagged you in a private video. See who it is here: http://fb-video-tag-login.com",
                "content_type": "text", "is_scam": True, "difficulty": "easy",
                "explanation": "Curiosity and social FOMO are used to drive users to fake login pages."
            },
            {
                "content": "Student Health: Flu shots are available this Thursday at the Student Union from 9 AM to 4 PM. Bring your student ID.",
                "content_type": "text", "is_scam": False, "difficulty": "easy",
                "explanation": "Informative alert for a physical event on campus."
            },
            {
                "content": "Your Norton Anti-Virus subscription renewed for $399.99. To cancel, call our helpdesk at +1 (888) 123-4567.",
                "content_type": "text", "is_scam": True, "difficulty": "hard",
                "explanation": "Classic invoice fraud. They want you to call so they can remotely access your computer for a 'refund'."
            },
            {
                "content": "Canvas: Your instructor posted a new announcement for 'Organic Chemistry'. Log in to review.",
                "content_type": "text", "is_scam": False, "difficulty": "easy",
                "explanation": "Standard educational platform notification."
            },
            {
                "content": "Warning: You've been targeted by a state-sponsored hacker. Click here for urgent protection: http://secure-shield-protect.net",
                "content_type": "text", "is_scam": True, "difficulty": "hard",
                "explanation": "High-fear tactics used to manipulate technically un-savvy users into installing malware."
            },
            {
                "content": "A friend shared a document via OneDrive: 'Graduation-Photo-List.doc.exe'.",
                "content_type": "text", "is_scam": True, "difficulty": "hard",
                "explanation": "The .doc.exe extension reveals this is an executable malware file, not a real document."
            },
            {
                "content": "University Registrar: The spring semester calendar has been updated. View it here: http://university.edu/registrar/calendar",
                "content_type": "text", "is_scam": False, "difficulty": "medium",
                "explanation": "Links to an official .edu domain in a standard subdirectory."
            },
            {
                "content": "Bitcoin: Your wallet received 0.05 BTC. Login to confirm: http://coinbase-login-verified.com",
                "content_type": "text", "is_scam": True, "difficulty": "medium",
                "explanation": "Fake crypto gains are used as bait to steal your actual wallet credentials."
            },
            {
                "content": "Discord Security: We detected a TOS violation on your account. Verify your identity at: discord-support-verify.com",
                "content_type": "text", "is_scam": True, "difficulty": "medium",
                "explanation": "Impersonates platform support to steal account tokens."
            }
        ]
        
        for q_data in questions:
            question = QuizQuestion(**q_data)
            db.add(question)
        
        db.commit()
        print(f"Successfully seeded {len(questions)} high-fidelity quiz questions!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_quiz()
