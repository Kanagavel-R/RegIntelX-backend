# ============================================================
# RegIntelX — Member 2: Backend API (FastAPI + MongoDB)
# ============================================================

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, List
from datetime import datetime
import os
from dotenv import load_dotenv

# ─────────────────────────────────────────
# Load Environment Variables
# ─────────────────────────────────────────
load_dotenv()
MONGO_URI = os.getenv(MONGO_KEY)

# ─────────────────────────────────────────
# MongoDB Connection
# ─────────────────────────────────────────
client = MongoClient(MONGO_URI)
db = client["regintelx"]
circulars_collection = db["circulars"]
tasks_collection     = db["tasks"]
users_collection     = db["users"]

# ─────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────
app = FastAPI(
    title="RegIntelX Backend API",
    version="1.0.0",
    description="Regulatory Intelligence Platform — Backend APIs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# Helper: Convert ObjectId → string
# ─────────────────────────────────────────
def serialize(doc) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# ─────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────

class Circular(BaseModel):
    title: str
    issuer: str
    date: str
    content: str
    severity: str
    department: str
    summary: Optional[str] = None
    tags: Optional[List[str]] = []

class Task(BaseModel):
    title: str
    department: str
    assigned_to: Optional[str] = None
    circular_id: Optional[str] = None
    deadline: Optional[str] = None
    severity: Optional[str] = "MEDIUM"
    status: str = "PENDING"

class TaskStatusUpdate(BaseModel):
    status: str

class User(BaseModel):
    name: str
    email: str
    role: str
    department: Optional[str] = None


# ═══════════════════════════════════════════
# ROOT
# ═══════════════════════════════════════════

@app.get("/", tags=["Root"])
def home():
    return {
        "message": "RegIntelX Backend is Running ✅",
        "version": "1.0.0"
    }


# ═══════════════════════════════════════════
# CIRCULAR APIs
# ═══════════════════════════════════════════

@app.post("/circulars", status_code=201, tags=["Circulars"])
def add_circular(circular: Circular):
    data = circular.model_dump()
    data["created_at"] = datetime.utcnow().isoformat()
    result = circulars_collection.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return {"message": "Circular added successfully", "data": data}


@app.get("/circulars", tags=["Circulars"])
def get_all_circulars():
    circulars = [serialize(doc) for doc in circulars_collection.find()]
    return {"count": len(circulars), "data": circulars}


@app.get("/circulars/{circular_id}", tags=["Circulars"])
def get_circular(circular_id: str):
    try:
        obj_id = ObjectId(circular_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid circular ID format")

    doc = circulars_collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Circular not found")
    return serialize(doc)


@app.put("/circulars/{circular_id}", tags=["Circulars"])
def update_circular(circular_id: str, updated: Circular):
    try:
        obj_id = ObjectId(circular_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid circular ID format")

    result = circulars_collection.update_one(
        {"_id": obj_id},
        {"$set": updated.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Circular not found")
    return {"message": "Circular updated successfully"}


@app.delete("/circulars/{circular_id}", tags=["Circulars"])
def delete_circular(circular_id: str):
    try:
        obj_id = ObjectId(circular_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid circular ID format")

    result = circulars_collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Circular not found")
    return {"message": "Circular deleted successfully"}


@app.get("/fetch-circulars", tags=["Circulars"])
def fetch_circulars_by_filter(issuer: str = None, severity: str = None):
    query = {}
    if issuer:
        query["issuer"] = issuer.upper()
    if severity:
        query["severity"] = severity.upper()
    circulars = [serialize(doc) for doc in circulars_collection.find(query)]
    return {"count": len(circulars), "data": circulars}


# ═══════════════════════════════════════════
# TASK APIs
# ═══════════════════════════════════════════

@app.post("/tasks", status_code=201, tags=["Tasks"])
def add_task(task: Task):
    data = task.model_dump()
    data["created_at"] = datetime.utcnow().isoformat()
    result = tasks_collection.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return {"message": "Task added successfully", "data": data}


@app.get("/tasks", tags=["Tasks"])
def get_all_tasks():
    tasks = [serialize(doc) for doc in tasks_collection.find()]
    return {"count": len(tasks), "data": tasks}


@app.get("/tasks/{task_id}", tags=["Tasks"])
def get_task(task_id: str):
    try:
        obj_id = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    doc = tasks_collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Task not found")
    return serialize(doc)


@app.put("/tasks/{task_id}", tags=["Tasks"])
def update_task(task_id: str, updated_task: Task):
    try:
        obj_id = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    result = tasks_collection.update_one(
        {"_id": obj_id},
        {"$set": updated_task.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated successfully"}


@app.patch("/tasks/{task_id}/status", tags=["Tasks"])
def update_task_status(task_id: str, status_update: TaskStatusUpdate):
    valid_statuses = ["PENDING", "IN_PROGRESS", "COMPLETED"]
    if status_update.status.upper() not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Choose from: {valid_statuses}"
        )
    try:
        obj_id = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    result = tasks_collection.update_one(
        {"_id": obj_id},
        {"$set": {"status": status_update.status.upper()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": f"Task status updated to {status_update.status.upper()}"}


@app.delete("/tasks/{task_id}", tags=["Tasks"])
def delete_task(task_id: str):
    try:
        obj_id = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    result = tasks_collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


# ═══════════════════════════════════════════
# USER APIs
# ═══════════════════════════════════════════

@app.post("/users", status_code=201, tags=["Users"])
def add_user(user: User):
    existing = users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    data = user.model_dump()
    data["created_at"] = datetime.utcnow().isoformat()
    result = users_collection.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return {"message": "User created successfully", "data": data}


@app.get("/users", tags=["Users"])
def get_all_users():
    users = [serialize(doc) for doc in users_collection.find()]
    return {"count": len(users), "data": users}


@app.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = users_collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


# ═══════════════════════════════════════════
# MAP + VALIDATE PROOF APIs
# ═══════════════════════════════════════════

@app.get("/generate-maps", tags=["MAP"])
def generate_maps():
    pipeline = [
        {
            "$group": {
                "_id": "$department",
                "total_tasks": {"$sum": 1},
                "pending":     {"$sum": {"$cond": [{"$eq": ["$status", "PENDING"]}, 1, 0]}},
                "in_progress": {"$sum": {"$cond": [{"$eq": ["$status", "IN_PROGRESS"]}, 1, 0]}},
                "completed":   {"$sum": {"$cond": [{"$eq": ["$status", "COMPLETED"]}, 1, 0]}}
            }
        }
    ]
    result = list(tasks_collection.aggregate(pipeline))
    return {"map_data": result}


@app.post("/validate-proof", tags=["Compliance"])
def validate_proof(task_id: str, proof_url: str):
    try:
        obj_id = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    result = tasks_collection.update_one(
        {"_id": obj_id},
        {"$set": {
            "proof_url": proof_url,
            "proof_submitted_at": datetime.utcnow().isoformat(),
            "status": "IN_PROGRESS"
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "message": "Proof submitted. Awaiting AI validation from Member 3.",
        "task_id": task_id,
        "proof_url": proof_url
    }