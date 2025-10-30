# backend_v2/app/services/websocket_manager.py
from fastapi import WebSocket, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import json
import asyncio

from app.models.session import ChatMessage

class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        # A dictionary to hold connections, perhaps grouped by session_id
        # For this simple case, a list is fine.
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """Broadcasts a message to all connected clients."""
        # Create a copy in case the list is modified during iteration
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except Exception:
                # Connection might be closed
                self.disconnect(connection)

async def save_and_broadcast_message(
    db: AsyncIOMotorDatabase,
    session_id: str,
    speaker: str,
    message: str,
    manager: ConnectionManager
):
    """
    Saves a chat message to the session in MongoDB and broadcasts it.
    """
    try:
        session_obj_id = ObjectId(session_id)
    except Exception:
        print(f"Invalid session ID for WebSocket: {session_id}")
        return

    chat_message = ChatMessage(speaker=speaker, message=message)
    
    # Atomically push the new message
    result = await db["assessment_sessions"].update_one(
        {"_id": session_obj_id},
        {"$push": {"interviewer_chat": chat_message.model_dump()}}
    )
    
    if result.matched_count == 0:
        print(f"Warning: WebSocket message for unknown session {session_id}")
        # Don't broadcast if session doesn't exist
        return
    
    # Broadcast the new message to all clients
    await manager.broadcast(chat_message.model_dump_json())


async def get_chatbot_response(prompt: str) -> str:
    """
    Mock "interviewer" chatbot logic.
    """
    await asyncio.sleep(0.3) # Simulate thinking
    prompt = prompt.lower()
    
    if "hello" in prompt or "hi" in prompt:
        return "Hello! I'm here to help if you have any questions about the platform or the process."
    elif "stuck" in prompt or "help" in prompt:
        return "I can't help with the solution, but try using the 'Get a Hint' (LLM) feature if you're stuck on the problem itself."
    elif "thanks" in prompt or "thank you" in prompt:
        return "You're welcome! Good luck."
    else:
        return "I've noted your comment. Please continue with the assessment."

