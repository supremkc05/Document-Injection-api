from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest, ChatResponse
from app.services.rag_service import rag_service

router = APIRouter(prefix="/api", tags=["Conversational RAG"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversational RAG endpoint with multi-turn support
    
    - **session_id**: Unique session identifier for maintaining conversation context
    - **user_message**: The user's message/question
    
    Returns:
    - **session_id**: The session ID
    - **response**: AI-generated response
    - **sources**: List of source document IDs used for the response
    """
    try:
        # Validate input
        if not request.session_id or not request.session_id.strip():
            raise HTTPException(
                status_code=400,
                detail="session_id is required"
            )
        
        if not request.user_message or not request.user_message.strip():
            raise HTTPException(
                status_code=400,
                detail="user_message is required"
            )

        # Process chat message with RAG
        response_text, sources = await rag_service.chat(
            session_id=request.session_id,
            user_message=request.user_message
        )

        return ChatResponse(
            session_id=request.session_id,
            response=response_text,
            sources=sources if sources else None
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )


@router.delete("/chat/{session_id}")
async def clear_session(session_id: str):
    """
    Clear conversation history for a session
    
    - **session_id**: Session identifier to clear
    """
    try:
        success = rag_service.clear_session(session_id)
        
        if success:
            return {"status": "success", "message": f"Session {session_id} cleared"}
        else:
            return {"status": "info", "message": f"Session {session_id} not found or already cleared"}
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing session: {str(e)}"
        )


@router.get("/chat/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get conversation history for a session
    
    - **session_id**: Session identifier
    """
    try:
        history = rag_service.get_session_history(session_id)
        return {
            "session_id": session_id,
            "history": history,
            "message_count": len(history)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session history: {str(e)}"
        )
