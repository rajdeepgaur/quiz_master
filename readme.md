-- Quiz Master --
A dynamic Flask-based application for managing quizzes, tracking student progress, and providing a comprehensive exam preparation platform.

Features

For Administrators
1. Create and manage subjects and chapters with detailed descriptions
2. Design quizzes with multiple-choice questions
3. Set quiz duration and availability dates (with clear UTC time indicators)
4. View students and their quiz attempts
5. Search functionality for subjects, chapters, and quizzes
6. Dedicated interface for student user management

For Students
1. Access organized quizzes by subject and chapter
2. Take timed quizzes with proper countdown timer
3. Unlimited access to past quizzes for practice (no date restrictions)
4. View personal progress:
(a)Recent quiz attempts with scores
(b) Detailed performance analysis by subject
(c)Comprehensive attempt history with timestamps

Technology Stack
1. Backend: Flask + SQLAlchemy
2. Database: PostgreSQL (with compatibility for SQLite)
3. Frontend:
(a) Bootstrap for responsive UI
(b) JavaScript for interactive forms and timers
4. Authentication: Flask-Login with Werkzeug security
5. Data Validation: SQLAlchemy + Flask-WTF
6. Session Management: Flask-Session

Setup
Environment Variables

DATABASE_URL=your_sqlite_database_url
SESSION_SECRET=your_session_secret

Activate the Environment
python -m venv venv
source venv/bin/activate

Install Dependencies
pip install -r requirements.txt
Database Setup

The application will automatically create necessary tables on first run
First registered user becomes the administrator

Run the Application
python main.py

The application will be available at http://localhost:5000

Usage Guide
Administrator Actions
1. Subject Management
Navigate to Admin Dashboard
Use "Add Subject" button to create new subjects with descriptions
Add chapters within subjects with detailed descriptions
Edit or delete subjects and chapters as needed

2. Quiz Creation and Management
Select a chapter to manage quizzes
Click "Add Quiz" to create a new quiz
Set quiz parameters:
Title
Duration (in minutes)
Start date and time (with UTC indicator)
End date and time (with UTC indicator)
Add multiple-choice questions with options and correct answers
Edit existing quizzes and questions
Remove quizzes when no longer needed

3. User Management
View list of student users (non-admin accounts)
Monitor student quiz attempts and scores
Search for specific users by username
Track overall system usage

Student Features
1. Taking Quizzes
Browse available quizzes by subject and chapter
Take active quizzes with accurate countdown timer
Access past quizzes for unlimited practice (no date restrictions)
Submit answers before timer expires
View immediate results and correct answers

2. Progress Tracking
Check personal dashboard for recent quiz attempts
View detailed attempt history with timestamps (UTC)
Filter quiz attempts by subject or date
Review performance across different subjects
Search for specific quizzes

Security Features
1. Password hashing using Werkzeug's secure generation and verification functions
2. Session management with Flask-Login for persistent user sessions
3. Role-based access control (admin vs. student users)
4. Secure validation of user inputs to prevent injection attacks
5. UTC time indicators for all date-time values to prevent timezone confusion

Time Handling
1. All datetime values stored in UTC format
2. Explicit UTC indicators on displayed timestamps
3. Consistent timestamp comparisons for quiz availability
4. Accurate countdown timer for quiz duration
5. Unlimited access to past quizzes for practice after end date