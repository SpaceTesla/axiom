from pydantic import BaseModel, Field


class DebateRequest(BaseModel):
    """Request schema for debate endpoint."""
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The argument or claim to be debated"
    )


class DebateResponse(BaseModel):
    """Response schema for debate endpoint."""
    
    response: str = Field(..., description="The LLM's debate response")
    model: str = Field(..., description="The model used for generation")

