# RegIntelX Backend

Backend API service for RegIntelX — Regulatory Intelligence Platform.

## Tech Stack

- FastAPI
- MongoDB
- PyMongo
- Python

## Features

- Circular management APIs
- Task management APIs
- User management APIs
- Compliance proof submission
- Department-wise task analytics
- REST API integration support

## Project Structure

```text
RegIntelX-backend/
│
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### Clone repository

```bash
git clone <repository-url>
```

### Go to project folder

```bash
cd RegIntelX-backend
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create `.env` file

```env
MONGO_URI=your_mongodb_connection_string
```

## Run Server

```bash
uvicorn main:app --reload
```

## API Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

## Main APIs

### Circulars

```text
POST   /circulars
GET    /circulars
GET    /circulars/{id}
PUT    /circulars/{id}
DELETE /circulars/{id}
GET    /fetch-circulars
```

### Tasks

```text
POST   /tasks
GET    /tasks
GET    /tasks/{id}
PUT    /tasks/{id}
PATCH  /tasks/{id}/status
DELETE /tasks/{id}
```

### Users

```text
POST   /users
GET    /users
DELETE /users/{id}
```

### Analytics

```text
GET /generate-maps
```

### Compliance

```text
POST /validate-proof
```

## Database Collections

- circulars
- tasks
- users

## Team

RegIntelX Development Team
