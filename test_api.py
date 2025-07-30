import requests
import json

# Base URL for your FastAPI app
BASE_URL = "http://localhost:8000"

def test_api():
    print("🚀 Testing 1:1 Weekly Report API\n")
    
    # Test 1: Register a mentor
    print("1. Registering a mentor...")
    mentor_data = {
        "name": "John Smith",
        "email": "john.smith@company.com",
        "password": "password123",
        "team_name": "Engineering",
        "current_position": "Senior Manager",
        "office_location": "New York"
        # No mentor_email = becomes a mentor
    }
    
    response = requests.post(f"{BASE_URL}/register", json=mentor_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        mentor = response.json()
        print(f"✅ Mentor registered: {mentor['name']} (ID: {mentor['id']})")
        mentor_id = mentor['id']
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test 2: Register a mentee
    print("\n2. Registering a mentee...")
    mentee_data = {
        "name": "Alice Johnson",
        "email": "alice.johnson@company.com", 
        "password": "password123",
        "team_name": "Engineering",
        "current_position": "Junior Developer",
        "office_location": "New York",
        "mentor_email": "john.smith@company.com"  # This makes them a mentee
    }
    
    response = requests.post(f"{BASE_URL}/register", json=mentee_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        mentee = response.json()
        print(f"✅ Mentee registered: {mentee['name']} (ID: {mentee['id']})")
        mentee_id = mentee['id']
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test 3: Login
    print("\n3. Testing login...")
    login_data = {
        "email": "alice.johnson@company.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Login successful: {user['name']} ({user['user_type']})")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 4: Get mentees for mentor
    print(f"\n4. Getting mentees for mentor (ID: {mentor_id})...")
    response = requests.get(f"{BASE_URL}/mentors/{mentor_id}/mentees")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        mentees = response.json()
        print(f"✅ Found {len(mentees)} mentees")
        for mentee in mentees:
            print(f"   - {mentee['name']} ({mentee['email']})")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 5: Create weekly report
    print(f"\n5. Creating weekly report for mentee (ID: {mentee_id})...")
    report_data = {
        "week_number": 45,
        "year": 2024,
        "accomplishments": "Completed user authentication module, fixed 3 critical bugs, attended team standup meetings daily.",
        "blockers_concerns_comments": "Need help with database optimization. Having issues with slow query performance on user table.",
        "aspirations": "Want to learn more about system architecture and take on more complex projects next quarter."
    }
    
    response = requests.post(f"{BASE_URL}/weekly-reports?mentee_id={mentee_id}", json=report_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        report = response.json()
        print(f"✅ Report created: Week {report['week_number']}, {report['year']}")
        report_id = report['id']
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test 6: Get latest reports for mentee
    print(f"\n6. Getting latest reports for mentee (ID: {mentee_id})...")
    response = requests.get(f"{BASE_URL}/mentees/{mentee_id}/reports/latest")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        reports = response.json()
        print(f"✅ Found {len(reports)} reports")
        for report in reports:
            print(f"   - Week {report['week_number']}, {report['year']}: {report['accomplishments'][:50]}...")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 7: Get all reports for mentor
    print(f"\n7. Getting all reports for mentor (ID: {mentor_id})...")
    response = requests.get(f"{BASE_URL}/mentors/{mentor_id}/reports")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        reports = response.json()
        print(f"✅ Found {len(reports)} reports from all mentees")
        for report in reports:
            print(f"   - {report['mentee_name']}: Week {report['week_number']}, {report['year']}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 8: Update report
    print(f"\n8. Updating weekly report (ID: {report_id})...")
    updated_report_data = {
        "week_number": 45,
        "year": 2024,
        "accomplishments": "Completed user authentication module, fixed 5 critical bugs (2 more than expected!), attended team standup meetings daily.",
        "blockers_concerns_comments": "Resolved database optimization issues with mentor's help. Query performance improved by 40%.",
        "aspirations": "Want to learn more about system architecture and mentor junior developers next quarter."
    }
    
    response = requests.put(f"{BASE_URL}/weekly-reports/{report_id}", json=updated_report_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        report = response.json()
        print(f"✅ Report updated successfully")
    else:
        print(f"❌ Error: {response.text}")
    
    print("\n✅ API testing completed successfully!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure your FastAPI server is running with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}") 