# Weekly Sync App - Streamlit UI

A simple web interface for the Weekly Sync mentor-mentee reporting system.

## Features

### 🔐 Authentication
- User registration (automatic mentor/mentee assignment)
- Login/logout functionality

### 👨‍🎓 Mentee Features
- Submit weekly reports with accomplishments, blockers, and aspirations
- View their own submitted reports
- Auto-populated week numbers and years

### 👨‍🏫 Mentor Features
- View list of assigned mentees
- Review all reports from their mentees
- Summary table and detailed report views

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

## Sample Users (from test_models.py)

If you've run `python test_models.py`, you can login with:

**Mentors:**
- alice.johnson@company.com (password: any password - SHA256 of what you enter)
- bob.smith@company.com

**Mentees:**
- charlie.brown@company.com
- diana.prince@company.com
- edward.wilson@company.com

## Technical Details

- **Frontend**: Single-file Streamlit app (streamlit_app.py)
- **Backend**: FastAPI REST API
- **Authentication**: Simple session-based (stored in Streamlit session state)
- **Data**: All data fetched from FastAPI backend via HTTP requests 