from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_active_user
from app.services.ai_assistant import AIAssistantService
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/ai", tags=["ai"])


class AIChatRequest(BaseModel):
    message: str


class AIChatResponse(BaseModel):
    response: str
    suggested_queries: List[str]


from app.services.license_manager import LicenseManager

@router.post("/chat", response_model=AIChatResponse)
def chat_with_ai_assistant(
    payload: AIChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Interactive Chat API endpoint with the AI Network Assistant (Copilot) in Bulgarian.
    """
    if not LicenseManager.check_feature_allowed("ai_assistant"):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Модулът 'AI Асистент' изисква активен търговски лиценз за LANi-Platform. Моля, инсталирайте или подновете Вашата лицензна подписка."
        )
    try:
        result = AIAssistantService.process_chat_message(db, current_user.id, payload.message)
        return {
            "response": result["response"],
            "suggested_queries": result["suggested_queries"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Грешка при обработка на съобщението от AI: {str(e)}"
        )


@router.get("/suggestions", response_model=List[str])
def get_ai_suggestions(
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns suggested queries for the AI Assistant interface.
    """
    return AIAssistantService.get_suggested_queries()
