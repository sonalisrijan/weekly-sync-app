import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

def make_api_call(endpoint, method='GET', data=None):
    """Make API calls to the FastAPI backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'PUT':
            response = requests.put(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url)
        else:
            response = requests.get(url)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.json().get('detail', 'Unknown error')
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Make sure the FastAPI server is running."
    except Exception as e:
        return None, str(e)

def login_page():
    st.title("🤝 Weekly Sync App")
    st.subheader("Login")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if email and password:
                data, error = make_api_call("/auth/login", "POST", {
                    "email": email,
                    "password": password
                })
                
                if data:
                    st.session_state.user = data
                    st.session_state.page = 'dashboard'
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(f"Login failed: {error}")
            else:
                st.error("Please fill in all fields")
    
    st.divider()
    if st.button("Don't have an account? Register here"):
        st.session_state.page = 'register'
        st.rerun()

def register_page():
    st.title("📝 Register New User")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
        
        with col2:
            team_name = st.text_input("Team Name")
            position = st.text_input("Current Position")
            location = st.text_input("Office Location")
        
        mentor_email = st.text_input("Mentor Email (leave blank if you're a mentor)")
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if all([name, email, password, team_name, position, location]):
                data, error = make_api_call("/auth/register", "POST", {
                    "name": name,
                    "email": email,
                    "password": password,
                    "team_name": team_name,
                    "current_position": position,
                    "office_location": location,
                    "mentor_email": mentor_email if mentor_email else None
                })
                
                if data:
                    st.success("Registration successful! Please login.")
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(f"Registration failed: {error}")
            else:
                st.error("Please fill in all required fields")
    
    if st.button("← Back to Login"):
        st.session_state.page = 'login'
        st.rerun()

def mentee_dashboard():
    st.title(f"👨‍🎓 Mentee Dashboard - {st.session_state.user['name']}")
    
    tab1, tab2 = st.tabs(["📝 Submit Report", "📊 My Reports"])
    
    with tab1:
        st.subheader("Submit Weekly Report")
        
        with st.form("report_form"):
            col1, col2 = st.columns(2)
            with col1:
                week_number = st.number_input("Week Number", min_value=1, max_value=53, value=datetime.now().isocalendar()[1])
            with col2:
                year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.now().year)
            
            accomplishments = st.text_area("🎯 Accomplishments", 
                placeholder="What did you accomplish this week?", height=100)
            
            blockers = st.text_area("🚧 Blockers/Concerns/Comments", 
                placeholder="Any blockers, concerns, or comments?", height=100)
            
            aspirations = st.text_area("🌟 Aspirations", 
                placeholder="What are your goals for next week?", height=100)
            
            submitted = st.form_submit_button("Submit Report")
            
            if submitted:
                if all([accomplishments, blockers, aspirations]):
                    data, error = make_api_call(
                        f"/reports/?mentee_id={st.session_state.user['id']}", 
                        "POST", {
                            "week_number": int(week_number),
                            "year": int(year),
                            "accomplishments": accomplishments,
                            "blockers_concerns_comments": blockers,
                            "aspirations": aspirations
                        }
                    )
                    
                    if data:
                        st.success("Report submitted successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to submit report: {error}")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("My Recent Reports")
        
        data, error = make_api_call(f"/reports/mentees/{st.session_state.user['id']}/latest")
        
        if data:
            if data:
                for report in data:
                    with st.expander(f"Week {report['week_number']}, {report['year']} - {report['submission_date'][:10]}"):
                        st.write("**🎯 Accomplishments:**")
                        st.write(report['accomplishments'])
                        st.write("**🚧 Blockers/Concerns:**")
                        st.write(report['blockers_concerns_comments'])
                        st.write("**🌟 Aspirations:**")
                        st.write(report['aspirations'])
            else:
                st.info("No reports submitted yet.")
        else:
            st.error(f"Failed to load reports: {error}")

def mentor_dashboard():
    st.title(f"👨‍🏫 Mentor Dashboard - {st.session_state.user['name']}")
    
    tab1, tab2 = st.tabs(["👥 My Mentees", "📊 All Reports"])
    
    with tab1:
        st.subheader("My Mentees")
        
        data, error = make_api_call(f"/users/mentors/{st.session_state.user['id']}/mentees")
        
        if data:
            if data:
                for mentee in data:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.write(f"**{mentee['name']}**")
                            st.write(f"📧 {mentee['email']}")
                        with col2:
                            st.write(f"💼 {mentee['current_position']}")
                            st.write(f"🏢 {mentee['team_name']}")
                        with col3:
                            st.write(f"📍 {mentee['office_location']}")
                        st.divider()
            else:
                st.info("No mentees assigned yet.")
        else:
            st.error(f"Failed to load mentees: {error}")
    
    with tab2:
        st.subheader("All Reports from My Mentees")
        
        data, error = make_api_call(f"/reports/mentors/{st.session_state.user['id']}")
        
        if data:
            if data:
                # Create a summary table
                reports_summary = []
                for report in data:
                    reports_summary.append({
                        "Mentee": report['mentee_name'],
                        "Week": f"{report['week_number']}, {report['year']}",
                        "Submitted": report['submission_date'][:10],
                        "Preview": report['accomplishments'][:50] + "..." if len(report['accomplishments']) > 50 else report['accomplishments']
                    })
                
                df = pd.DataFrame(reports_summary)
                st.dataframe(df, use_container_width=True)
                
                st.subheader("Detailed Reports")
                
                for report in data:
                    with st.expander(f"{report['mentee_name']} - Week {report['week_number']}, {report['year']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Submitted:** {report['submission_date'][:10]}")
                        with col2:
                            st.write(f"**Mentee:** {report['mentee_name']}")
                        
                        st.write("**🎯 Accomplishments:**")
                        st.write(report['accomplishments'])
                        st.write("**🚧 Blockers/Concerns:**")
                        st.write(report['blockers_concerns_comments'])
                        st.write("**🌟 Aspirations:**")
                        st.write(report['aspirations'])
            else:
                st.info("No reports submitted yet.")
        else:
            st.error(f"Failed to load reports: {error}")

def main():
    # Sidebar
    with st.sidebar:
        if st.session_state.user:
            st.write(f"👋 Welcome, **{st.session_state.user['name']}**")
            st.write(f"Role: **{st.session_state.user['user_type'].title()}**")
            st.write(f"Team: **{st.session_state.user['team_name']}**")
            
            if st.button("🚪 Logout"):
                st.session_state.user = None
                st.session_state.page = 'login'
                st.rerun()
        else:
            st.write("Not logged in")
    
    # Main content
    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'register':
        register_page()
    elif st.session_state.page == 'dashboard':
        if st.session_state.user:
            if st.session_state.user['user_type'] == 'mentee':
                mentee_dashboard()
            else:
                mentor_dashboard()
        else:
            st.session_state.page = 'login'
            st.rerun()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Weekly Sync App",
        page_icon="🤝",
        layout="wide"
    )
    main() 