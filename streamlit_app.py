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
    
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
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
                    # Clear login form
                    if "login_email" in st.session_state:
                        del st.session_state["login_email"]
                    if "login_password" in st.session_state:
                        del st.session_state["login_password"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(f"Login failed: {error}")
            else:
                st.error("Please fill in all fields")
    
    st.divider()
    if st.button("Don't have an account? Register here", key="go_to_register"):
        st.session_state.page = 'register'
        st.rerun()

def register_page():
    st.title("📝 Register New User")
    
    with st.form("register_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", key="reg_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
        
        with col2:
            team_name = st.text_input("Team Name", key="reg_team")
            position = st.text_input("Current Position", key="reg_position")
            location = st.text_input("Office Location", key="reg_location")
        
        mentor_email = st.text_input("Mentor Email (leave blank if you're a mentor)", key="reg_mentor_email")
        
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
                    # Clear the form by resetting session state keys
                    for key in ["reg_name", "reg_email", "reg_password", "reg_team", "reg_position", "reg_location", "reg_mentor_email"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(f"Registration failed: {error}")
            else:
                st.error("Please fill in all required fields")
    
    st.divider()
    
    if st.button("← Back to Login", key="back_to_login"):
        st.session_state.page = 'login'
        st.rerun()

def mentee_dashboard():
    st.title(f"👨‍🎓 Mentee Dashboard - {st.session_state.user['name']}")
    
    tab1, tab2 = st.tabs(["📝 Submit Report", "📊 My Reports"])
    
    with tab1:
        st.subheader("Submit Weekly Report")
        
        with st.form("report_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                week_number = st.number_input("Week Number", min_value=1, max_value=53, value=datetime.now().isocalendar()[1], key="report_week")
            with col2:
                year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.now().year, key="report_year")
            
            accomplishments = st.text_area("🎯 Accomplishments", 
                placeholder="What did you accomplish this week?", height=100, key="report_accomplishments")
            
            blockers = st.text_area("🚧 Blockers/Concerns/Comments (Optional)", 
                placeholder="Any blockers, concerns, or comments? (Leave blank if none)", height=100, key="report_blockers")
            
            aspirations = st.text_area("🌟 Aspirations", 
                placeholder="What are your goals for next week?", height=100, key="report_aspirations")
            
            submitted = st.form_submit_button("Submit Report")
            
            if submitted:
                # Only require accomplishments and aspirations, blockers is optional
                if accomplishments.strip() and aspirations.strip():
                    data, error = make_api_call(
                        f"/reports/?mentee_id={st.session_state.user['id']}", 
                        "POST", {
                            "week_number": int(week_number),
                            "year": int(year),
                            "accomplishments": accomplishments,
                            "blockers_concerns_comments": blockers if blockers.strip() else "No blockers or concerns reported.",
                            "aspirations": aspirations
                        }
                    )
                    
                    if data:
                        # Celebratory effect
                        st.balloons()
                        
                        st.success("✅ Report submitted successfully!")
                    else:
                        st.error(f"Failed to submit report: {error}")
                else:
                    st.error("Please fill in Accomplishments and Aspirations fields")
    
    with tab2:
        st.subheader("My Reports")
        
        # Section 1: Latest 2 Reports
        st.write("### 📊 Latest Reports")
        
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
            st.error(f"Failed to load latest reports: {error}")
        
        st.divider()
        
        # Section 2: Search by Week
        st.write("### 🔍 Search by Week")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            search_week = st.number_input("Week Number", min_value=1, max_value=53, 
                                        value=datetime.now().isocalendar()[1], key="search_week")
        with col2:
            search_year = st.number_input("Year", min_value=2020, max_value=2030, 
                                        value=datetime.now().year, key="search_year")
        with col3:
            search_button = st.button("🔍 Search", key="search_report")
        
        if search_button:
            # Check if mentee has a mentor assigned
            mentor_id = st.session_state.user.get('mentor_id')
            
            if not mentor_id:
                st.error("❌ No mentor assigned. Cannot search reports.")
            else:
                # Get all reports from mentor to find this mentee's specific report
                all_reports, error = make_api_call(f"/reports/mentors/{mentor_id}")
                
                if all_reports:
                    # Filter for this specific mentee and week
                    specific_report = [r for r in all_reports 
                                     if r['mentee_id'] == st.session_state.user['id'] 
                                     and r['week_number'] == search_week 
                                     and r['year'] == search_year]
                    
                    if specific_report:
                        report = specific_report[0]
                        st.success(f"✅ Found report for Week {search_week}, {search_year}")
                        
                        with st.container():
                            st.write(f"**📅 Submitted:** {report['submission_date'][:10]}")
                            st.write("**🎯 Accomplishments:**")
                            st.write(report['accomplishments'])
                            st.write("**🚧 Blockers/Concerns:**")
                            st.write(report['blockers_concerns_comments'])
                            st.write("**🌟 Aspirations:**")
                            st.write(report['aspirations'])
                    else:
                        st.warning(f"❌ No report found for Week {search_week}, {search_year}")
                        st.info("💡 Make sure you've submitted a report for this week.")
                else:
                    st.error(f"Failed to search reports: {error}")
        
        # Show instruction when no search is performed
        if not search_button:
            st.info("💡 Use the search above to find reports from specific weeks.")

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
        st.subheader("📊 Reports Search & Review")
        
        # Get mentees for dropdown
        mentees_data, mentees_error = make_api_call(f"/users/mentors/{st.session_state.user['id']}/mentees")
        
        if mentees_data:
            if mentees_data:
                # Search filters
                st.write("### 🔍 Filter Reports")
                
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    # Create mentee options for dropdown
                    mentee_options = ["Select a mentee..."] + [f"{mentee['name']}" for mentee in mentees_data]
                    selected_mentee = st.selectbox("👤 Select Mentee", mentee_options, key="mentor_mentee_filter")
                
                with col2:
                    filter_week = st.number_input("📅 Week (Optional)", min_value=0, max_value=53, 
                                                value=0, key="mentor_week_filter", 
                                                help="Leave as 0 to show all weeks")
                
                with col3:
                    filter_year = st.number_input("📆 Year (Optional)", min_value=0, max_value=2030, 
                                                value=0, key="mentor_year_filter",
                                                help="Leave as 0 to show all years")
                
                with col4:
                    search_reports = st.button("🔍 Search", key="mentor_search_reports")
                
                st.divider()
                
                # Handle search
                if search_reports or selected_mentee != "Select a mentee...":
                    if selected_mentee == "Select a mentee...":
                        st.warning("⚠️ Please select a mentee to view reports.")
                    else:
                        # Find selected mentee's ID
                        selected_mentee_data = next((m for m in mentees_data if m['name'] == selected_mentee), None)
                        
                        if selected_mentee_data:
                            # Get all reports for this mentor
                            all_reports, reports_error = make_api_call(f"/reports/mentors/{st.session_state.user['id']}")
                            
                            if all_reports:
                                # Filter reports for selected mentee
                                mentee_reports = [r for r in all_reports if r['mentee_id'] == selected_mentee_data['id']]
                                
                                # Apply week/year filters if specified
                                if filter_week > 0:
                                    mentee_reports = [r for r in mentee_reports if r['week_number'] == filter_week]
                                
                                if filter_year > 0:
                                    mentee_reports = [r for r in mentee_reports if r['year'] == filter_year]
                                
                                # Sort by submission date (newest first) and limit to 5 if no specific week/year
                                mentee_reports.sort(key=lambda x: x['submission_date'], reverse=True)
                                
                                if filter_week == 0 and filter_year == 0:
                                    mentee_reports = mentee_reports[:5]  # Latest 5 reports
                                
                                if mentee_reports:
                                    # Show filter summary
                                    filter_text = f"**{selected_mentee}**"
                                    if filter_week > 0 or filter_year > 0:
                                        if filter_week > 0 and filter_year > 0:
                                            filter_text += f" - Week {filter_week}, {filter_year}"
                                        elif filter_week > 0:
                                            filter_text += f" - Week {filter_week}"
                                        elif filter_year > 0:
                                            filter_text += f" - Year {filter_year}"
                                    else:
                                        filter_text += f" - Latest {len(mentee_reports)} reports"
                                    
                                    st.success(f"✅ Found {len(mentee_reports)} report(s) for {filter_text}")
                                    
                                    # Display reports
                                    for report in mentee_reports:
                                        with st.expander(f"Week {report['week_number']}, {report['year']} - {report['submission_date'][:10]}"):
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                st.write(f"**📅 Submitted:** {report['submission_date'][:10]}")
                                            with col2:
                                                st.write(f"**👤 Mentee:** {report['mentee_name']}")
                                            
                                            st.write("**🎯 Accomplishments:**")
                                            st.write(report['accomplishments'])
                                            st.write("**🚧 Blockers/Concerns:**")
                                            st.write(report['blockers_concerns_comments'])
                                            st.write("**🌟 Aspirations:**")
                                            st.write(report['aspirations'])
                                else:
                                    st.warning(f"❌ No reports found for {selected_mentee} with the specified filters.")
                                    st.info("💡 Try adjusting your search criteria or check if reports have been submitted.")
                            else:
                                st.error(f"Failed to load reports: {reports_error}")
                        else:
                            st.error("❌ Selected mentee not found.")
                else:
                    st.info("💡 Select a mentee above to view their reports. Week and year filters are optional.")
            else:
                st.info("No mentees assigned yet.")
        else:
            st.error(f"Failed to load mentees: {mentees_error}")

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