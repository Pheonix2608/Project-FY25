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
    """Represents a chat message sent by a user.

    Attributes:
        message (str): The content of the user's message.
    """
    message: str

class ChatResponse(BaseModel):
    """Represents a chat response sent by the chatbot.

    Attributes:
        user_id (str): The user ID associated with the request.
        response (str): The chatbot's textual response.
        intent (str): The intent predicted by the model.
        confidence (float): The confidence score of the prediction.
    """
    user_id: str
    response: str
    intent: str
    confidence: float

async def get_api_key(x_api_key: str = Header(...)):
    """A FastAPI dependency to verify the API key from the request header.

    Args:
        x_api_key (str): The API key passed in the `X-API-Key` header.

    Raises:
        HTTPException: If the chatbot application is not initialized (503),
            or if the API key is invalid or expired (401).

    Returns:
        str: The user ID associated with the valid API key.
    """
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
    """The main endpoint for interacting with the chatbot.

    This endpoint requires a valid API key for authentication. It receives a
    user's message, processes it through the chatbot application, logs the
    interaction, and returns the chatbot's response.

    Args:
        message (ChatMessage): The user's message.
        user_id (str): The user ID, injected by the `get_api_key` dependency.
        x_api_key (str): The API key from the header, used for logging.

    Returns:
        ChatResponse: The chatbot's response, including the intent and
            confidence score.
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
    """Sets the global chatbot application instance for the API to use.

    This function is called from the main application thread during startup
    to inject the central `ChatbotApp` instance into the API module, making
    it accessible to the endpoint handlers.

    Args:
        app_instance (ChatbotApp): The instance of the main chatbot application.
    """
    global chatbot_app
    chatbot_app = app_instance