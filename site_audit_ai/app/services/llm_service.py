from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas import AuditResponse
from app.config import settings

# Mantemos o modelo que funcionou para você
MODEL_NAME = "gemini-2.5-flash" 

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME, 
    temperature=0.4, # Aumentei um pouco para ele ser mais "opinativo" e menos robótico
    google_api_key=settings.GOOGLE_API_KEY
)

structured_llm = llm.with_structured_output(AuditResponse)

async def analyze_with_gemini(html_content: str, screenshot_b64: str, instruction: str = None):
    
    print(f"🧠 Enviando para o Gemini ({MODEL_NAME}) - Modo Crítico...")

    # AQUI ESTÁ A MÁGICA: O NOVO PROMPT "MALVADO"
    prompt_text = f"""
    Você é um Especialista em UI/UX de renome mundial (Nielsen Norman Group), conhecido por ser EXTREMAMENTE CRÍTICO e exigente.
    
    Sua missão é destruir construtivamente o design do site analisado. Não seja "bonzinho".
    
    REGRAS DE NOTA (SCORE):
    - 90-100: Design premiado, Apple/Airbnb level.
    - 70-89: Design moderno, limpo, 2024/2025.
    - 50-69: Design funcional mas DATADO (cara de 2015), genérico ou com pequenos erros.
    - 0-49: Design AMADOR, feio, antigo, poluição visual, imagens ruins ou cores berrantes.
    
    O QUE PROCURAR (PENALIZE SEVERAMENTE):
    1. Aparência de "Site Antigo" ou feito em tecnologias obsoletas.
    2. Imagens de baixa qualidade, esticadas ou banco de imagens genérico.
    3. Excesso de elementos chamando atenção (botões piscando, ícones tremendo).
    4. Espaçamento ruim (elementos colados uns nos outros).
    5. Tipografia difícil de ler ou não profissional.
    
    Instrução extra do usuário: {instruction if instruction else "Foque na estética e na credibilidade que o site passa."}
    
    Responda em PORTUGUÊS DO BRASIL. No resumo, seja direto sobre a sensação que o site passa (ex: "Passa amadorismo", "Parece abandonado").
    """

    message = HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}
            },
            {"type": "text", "text": prompt_text},
            # Mandamos menos HTML agora para ele focar mais na FOTO (Design) do que no código
            {"type": "text", "text": f"HTML Snippet:\n{html_content[:10000]}"} 
        ]
    )

    try:
        response = await structured_llm.ainvoke([message])
        return response
    except Exception as e:
        print(f"❌ Erro no Gemini: {e}")
        return None