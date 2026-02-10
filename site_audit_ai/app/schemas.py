from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

# O que entra na API (Input)
class AuditRequest(BaseModel):
    url: HttpUrl = Field(..., description="A URL do site a ser analisado")
    custom_instruction: Optional[str] = Field(
        default=None, 
        description="Instrução específica, ex: 'Verifique se os botões são verdes'"
    )

# O que sai da API (Output) - Estrutura para a IA preencher
class AuditPoint(BaseModel):
    category: str = Field(..., description="UI, UX, Performance ou SEO")
    description: str
    suggestion: str

class AuditResponse(BaseModel):
    url: str
    score: int = Field(..., ge=0, le=100, description="Nota de 0 a 100")
    strengths: List[AuditPoint]
    weaknesses: List[AuditPoint]
    summary: str