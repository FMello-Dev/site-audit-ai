from fastapi import FastAPI, HTTPException
from app.schemas import AuditRequest, AuditResponse
from app.services.auditor import fetch_site_data
from app.services.llm_service import analyze_with_gemini

app = FastAPI(title="SiteAudit AI Agent")

@app.post("/analyze", response_model=AuditResponse)
async def analyze_website(request: AuditRequest):
    """
    Orquestrador Principal:
    1. Scraper (Playwright) -> Pega HTML e Print
    2. Vision AI (Gemini) -> Analisa UI/UX e Código
    """
    
    print(f"🚀 Recebida solicitação para: {request.url}")

    # PASSO 1: Coleta de Dados (Os Olhos)
    site_data = await fetch_site_data(str(request.url))
    
    if not site_data:
        raise HTTPException(status_code=400, detail="Falha ao acessar o site. Verifique a URL ou se o site bloqueia bots.")

    print("✅ Dados coletados. Iniciando análise da IA...")

    # PASSO 2: Análise Inteligente (O Cérebro)
    # Passamos o HTML, a Imagem em Base64 e a instrução extra do usuário
    ai_analysis = await analyze_with_gemini(
        html_content=site_data["html"],
        screenshot_b64=site_data["screenshot"],
        instruction=request.custom_instruction
    )

    if not ai_analysis:
        raise HTTPException(status_code=500, detail="Erro ao processar a análise com a IA.")

    # Injetamos a URL original na resposta para garantir que o JSON volte completo
    # (Às vezes a IA esquece de repetir a URL no JSON de saída)
    ai_analysis.url = str(request.url)

    print("✨ Análise concluída com sucesso!")
    return ai_analysis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)