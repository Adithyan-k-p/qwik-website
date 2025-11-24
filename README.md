# 🌟 Qwik – Ephemeral Social Media Web Platform

**Qwik** is a responsive web application built with a modern Django REST API backend and a lightweight HTML/CSS/JavaScript frontend. It empowers users to share spontaneous moments — photos, videos, or status updates — that automatically disappear after 24 hours. Qwik prioritizes **authenticity**, **privacy**, and **real-time interaction**.

📄 For detailed requirements, see [docs/PRD.md](docs/PRD.md)  
📦 For MVP scope, check [docs/MVP.md](docs/MVP.md)

---

## 🚀 Key Features

- 📸 **Ephemeral Posts**: Share “Blinks” that vanish after 24 hours.
- 🎭 **Mood & Moment Tags**: Add emotional context to your posts.
- 💬 **Real-Time Chat**: One-to-one messaging with seen status and typing indicators (via WebSockets).
- 😍 **Reactions & Comments**: Express yourself with emojis and comments.
- 🔔 **Smart Notifications**: Get notified only when it matters.
- 🔐 **Privacy Controls**: Choose your audience — public, friends, or close circle.
- 🛡️ **Admin Panel**: Moderate content, manage users, and view reports.

---

## 🧱 Tech Stack

| Layer         | Technology                        |
|---------------|-----------------------------------|
| Frontend      | **HTML, CSS, and Vanilla JavaScript**|
| Backend       | Django + Django REST Framework    |
| Database      | PostgreSQL                        |
| Real-Time     | Django Channels + Redis           |
| Media Storage | Cloudinary / AWS S3 / Supabase    |
| Authentication| JWT (SimpleJWT)                   |
| Notifications | WebSockets (In-App)               |

---

## 📁 Project Structure

```text
qwik/
├── backend/       # Django backend with REST APIs and real-time features
├── frontend/      # **Standard HTML, CSS, and JavaScript files**
├── docs/          # Documentation: PRD, MVP, and architecture details
└── README.md      # This file
```

🛠️ Getting Started
🔧 Backend Setup (Django)
Navigate to the backend directory:

Bash

cd backend/
Create and activate a virtual environment:

Bash

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
Install dependencies:

Bash

pip install -r requirements.txt
(Note: Ensure you have PostgreSQL running and your .env file is configured per the .env-example with Supabase/DB credentials.)

Set up the database:

Bash

python manage.py migrate
Run the development server (for API and WebSockets):

Bash

python manage.py runserver
🌐 Frontend Setup (HTML, CSS, JS)
The frontend consists of static files that communicate with the Django API.

Navigate to the frontend directory:

Bash

cd frontend/
Development: Since this is a static web application, you can open the main HTML files (e.g., index.html, login.html) directly in your browser. Note: Due to browser security restrictions (CORS), complex API calls (especially POST requests and WebSockets) must be tested by serving the files from a local web server (e.g., using a VS Code extension like "Live Server" or a simple Python HTTP server).

API Integration: All logic for fetching data, handling user input, and managing the application state must be written in the linked JavaScript files using fetch and WebSocket APIs. Ensure your JavaScript is configured to send the JWT access token with every authenticated request.

🧪 MVP Scope
✅ JWT-based user authentication

✅ Ephemeral post creation with mood tags

✅ Feed from friends and public posts

✅ Real-time 1-to-1 chat

✅ In-app notifications

✅ Basic admin panel for moderation

📌 Roadmap
[ ] AI-powered feed recommendations

[ ] Group chat functionality

[ ] Voice/video calls

[ ] AR filters and stickers

[ ] PWA (Progressive Web App) support for push notifications

[ ] Advanced analytics dashboard

🤝 Contributing
We welcome contributions! To get started:

Fork the repository

Create a feature branch:

Bash

git checkout -b feature/your-feature
Commit your changes:

Bash

git commit -m "Add your feature"
Push to your branch:

Bash

git push origin feature/your-feature
Open a pull request

For major changes, please open an issue first to discuss your ideas.

📄 License
This project is licensed under the MIT License. See the LICENSE file for details.

✨ Credits
Built with ❤️ by Adithyan