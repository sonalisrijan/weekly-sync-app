# 1:1 Weekly Report API Guide

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
uvicorn main:app --reload
```

The API will be available at: http://localhost:8000

### 3. View API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 API Endpoints

### **User Management**

#### 1. Register User
**POST** `/register`

Registers a new user (mentor or mentee based on `mentor_email` field).

```json
{
  "name": "John Smith",
  "email": "john.smith@company.com",
  "password": "password123",
  "team_name": "Engineering",
  "current_position": "Senior Manager",
  "office_location": "New York",
  "mentor_email": null  // null = mentor, email = mentee
}
```

**curl example:**
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@company.com",
    "password": "password123",
    "team_name": "Engineering",
    "current_position": "Junior Developer",
    "office_location": "New York",
    "mentor_email": "john.smith@company.com"
  }'
```

#### 2. User Login
**POST** `/login`

```json
{
  "email": "alice@company.com",
  "password": "password123"
}
```

#### 3. Get User Profile
**GET** `/users/{user_id}`

```bash
curl http://localhost:8000/users/1
```

#### 4. Get Mentees for Mentor
**GET** `/mentors/{mentor_id}/mentees`

Returns all active mentees for a specific mentor.

```bash
curl http://localhost:8000/mentors/1/mentees
```

### **Weekly Reports**

#### 1. Create Weekly Report
**POST** `/weekly-reports?mentee_id={mentee_id}`

```json
{
  "week_number": 45,
  "year": 2024,
  "accomplishments": "Completed user auth module, fixed 3 bugs",
  "blockers_concerns_comments": "Need help with database optimization",
  "aspirations": "Learn system architecture"
}
```

**curl example:**
```bash
curl -X POST "http://localhost:8000/weekly-reports?mentee_id=2" \
  -H "Content-Type: application/json" \
  -d '{
    "week_number": 45,
    "year": 2024,
    "accomplishments": "Completed user authentication module",
    "blockers_concerns_comments": "Need help with database queries",
    "aspirations": "Want to learn more about system design"
  }'
```

#### 2. Get Latest 2 Reports for Mentee
**GET** `/mentees/{mentee_id}/reports/latest`

Perfect for mentor dashboard - shows the most recent submissions.

```bash
curl http://localhost:8000/mentees/2/reports/latest
```

#### 3. Get All Reports for Mentor
**GET** `/mentors/{mentor_id}/reports`

Shows all reports from all of the mentor's mentees.

```bash
curl http://localhost:8000/mentors/1/reports
```

#### 4. Update Weekly Report
**PUT** `/weekly-reports/{report_id}`

```json
{
  "week_number": 45,
  "year": 2024,
  "accomplishments": "Updated accomplishments text",
  "blockers_concerns_comments": "Updated concerns",
  "aspirations": "Updated aspirations"
}
```

#### 5. Delete Weekly Report
**DELETE** `/weekly-reports/{report_id}`

```bash
curl -X DELETE http://localhost:8000/weekly-reports/1
```

## 🧪 Testing the API

### Option 1: Run the Test Script
```bash
python test_api.py
```

This will automatically test all endpoints with sample data.

### Option 2: Use FastAPI Docs
1. Go to http://localhost:8000/docs
2. Use the interactive interface to test each endpoint
3. Click "Try it out" on any endpoint

### Option 3: Manual Testing with curl

**Complete workflow example:**

```bash
# 1. Register a mentor
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sarah Wilson",
    "email": "sarah@company.com",
    "password": "password123",
    "team_name": "Product",
    "current_position": "Senior Manager",
    "office_location": "San Francisco"
  }'

# 2. Register a mentee
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mike Chen",
    "email": "mike@company.com", 
    "password": "password123",
    "team_name": "Product",
    "current_position": "Associate PM",
    "office_location": "San Francisco",
    "mentor_email": "sarah@company.com"
  }'

# 3. Create a weekly report (assuming mentee_id=2)
curl -X POST "http://localhost:8000/weekly-reports?mentee_id=2" \
  -H "Content-Type: application/json" \
  -d '{
    "week_number": 45,
    "year": 2024,
    "accomplishments": "Finished user research, created wireframes",
    "blockers_concerns_comments": "Need approval for design changes",
    "aspirations": "Want to lead a product launch next quarter"
  }'

# 4. Get mentees for mentor (assuming mentor_id=1)
curl http://localhost:8000/mentors/1/mentees

# 5. Get latest reports for mentee
curl http://localhost:8000/mentees/2/reports/latest
```

## 🔐 Data Flow

### Registration Flow:
1. **Mentor registers first** (no `mentor_email`)
2. **Mentee registers** with mentor's email in `mentor_email` field
3. System automatically links mentee to mentor

### Report Submission Flow:
1. **Mentee creates report** via `/weekly-reports` endpoint
2. **System prevents duplicates** (same mentee + week + year)
3. **Mentor views reports** via mentor dashboard endpoints

### Mentor Dashboard Flow:
1. **Get all mentees**: `/mentors/{id}/mentees`
2. **For each mentee, get latest 2 reports**: `/mentees/{id}/reports/latest`
3. **Or get all reports at once**: `/mentors/{id}/reports`

## 🗄️ Database Schema

The API uses these SQLAlchemy models:
- **User**: Stores both mentors and mentees (self-referencing)
- **WeeklyReport**: Stores weekly submissions with foreign keys to mentee and mentor

## 🚨 Error Handling

The API returns proper HTTP status codes:
- **200**: Success
- **400**: Bad Request (validation errors, duplicates)
- **401**: Unauthorized (invalid login)
- **404**: Not Found (user/report doesn't exist)

Example error response:
```json
{
  "detail": "Email already registered"
}
```

## 📊 Response Examples

### User Response:
```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john@company.com",
  "user_type": "mentor",
  "team_name": "Engineering",
  "current_position": "Senior Manager", 
  "office_location": "New York",
  "mentor_id": null
}
```

### Weekly Report Response:
```json
{
  "id": 1,
  "mentee_id": 2,
  "mentor_id": 1,
  "week_number": 45,
  "year": 2024,
  "accomplishments": "Completed authentication module",
  "blockers_concerns_comments": "Need help with database optimization",
  "aspirations": "Learn system architecture",
  "submission_date": "2024-11-07T10:30:00Z",
  "mentee_name": "Alice Johnson"
}
```

## 🔄 Next Steps

Once your API is working, you can:
1. **Build Streamlit frontend** that calls these endpoints
2. **Add JWT authentication** for secure sessions
3. **Add email notifications** when reports are submitted
4. **Deploy to production** (Heroku, AWS, etc.)

---

🎉 **Your 1:1 Weekly Report API is ready to use!** 