# Document Scanning & Matching System

## Overview
This project is a self-contained document scanning and matching system with a built-in credit system. Each user starts each day with 20 free scans, and additional scans require a credit request that an admin can approve or deny. The system supports user authentication (including password change and password reset), document upload with text matching using a text frequency algorithm, and an analytics dashboard for tracking usage and credit statistics.


## Features

### 1. User Management & Authentication
- **User Registration & Login:** Basic username/password authentication.
- **Password Management:** Users can change their password, and a "Forgot Password" function is provided for password resets.
- **User Roles:** Two roles are supported: Regular Users and Admins.
- **User Profile:** Displays user details including credits, scan history, and credit requests.

### 2. Credit System
- **Daily Free Credits:** Every user starts with 20 free scans per day.
- **Credit Deduction:** Each document scan deducts 1 credit.
- **Credit Requests:** Users can request additional credits if they run out.
- **Admin Approval:** Admins can approve or deny credit requests and manually update credit balances.
- **Automatic Credit Reset:** Credits automatically reset to 20 at midnight using cron jobs.
  - **Cron Command:** `python manage.py crontab add`  
    (Alternatively, set up a system cron job such as `0 0 * * * /path/to/venv/bin/python /path/to/manage.py runcrons`)

### 3. Document Scanning & Matching
- **Document Upload:** Users can upload plain text files for scanning.
- **Text Matching:** The system uses a text frequency algorithm to compare the uploaded document against existing ones and returns similar documents based on common keywords.
- **Bonus (Future Enhancement):** Integration with AI-powered document matching using OpenAI, Gemini, or DeepSeek can be added for improved accuracy.

### 4. Smart Analytics Dashboard
- **Scan Tracking:** Tracks the number of scans per user per day.
- **Topic Identification:** Identifies the most common scanned document topics via text frequency analysis.
- **User Ranking:** Displays top users by scan count and credit usage.
- **Admin Statistics:** Provides detailed credit usage statistics for admins.

### 5. API Endpoints
| Method | Endpoint               | Description                                   |
|--------|------------------------|-----------------------------------------------|
| POST   | `/auth/register`       | User registration                             |
| POST   | `/auth/login`          | User login (session-based)                    |
| POST   | `/auth/logout`         | User logout                                   |
| GET    | `/user/profile`        | Retrieve user profile and current credits     |
| POST   | `/user/request-credits`     | Submit a request for additional credits       |
| POST   | `/user/list-request`     | List all request for additional credits       |
| POST   | `/documets/ScanUpload`                | Upload document for scanning (deducts 1 credit) |
| GET    | `documents/matches/<docId>`     | Get matching documents for a given document   |
| GET    | `/documents/dashboard`     | Retrieve analytics data for admins            |
| POST   | `/change-password`| Change user password                         |
| POST   | `/reset-password`         | Initiate password reset (forgot password)     |

## Tech Stack & Technologies

- **Frontend:** HTML, CSS, and Vanilla JavaScript (no frameworks).
- **Backend:** Django (Python) for business logic and API endpoints.
- **Database:** SQLite (for local storage).
- **File Storage:** Documents are stored locally on the server.
- **Authentication:** Django's built-in authentication system with secure (hashed) password storage.
- **Task Scheduling:** Automatic credit reset is handled using Django-crontab.
- **Document Matching:** A custom text frequency algorithm is used for document matching.
- **Deployment:** Self-contained application running on a local server.

## Installation & Setup

### Prerequisites
- Python 3.x
- pip
- Virtual environment (recommended)

### Steps to Run the Project
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/kishoretocs/Document-matching.git