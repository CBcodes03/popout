# 🌟 PopOut - Real-Time Local Connections Platform

![PopOut Banner](https://user-images.githubusercontent.com/your-username/popout-banner.png)  
*Connecting you instantly with nearby people for spontaneous meetups*

---

## 📋 Overview

**PopOut** is a **location-based social networking platform** that enables users to discover and join **real-time local meetups**. Whether it’s coffee, study sessions, walks, or any activity nearby, PopOut connects you instantly with people around you.

> 💬 Real connections. ⚡ Real-time. 📍 Local.

---

## 🎯 Problem Statement

In today’s digital world, finding spontaneous local connections is difficult:

- ❌ **Lack of Spontaneity** – Advance planning is often required  
- ❌ **Geographic Barriers** – Hard to discover people nearby  
- ❌ **Notification Overload** – Users must constantly check apps  
- ❌ **Meaningless Connections** – Random online chats rarely translate to real meetups  
- ❌ **Time-Consuming Discovery** – Finding events or people takes effort  

---

## 🚀 Objectives

PopOut aims to:

- ⚡ Enable **instant local connections**  
- 📍 Leverage **real-time location intelligence**  
- 🤝 Facilitate **spontaneous meetups**  
- 🔔 Provide **real-time notifications**  
- ❤️ Promote **meaningful interactions**  

---

## 🛠️ Architecture & Methodologies

### Backend
- **Django 5.2.8** + **Django REST Framework 3.14+**  
- **JWT Authentication** (`djangorestframework-simplejwt`)  
- **Geopy 2.4.1** for location calculations  
- **Real-Time Notifications** via in-app system  
- **SQLite / PostgreSQL** with optimized queries  

### Frontend
- **HTML5, CSS3, JavaScript (ES6+)**  
- **Tailwind CSS** for responsive design  
- **Google Fonts (Inter)**  
- **Browser Geolocation API**  
- Dynamic forms & **toast notifications**  

### Matching Algorithm
- Distance-based filtering of events  
- Time-based relevance & join expiry  
- Smart filtering: exclude user's own events  
- Participant management for optimized group sizes  

---

## ✨ Unique Selling Points

| Feature | Description |
|---------|-------------|
| 🕐 **Real-Time Connections** | Instantly find nearby companions |
| 📍 **Location-Based Smart Matching** | Events displayed based on your current location |
| 🔔 **Instant Engagement** | Notifications sent immediately to nearby users |

---

## 💻 Tech Stack

### Backend
- Django, DRF, JWT  
- Geopy, Pillow, psycopg2-binary  
- CORS: `django-cors-headers`  
- Static files: `WhiteNoise`  

### Frontend
- HTML, CSS, JS, Tailwind CSS  
- Google Fonts, Geolocation API  

### Authentication
- JWT, Google OAuth2, Email OTP  

### Database
- SQLite (development), PostgreSQL (production)  

---

## 🔄 Workflow

### User Registration
1. Email & password registration  
2. OTP verification  
3. JWT session creation  
4. Optional Google OAuth sign-in  

### Event Creation
1. Update location (latitude & longitude)  
2. Create event: title, description, coordinates, time, max participants  
3. Chat group auto-created for the event  
4. Event becomes visible to nearby users  

### Event Discovery
1. Find nearby events using geodesic distance  
2. Filter by distance, time, and availability  
3. Request to join event  
4. Organizer approves/rejects  
5. Accepted users auto-added to chat  

### Notifications & Chat
- Real-time notifications for events & join requests  
- Event chat auto-created with members  
- Messages stored with timestamps  

---

## 📊 Achievements

- ✅ Real-time location matching  
- ✅ Instant notifications  
- ✅ Secure authentication (JWT & OAuth)  
- ✅ Scalable REST API architecture  
- ✅ Responsive UI with modern design  
- ✅ Complete event lifecycle & chat integration  

---

## 🔮 Future Scope

### Chat Features
- WebSockets for real-time messaging  
- Media sharing, read receipts, typing indicators  

### Advanced Features
- Push notifications, AI recommendations, event ratings  
- Recurring events, social features, analytics dashboard  

### Technical Improvements
- Redis caching, Celery async tasks, API rate limiting  
- Native iOS & Android apps, Progressive Web App (PWA)  

---

## 📝 Installation & Setup

### Prerequisites
- Python 3.8+, pip, virtual environment  

### Steps
```bash
git clone <repo-url>
cd popout
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver
