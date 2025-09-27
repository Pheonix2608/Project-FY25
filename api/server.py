# api/server.py

from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import Optional

# This will be set by the main application
chatbot_app = None

app = FastAPI(
    title="Intelligent Chatbot API",
    description="A modern, asynchronous API for the Intelligent Chatbot.",
    version="2.0.0"
)

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    user_id: str
    response: str
    intent: str
    confidence: float

async def get_api_key(x_api_key: str = Header(...)):
    """Dependency to verify the API key."""
    if not chatbot_app:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot application not initialized."
        )

    user_id = chatbot_app.api_key_manager.verify_api_key(x_api_key)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key."
        )
    return user_id

@app.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    user_id: str = Depends(get_api_key),
    x_api_key: str = Header(...)
):
    """
    Main endpoint for interacting with the chatbot.
    """
    if not chatbot_app:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot application not initialized."
        )

    response_data = chatbot_app.process_input(user_id, message.message)

    # Log the API session
    chatbot_app.log_api_session(
        user_id,
        x_api_key,
        message.dict(),
        response_data
    )

    return ChatResponse(
        user_id=user_id,
        response=response_data.get("response"),
        intent=response_data.get("intent"),
        confidence=response_data.get("confidence")
    )

def set_chatbot_app(app_instance):
    """
    Sets the chatbot application instance for the API to use.
    This is called from the main application thread.
    """
    global chatbot_app
    chatbot_app = app_instance