# Certificate Report Generator

## Overview

The Certificate Report Generator is a Flask-based web application that allows users to manage student enrollments, generate certificates, and update details. The system provides a user-friendly interface for easy navigation and seamless student management.

**Features**

- Enroll students into courses
- Generate course completion certificates
- Update student details
- View student records
- User authentication for admin login

## Technologies Used
- Python (Flask)
- SQLite (Database)
- HTML, CSS (Frontend)
- Docker & Docker Compose (Containerization)
- AWS (If deploying on AWS)

## Installation & Setup

### Prerequisites:
- Install **Python 3.10+**
- Install **Docker & Docker Compose** (for deployment)

### Steps to Run Locally:
1. Clone the repository:
   ```bash
   git clone https://github.com/hema1304/Certificate-Report-Generator.git
   cd Certificate-Report-Generator
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   flask run
   ```

### Running with Docker:
```bash
docker-compose up --build -d
