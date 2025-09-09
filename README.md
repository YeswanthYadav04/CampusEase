# 🎓 Campus Bot - University Chatbot



A comprehensive multilingual AI-powered campus assistant built with *Django* that serves as a one-stop solution for students' academic needs.



[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)

[![Django](https://img.shields.io/badge/django-5.0-green.svg)](https://djangoproject.com)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)



## 🌟 Overview



Campus Bot revolutionizes the student experience by providing instant access to academic information through an intelligent chatbot interface. Whether you need your class schedule, want to download course materials, or have questions about recent college announcements, Campus Bot has you covered.



## ✨ Key Features



### 📚 *Academic Management*

- *📅 Timetables & Academic Calendar* - Get your personalized class schedules and important academic dates

- *🏫 Attendance Tracking* - Check attendance records and schedule queries

- *📑 Document Retrieval* - Access PDFs, PowerPoint presentations, notes, and assignments



### 🤖 *Intelligent Assistance*

- *📢 Circular Extraction* - Automatically processes uploaded college circulars and provides instant answers

- *🧑‍🏫 Faculty Directory* - Complete faculty information with contact details

- *🔍 Smart Query Processing* - Advanced natural language understanding for accurate responses



### 🌐 *Multilingual Support*

- *English* - Primary language support

- *हिन्दी (Hindi)* - Native Hindi language support

- *ગુજરાતી (Gujarati)* - Regional language integration



## 🛠 Technology Stack



| Category | Technologies |

|----------|-------------|

| *Backend Framework* | Django 5, Django REST Framework |

| *Language Processing* | Googletrans, Langdetect, Scikit-learn |

| *Database* | SQLite (development), PostgreSQL/MySQL (production ready) |

| *Document Processing* | PyPDF2, python-pptx |

| *Testing & Async* | Pytest, Trio |

| *NLP & Matching* | Fuzzy string matching, TF-IDF similarity |



## 📋 Prerequisites



- *Python 3.12* (Required - Python 3.13 not supported due to library compatibility)

- *pip* (Python package manager)

- *Git* (for version control)



⚠ *Important*: This project requires Python 3.12 specifically due to dependency compatibility issues with newer Python versions.



## 🚀 Installation & Setup



### 1️⃣ Clone the Repository

bash

git clone https://github.com/KoranneVaidehi/campus-bot.git

cd campus-bot





### 2️⃣ Create Virtual Environment

bash

# Windows

py -3.12 -m venv chatbot_env_312

chatbot_env_312\Scripts\activate



# macOS/Linux

python3.12 -m venv chatbot_env_312

source chatbot_env_312/bin/activate





### 3️⃣ Install Dependencies

bash

pip install -r requirements.txt





### 4️⃣ Database Setup

bash

py manage.py makemigrations

py manage.py migrate





### 5️⃣ Create Superuser (Optional)

bash

py manage.py createsuperuser





### 6️⃣ Run Development Server

bash

py manage.py runserver





The application will be available at http://localhost:8000



## 📂 Project Structure





university_chatbot/

├── 📁 chatbot/                 # Main chatbot application

│   ├── 📄 models.py           # Database models & schemas

│   ├── 📄 views.py            # API views & business logic

│   ├── 📄 utils.py            # NLP utilities & language processing

│   ├── 📄 urls.py             # URL routing configuration

│   ├── 📁 migrations/         # Database migration files

│   └── 📁 templates/          # HTML templates

├── 📁 university_chatbot/     # Project configuration

│   ├── 📄 settings.py         # Django settings

│   ├── 📄 urls.py             # Main URL configuration

│   └── 📄 wsgi.py             # WSGI configuration

├── 📁 static/                 # Static files (CSS, JS, images)

├── 📁 media/                  # User uploaded files

├── 📄 requirements.txt        # Python dependencies

├── 📄 manage.py              # Django management script

└── 📄 README.md              # Project documentation





## 🔧 Configuration



### Environment Variables

Create a .env file in the root directory:



env

SECRET_KEY=your-secret-key-here

DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=SQLite:///db.sqlite3





### Database Configuration

For production, update your database settings in settings.py:



python

DATABASES = {

    'default': {

        'ENGINE': 'Django.db.backends.postgresql',

        'NAME': 'campus_bot_db',

        'USER': 'your_username',

        'PASSWORD': 'your_password',

        'HOST': 'localhost',

        'PORT': '5432',

    }

}





## 🔌 API Endpoints



| Endpoint | Method | Description |

|----------|--------|-------------|

| /api/chat/ | POST | Main chatbot interaction |

| /api/documents/ | GET | Retrieve available documents |

| /api/faculty/ | GET | Get faculty information |

| /api/timetable/ | GET | Access timetable data |

| /api/circulars/ | GET | Fetch recent circulars |



## 💡 Usage Examples



### Basic Chat Interaction

python

import requests



response = requests.post('http://localhost:8000/api/chat/', {

    'message': 'What is my timetable for today?',

    'language': 'en'

})





### Document Search

python

response = requests.get('http://localhost:8000/api/documents/', {

    'query': 'machine learning notes',

    'subject': 'CS'

})





## 🧪 Testing



Run the test suite:

bash

pytest





Run with coverage:

bash

pytest --cov=chatbot







## 🎯 Roadmap



- [ ] *Mobile Application* - React Native/Flutter app

- [ ] *Advanced NLP* - Integration with LLMs for better understanding

- [ ] *Voice Interface* - Speech-to-text and text-to-speech capabilities

- [ ] *Analytics Dashboard* - Usage statistics and insights

- [ ] *Integration APIs* - Connect with LMS and other campus systems

- [ ] *Push Notifications* - Real-time updates and alerts



## 🐛 Known Issues



- Python 3.13 compatibility pending library updates

- Large PDF processing may timeout on slower systems

- Translation accuracy varies for technical terms




