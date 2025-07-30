# Database Schema Documentation: 1:1 Weekly Report System

## Overview
This document outlines the database schema for a 1:1 weekly report submission web application built with FastAPI and Streamlit. The system manages mentor-mentee relationships and weekly report submissions.

## Schema Design

### 1. Users Table

The `users` table stores information for both mentors and mentees using a self-referencing design.

**Fields:**
- `id`: Primary key (auto-increment integer)
- `name`: Full name of the user (2-100 characters)
- `email`: Unique email address (validated)
- `password_hash`: Hashed password for authentication
- `user_type`: Enum ('mentor' or 'mentee')
- `mentor_id`: Foreign key referencing users.id (null for mentors)
- `team_name`: Team name (2-100 characters)
- `current_position`: Job position (2-100 characters)
- `office_location`: Office location (2-100 characters)
- `is_active`: Boolean flag for soft deletion
- `created_at`: Timestamp of record creation
- `updated_at`: Timestamp of last update

**Relationships:**
- Self-referencing: mentor_id → users.id
- One mentor can have many mentees
- One mentee has exactly one mentor

### 2. Weekly Reports Table

The `weekly_reports` table stores the weekly submissions from mentees to their mentors.

**Fields:**
- `id`: Primary key (auto-increment integer)
- `mentee_id`: Foreign key referencing users.id
- `mentor_id`: Foreign key referencing users.id
- `week_number`: Week number (1-53)
- `year`: Year of the report (2020-2030)
- `accomplishments`: Tasks finished and accomplishments (10-2000 characters)
- `blockers_concerns_comments`: Blockers, concerns, and comments (max 2000 characters)
- `aspirations`: Future aspirations (max 1000 characters)
- `submission_date`: When the report was submitted
- `created_at`: Timestamp of record creation
- `updated_at`: Timestamp of last update

**Constraints:**
- Unique constraint on (mentee_id, week_number, year) - prevents duplicate reports
- Both mentee_id and mentor_id must reference valid users

## Key Features

### 1. User Registration Flow
- Users register with all required information including mentor details
- System automatically determines user_type based on mentor_email presence:
  - If mentor_email provided → user is a mentee
  - If no mentor_email → user is a mentor
- Mentor lookup happens during registration to establish mentor_id relationship

### 2. Mentor Dashboard
- Mentors can query all their mentees using: `SELECT * FROM users WHERE mentor_id = {mentor_id}`
- For each mentee, mentors can view latest 2 reports using:
  ```sql
  SELECT * FROM weekly_reports 
  WHERE mentee_id = {mentee_id} 
  ORDER BY year DESC, week_number DESC 
  LIMIT 2
  ```

### 3. Mentee Report Submission
- Mentees submit weekly reports with validation:
  - Week number validation (1-53)
  - Year validation (2020-2030)
  - Content length validation
- System prevents duplicate submissions for same week/year
- Automatic mentor assignment based on mentee's mentor_id

### 4. Data Integrity
- Foreign key constraints ensure referential integrity
- Unique constraints prevent duplicate weekly reports
- Email uniqueness prevents duplicate user accounts
- Soft deletion using is_active flag preserves historical data

## Pydantic Models

The schema includes comprehensive Pydantic models for API validation:

### Request Models
- `UserCreate`: For user registration
- `WeeklyReportCreate`: For report submission
- `UserUpdate`, `WeeklyReportUpdate`: For updates

### Response Models
- `UserResponse`: Safe user data for API responses
- `WeeklyReportResponse`: Report data with mentee name
- `MenteeListItem`: Simplified mentee info for dropdowns
- `WeeklyReportSummary`: Summary for listing views

### Utility Models
- `LoginRequest`, `LoginResponse`: Authentication
- `ApiResponse`: Standardized API responses
- `UserType`: Enum for user types

## Security Considerations

1. **Password Storage**: Uses password hashing (implementation needed)
2. **Email Validation**: EmailStr type ensures valid email format
3. **Input Validation**: Field constraints prevent malicious input
4. **Soft Deletion**: is_active flag preserves data while hiding inactive users

## Query Patterns

### Common Queries for the Application:

1. **Get mentees for a mentor:**
   ```sql
   SELECT id, name, email, team_name, current_position, office_location
   FROM users 
   WHERE mentor_id = ? AND is_active = true
   ```

2. **Get latest 2 reports for a mentee:**
   ```sql
   SELECT wr.*, u.name as mentee_name
   FROM weekly_reports wr
   JOIN users u ON wr.mentee_id = u.id
   WHERE wr.mentee_id = ?
   ORDER BY wr.year DESC, wr.week_number DESC
   LIMIT 2
   ```

3. **Check if report exists for mentee/week/year:**
   ```sql
   SELECT COUNT(*) FROM weekly_reports
   WHERE mentee_id = ? AND week_number = ? AND year = ?
   ```

4. **Get mentor info for a mentee:**
   ```sql
   SELECT m.* FROM users m
   JOIN users mentee ON m.id = mentee.mentor_id
   WHERE mentee.id = ?
   ```

## Future Enhancements

1. **Audit Trail**: Track who made changes when
2. **Report Status**: Add status field (draft, submitted, reviewed)
3. **Attachments**: Support file attachments to reports
4. **Notifications**: Email/in-app notifications for new reports
5. **Report Templates**: Predefined templates for different report types
6. **Bulk Operations**: Import/export functionality
7. **Report Analytics**: Dashboard with submission statistics

## Database Migration Strategy

When implementing with SQLAlchemy:

1. Create migration scripts for table creation
2. Add indexes for performance:
   - Index on users.email
   - Index on users.mentor_id
   - Index on weekly_reports.mentee_id
   - Index on weekly_reports.mentor_id
   - Composite index on (mentee_id, year, week_number)

3. Set up proper foreign key constraints with cascading rules
4. Implement database connection pooling for production

## Testing Considerations

1. **Unit Tests**: Test model validation and constraints
2. **Integration Tests**: Test database operations and relationships
3. **Data Integrity Tests**: Verify foreign key constraints work
4. **Performance Tests**: Test query performance with large datasets

This schema provides a solid foundation for the 1:1 weekly report system with room for future enhancements while maintaining data integrity and security. 