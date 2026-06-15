from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
import uuid

from app.core.database import get_db
from app.services.agent_service import run_agent

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    document_ids: list[str] = []


class SessionCreateRequest(BaseModel):
    document_ids: list[str] = []


@router.post("/session")
async def create_session(req: SessionCreateRequest):
    db = get_db()
    session = {
        "session_id": str(uuid.uuid4()),
        "document_ids": req.document_ids,
        "messages": [],
        "created_at": datetime.utcnow(),
    }
    result = await db.sessions.insert_one(session)
    return {"session_id": session["session_id"], "id": str(result.inserted_id)}


@router.post("/message")
async def send_message(req: ChatRequest):
    db = get_db()

    # Resolve or create session
    session = None
    if req.session_id:
        session = await db.sessions.find_one({"session_id": req.session_id})

    if not session:
        session = {
            "session_id": req.session_id or str(uuid.uuid4()),
            "document_ids": req.document_ids,
            "messages": [],
            "created_at": datetime.utcnow(),
        }
        await db.sessions.insert_one(session)

    # Merge any new document_ids into session
    doc_ids = list(set(session.get("document_ids", []) + req.document_ids))

    # Resolve document paths
    document_paths = []
    for doc_id in doc_ids:
        try:
            doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
            if doc:
                document_paths.append(doc["upload_path"])
        except Exception:
            pass

    # Build history for agent
    history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in session.get("messages", [])
    ]

    # Run agent
    try:
        answer = run_agent(req.message, history, document_paths)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # Persist messages
    user_msg = {"role": "user", "content": req.message, "timestamp": datetime.utcnow()}
    assistant_msg = {"role": "model", "content": answer, "timestamp": datetime.utcnow()}

    await db.sessions.update_one(
        {"session_id": session["session_id"]},
        {
            "$push": {"messages": {"$each": [user_msg, assistant_msg]}},
            "$set": {"document_ids": doc_ids},
        },
        upsert=True,
    )

    return {
        "session_id": session["session_id"],
        "answer": answer,
        "role": "assistant",
    }


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    db = get_db()
    session = await db.sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session["id"] = str(session.pop("_id"))
    for msg in session.get("messages", []):
        if "timestamp" in msg:
            msg["timestamp"] = msg["timestamp"].isoformat()
    session["created_at"] = session["created_at"].isoformat()
    return session


@router.get("/sessions")
async def list_sessions():
    db = get_db()
    sessions = []
    async for s in db.sessions.find({}, {"messages": 0}):
        s["id"] = str(s.pop("_id"))
        s["created_at"] = s["created_at"].isoformat()
        sessions.append(s)
    return sessions
