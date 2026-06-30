# 🤖 AI Resume Analyzer

An intelligent web application that analyzes resumes using Google's Gemini AI and provides professional feedback to help candidates improve their resumes.

![Demo](https://img.shields.io/badge/Demo-Live-green)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Gemini](https://img.shields.io/badge/Gemini-AI-orange)

---

## 🚀 Live Demo 

🔗 **[View Live Application](https://resume-analyzer-9pqr.onrender.com/)**

---

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🔐 Authentication
- **JWT-based authentication** with access and refresh tokens
- Secure user registration and login
- Token refresh mechanism for extended sessions

### 📄 Resume Management
- **Upload PDF resumes** with validation
- **Extract text** from PDF files automatically
- Store uploaded resumes with status tracking
- View all uploaded resumes in a list

### 🤖 AI-Powered Analysis
- **Google Gemini AI integration** for intelligent resume analysis
- Provides feedback on:
  - Professional summary
  - Key skills identification
  - Strengths and weaknesses
  - Areas for improvement
  - Actionable recommendations
  - Overall rating (1-10)

### 🌐 Deployment
- Deployed on **Render** with automatic deployment
- PostgreSQL database support
- Static files served via WhiteNoise
- Production-ready security settings

---

## 🛠️ Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Django** | 5.0.6 | Web framework |
| **Django REST Framework** | 3.15.1 | RESTful API development |
| **Simple JWT** | 5.3.1 | JWT authentication |
| **PyPDF2** | 3.0.1 | PDF parsing |
| **Google GenAI** | Latest | Gemini AI integration |
| **Gunicorn** | 21.2.0 | Production WSGI server |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure |
| **CSS3** | Styling |
| **JavaScript** | API calls and interactivity |
| **Fetch API** | HTTP requests |

### Database & Deployment
| Technology | Purpose |
|------------|---------|
| **SQLite** | Development database |
| **PostgreSQL** | Production database |
| **Render** | Cloud deployment |
| **WhiteNoise** | Static file serving |

---

## 🏗️ Architecture
resume-analyzer/
├── core/
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI configuration
├── accounts/
│   ├── models.py            # Custom User model
│   ├── views.py             # Authentication views
│   ├── serializers.py       # User serializers
│   └── urls.py              # Auth endpoints
├── resumes/
│   ├── models.py            # Resume model
│   ├── views.py             # Resume analysis views
│   ├── serializers.py       # Resume serializers
│   ├── utils.py             # PDF parser
│   ├── gemini_service.py    # Gemini AI integration
│   └── urls.py              # Resume endpoints
├── templates/
│   └── index.html           # Frontend interface
├── media/                   # Uploaded files
├── static/                  # Static files
├── requirements.txt         # Python dependencies
├── build.sh                 # Render build script
├── runtime.txt              # Python version
└── .env.example             # Environment template

---

## 💻 Installation

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/harshvardhan1907-19/resume-analyzer.git
cd resume-analyzer

Step 2: Create Virtual Environment
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies
pip install -r requirements.txt

Step 4: Set Up Environment Variables
Create a .env file in the project root:

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

Step 5: Run Migrations
python manage.py makemigrations
python manage.py migrate

Step 6:
Access the Application
Open your browser and go to: http://localhost:8000/
