# Weekly Sync App - Streamlit UI

A simple web interface for the Weekly Sync mentor-mentee reporting system.

## Features

### 🔐 Authentication
- User registration (automatic mentor/mentee assignment)
- Login/logout functionality

### 👨‍🎓 Mentee Features
- Submit weekly reports with accomplishments and aspirations (required)
- Optionally add blockers/concerns/comments
- View their latest 2 submitted reports
- Search and view reports from specific weeks
- Auto-populated week numbers and years

### 👨‍🏫 Mentor Features
- View list of assigned mentees with contact details
- Search and filter reports by mentee (required)
- Optional week and year filters for specific reports
- View latest 5 reports per mentee when no specific filters are applied

## Setup & Usage

### 1. Install Dependencies
```bash
# Make sure you're in the venv
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt
```

### 2. Start the FastAPI Backend
```bash
# In terminal 1
./venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

### 3. Start the Streamlit UI
```bash
# In terminal 2 (new terminal)
source venv/bin/activate
streamlit run streamlit_app.py
```

### 4. Access the Application
- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs

## Usage Flow

1. **Register**: Create accounts for mentors first, then mentees (with mentor email)
2. **Login**: Use your credentials to access role-based dashboard
3. **Mentees**: Submit weekly reports using the form
4. **Mentors**: Review mentee progress and reports

## Sample Users

**Important**: The test users from `test_models.py` have placeholder password hashes and cannot be used to login via the Streamlit UI.

**Recommended approach**: 
1. **Register new users** through the Streamlit registration form
2. **Create a mentor first** (leave mentor email blank)
3. **Create mentees** (enter the mentor's email)

**Example Registration Flow:**
1. Register mentor: name="John Mentor", email="john@company.com", password="mypassword" (leave mentor email blank)
2. Register mentee: name="Jane Mentee", email="jane@company.com", password="mypassword", mentor_email="john@company.com"
3. Login with the credentials you just created

This ensures proper password hashing and role assignment.

## Technical Details

- **Frontend**: Single-file Streamlit app (streamlit_app.py)
- **Backend**: FastAPI REST API
- **Authentication**: Simple session-based (stored in Streamlit session state)
- **Data**: All data fetched from FastAPI backend via HTTP requests 