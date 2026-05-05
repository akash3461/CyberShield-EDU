import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_sync():
    print("--- 📡 CyberShield API Verification ---")
    
    # 1. Register
    reg_data = {
        "username": "verify_sync_user",
        "email": "sync@test.com",
        "password": "password123"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    print(f"Registration: {r.status_code} {r.text}")
    
    # 2. Login
    login_data = {"username": "verify_sync_user", "password": "password123"}
    r = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Token Obtained ✅")
    
    # 3. Test Reward (Fixed Prefix)
    reward_data = {"xp_amount": 75, "reason": "Surgical Verification Test"}
    r = requests.post(f"{BASE_URL}/awareness/reward", headers=headers, json=reward_data)
    print(f"Reward Status: {r.status_code}")
    print(f"Reward Response: {r.json()}")
    
    # 4. Test Profile (Fixed Double Prefix)
    r = requests.get(f"{BASE_URL}/gamification/profile", headers=headers)
    print(f"Profile Status: {r.status_code}")
    profile = r.json()
    print(f"Dossier XP: {profile.get('xp')} (Expected: 75)")
    print(f"Rank: {profile.get('rank')}")
    
    if profile.get("xp") == 75:
        print("\n🏆 VERIFICATION SUCCESS: Global XP Persistence is LIVE!")
    else:
        print("\n❌ VERIFICATION FAILED: XP Sync Issue Persistent.")

if __name__ == "__main__":
    test_sync()
