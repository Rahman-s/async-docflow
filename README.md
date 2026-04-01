# 🚀 Async Document Processing System

A full-stack async workflow system for uploading, processing, reviewing, and exporting documents.

---

## 🧠 Project Overview

This project demonstrates how to build a scalable asynchronous processing system using modern backend and frontend technologies.

Users can:
- 📤 Upload documents
- 🔄 Track real-time processing status
- 🧠 Process documents asynchronously using Celery
- ✏️ Review and edit extracted data
- ✅ Finalize documents
- 📊 Export results as JSON or CSV

---

## 🏗️ Architecture

Frontend (Next.js)  
⬇  
FastAPI Backend  
⬇  
Celery Worker (Async Processing)  
⬇  
Redis (Message Broker)  
⬇  
PostgreSQL (Database)

---

## 🛠️ Tech Stack

### 🔹 Backend
- FastAPI
- PostgreSQL
- Celery
- Redis

### 🔹 Frontend
- Next.js (App Router)
- TypeScript
- Tailwind CSS
- Axios

---

## ⚙️ Setup Instructions

### 1️⃣ Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

2️⃣ Start Redis
cd C:\Resume\Redis-x64-5.0.14.1
redis-server.exe
3️⃣ Start FastAPI Server
cd backend
uvicorn app.main:app --reload

4️⃣ Start Celery Worker
cd backend
celery -A celery_app:celery worker --loglevel=info -P solo -Q documents

💻 Frontend Setup
cd frontend
npm install
npm run dev

Open browser:

http://localhost:3000

🔄 Workflow
User uploads a document
Document status = queued
Celery worker processes document → processing
Extraction complete → completed
User reviews & edits data
User finalizes document
Export data (JSON / CSV)

📡 API Endpoints
Method	Endpoint
POST	/documents/upload
GET	/documents
GET	/documents/{id}
PUT	/documents/{id}/review
PUT	/documents/{id}/finalize
POST	/documents/{id}/retry
GET	/export/json
GET	/export/csv

🧪 Assumptions
Processing is simulated (no real AI extraction)
Only basic file handling
Single-user system

⚠️ Limitations
No authentication system
No file validation (PDF/image handling limited)
No cloud deployment

Basic UI (no advanced UX)
🔮 Future Improvements
🔐 Add authentication (JWT)
🤖 Integrate AI/NLP for real extraction
📄 Add PDF/image preview
☁️ Deploy on cloud (AWS/Render)
📊 Analytics dashboard
🎥 Demo

This project demonstrates:

File upload
Async processing (Celery + Redis)
Real-time status updates
Review & finalize workflow
Export functionality
👨‍💻 Author

Mohd Rahman
B.Tech ECE (PSIT)
Aspiring Software Developer 🚀

⭐ Key Highlights
Async processing using Celery
Real-time UI updates
Full-stack integration
Clean architecture design