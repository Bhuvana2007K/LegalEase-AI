from pydantic import BaseModel


class DocumentRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    effective_date: str
    jurisdiction: str = ""
    additional_instructions: str = ""


class ExportRequest(BaseModel):
    document_type: str
    content: str


class HealthResponse(BaseModel):
    status: str
    gemini_configured: bool
    model: str