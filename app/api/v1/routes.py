from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.deps import get_config
from app.core.config import Settings
from app.schemas.debate import DebateRequest, DebateResponse
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/v1", tags=["debate"])


def get_llm_service(settings: Settings = Depends(get_config)) -> LLMService:
    """Dependency to get LLM service instance."""
    return LLMService(settings)


@router.post(
    "/debate",
    response_model=DebateResponse,
    status_code=status.HTTP_200_OK,
    summary="Debate an argument",
    description="Submit an argument or claim to receive a logical debate response"
)
async def debate(
    request: DebateRequest,
    llm_service: LLMService = Depends(get_llm_service),
    settings: Settings = Depends(get_config)
) -> DebateResponse:
    """Debate endpoint that processes arguments using the LLM."""
    try:
        response_text = await llm_service.generate_response(request.message)
        return DebateResponse(
            response=response_text,
            model=settings.llm_model
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )

