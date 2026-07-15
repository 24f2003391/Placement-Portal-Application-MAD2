# 🎓 Placement Portal Application

A full-stack Placement Portal Application developed as part of the **Modern Application Development II (MAD-II)** course.

The application streamlines the campus placement process by providing a common platform for **Administrators**, **Companies**, and **Students**. It supports placement drive management, student applications, interview scheduling, offer management, asynchronous background jobs, email notifications, and caching.

---

# 🚀 Features

## 👨‍💼 Admin

- Login using a pre-created administrator account
- Approve or reject company registrations
- Approve or reject placement drives
- View all registered students and companies
- Blacklist or unblacklist students
- Blacklist or unblacklist companies
- View applications for placement drives
- Monitor placement statistics through the dashboard

---

## 🏢 Company

- Register company profile
- Create placement drives
- Define eligibility criteria
- View created drives
- View student applications
- Shortlist or reject applicants
- Schedule interviews
- Cancel or complete interviews
- Generate placement offers
- Export applications as CSV

---

## 🎓 Student

- Register and login
- Update profile details
- Browse approved placement drives
- Search placement drives
- Apply to eligible placement drives
- Upload resume while applying
- Track application status
- View scheduled interviews
- Accept or reject placement offers
- Download offer letters
- View placement history

---

# ⏰ Background Jobs

The application uses **Celery** for asynchronous and scheduled tasks.

### Daily Reminder

- Sends reminder emails to students regarding upcoming application deadlines.

### Monthly Activity Report

- Generates a monthly placement report.
- Sends the report to the administrator via email.

### CSV Export

- Companies can export application details as a CSV file.
- Export is handled asynchronously using Celery.

---

# ⚡ Caching

Redis is used for caching frequently accessed data to improve API response time.

---

# 🛠 Technology Stack

## Backend

- Flask
- Flask-RESTful
- Flask-Security-Too
- Flask-SQLAlchemy
- Flask-Mail
- Flask-Caching
- Celery
- Redis
- SQLite

## Frontend

- Vue 3
- Vue Router
- Pinia
- Bootstrap 5
  

---

# 📁 Project Structure

```text
Placement-Portal-Application
│
├── backend
│   ├── app.py
│   ├── celery_app.py
│   ├── requirements.txt
│   │
│   ├── controller
│   │   ├── admin_api.py
│   │   ├── auth_helpers_api.py
│   │   ├── company_api.py
│   │   ├── student_api.py
│   │   ├── models.py
│   │   ├── datastore.py
│   │   ├── config.py
│   │   └── extensions.py
│   │
│   ├── templates
│   │   ├── daily_reminder.html
│   │   └── monthly_report_admin.html
│   │
│   └── instance
│       ├── exports
│       └── uploads
│
├── frontend
│   ├── public
│   ├── src
│   │   ├── components
│   │   ├── router
│   │   ├── stores
│   │   └── views
│   │
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

# ⚙️ Installation

## Prerequisites

Install the following before running the project.

- Python 3.x
- Node.js and npm
- Redis
- Mailpit
- Git

---

## Clone the Repository

```bash
git clone <repository-url>
cd Placement-Portal-Application
```

---

# Backend Setup

Move into the backend folder.

```bash
cd backend
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate it.

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

---

# Frontend Setup

Open a new terminal.

```bash
cd frontend
```

Install frontend dependencies.

```bash
npm install
```

---

# Running the Application

The project requires multiple services running simultaneously.

## Terminal 1 – Redis Server

```bash
redis-server
```

---

## Terminal 2 – Mailpit

```bash
mailpit
```

---

## Terminal 3 – Celery Worker

```bash
cd backend

celery -A celery_app.celery worker --loglevel=info
```

---

## Terminal 4 – Celery Beat

```bash
cd backend

celery -A celery_app.celery beat --loglevel=info
```

---

## Terminal 5 – Flask Backend

```bash
cd backend

python app.py
```

---

## Terminal 6 – Vue Frontend

```bash
cd frontend

npm run dev
```

---

# Access the Application

Frontend

```
http://localhost:5173
```

Backend API

```
http://localhost:5000
```

Mailpit Dashboard

```
http://localhost:8025
```

---

# Database

- SQLite is used as the database.
- The database is created programmatically by the application.
- No manual database creation is required.

