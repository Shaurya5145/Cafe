# ☕ Cafe Finder Website

The **Cafe Finder** is a web application built to help users discover and bookmark cafes with ease. Designed with a simple and intuitive interface, this platform allows users to explore cafes, view details, and manage their favorite spots.

---

## 🚀 Features

- 🔍 **Search Cafes** – Find cafes by name or location.
- 📌 **Bookmark Cafes** – Logged-in users can save cafes they like.
- 🔐 **User Authentication** – Secure login and registration.
- 📝 **Add Your Cafe** – Owners can list new cafes.
- 📍 **Google Maps Integration** – View cafe locations on the map.

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, Bootstrap (or Tailwind)
- **Backend**: Python, Flask
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Deployment**: (e.g. Render / Heroku / Azure VM)

---

## 📂 Project Structure

cafe_finder/
│
├── static/ # CSS, images
├── templates/ # HTML templates (Jinja2)
├── app.py # Main Flask app
├── models.py # SQLAlchemy models
├── forms.py # Flask-WTF forms
├── config.py # Configuration settings
└── requirements.txt # Python dependencies

## ✅ Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/cafe-finder.git
   cd cafe-finder
Create a virtual environment

python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
Install dependencies

pip install -r requirements.txt
Set up environment variables

FLASK_APP=app.py

FLASK_ENV=development

SECRET_KEY=your_secret_key

Run the app

bash
Copy
Edit
flask run
