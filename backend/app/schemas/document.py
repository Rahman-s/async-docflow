from pydantic import BaseModel
from typing import Optional


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    progress: int
    extracted_data: Optional[str] = None
    finalized_data: Optional[str] = None
    is_finalized: bool
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentUpdate(BaseModel):
    finalized_data: str


class FinalizeRequest(BaseModel):
    finalized_data: str