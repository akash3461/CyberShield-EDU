import requests
import json

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def test_endpoint(name, method, url, data=None):
    print(f"--- Testing {name} ---")
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error testing {name}: {e}")
    print("\n")

if __name__ == "__main__":
    # 1. Root
    test_endpoint("Root", "GET", f"{BASE_URL}/")
    
    # 2. Awareness
    test_endpoint("Awareness", "GET", f"{BASE_URL}/awareness")
    
    # 3. Scam Text Detection (Scam case)
    test_endpoint("Scam Text (Positive)", "POST", f"{API_V1}/detect/text", 
                  {"text": "Congratulations! You selected for remote internship. Please pay 2000 INR registration fee."})
    
    # 4. Scam Text Detection (Safe case)
    test_endpoint("Safe Text (Negative)", "POST", f"{API_V1}/detect/text", 
                  {"text": "Hey, are we still on for the movie tonight?"})
