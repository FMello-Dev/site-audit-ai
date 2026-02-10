from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas import AuditResponse
from app.config import settings

# Mantemos o modelo 2.5 flash (ou o que estiver funcionando para você)
MODEL_NAME = "gemini-2.5-flash" 

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME, 
    temperature=0.3, # Baixei para 0.3 para ele ser mais frio e analítico
    google_api_key=settings.GOOGLE_API_KEY
)

structured_llm = llm.with_structured_output(AuditResponse)

async def analyze_with_gemini(html_content: str, screenshot_b64: str, instruction: str = None):
    
    print(f"🧠 Enviando para o Gemini ({MODEL_NAME}) - Modo Consultor Implacável...")

    prompt_text = f"""
    Você é um Consultor de Elite em Estratégia Digital e Conversão (CRO), contratado para fazer uma auditoria BRUTALMENTE HONESTA.
    
    SEU CLIENTE: É um empresário que não entende de código, mas entende de DINHEIRO.
    SUA MISSÃO: Encontrar falhas no site que estão "queimando" o dinheiro dele ou afugentando clientes.
    
    DIRETRIZES DE ANÁLISE (SEJA RIGOROSO):
    1. ESTÉTICA É CREDIBILIDADE: Se o site parece feito em 2015, diga que isso destrói a confiança da marca. Design datado = Empresa parada no tempo.
    2. VELOCIDADE É VENDA: Se o código sugerir lentidão, explique que clientes não esperam e vão para o concorrente.
    3. CLAREZA É REI: Se não der para entender o que a empresa vende em 3 segundos, critique severamente.
    4. RESPONSIVIDADE: Se o site parecer ruim no celular, diga que ele está perdendo 80% dos clientes.

    REGRAS DE LINGUAGEM (TRADUÇÃO DE NEGÓCIOS):
    - PROIBIDO "TECH-JARGON": Nada de "CSS", "HTML", "Tags", "Framework", "Scripts".
    - USE TERMOS DE IMPACTO: "Fricção no usuário", "Perda de conversão", "Poluição visual", "Falta de hierarquia", "Sensação de amadorismo".

    SISTEMA DE PONTUAÇÃO (RÉGUA ALTA):
    - 90-100: Nível Apple/Nubank. Impecável. (Raríssimo).
    - 70-89: Bom, moderno e funcional. Passa confiança.
    - 50-69: Medíocre. Funciona, mas tem cara de "barato" ou antigo. Precisa de reforma.
    - 0-49: Crítico. O site está ativamente prejudicando a imagem da empresa.

    Instrução extra do usuário: {instruction if instruction else "Foque na credibilidade e na experiência do cliente final."}
    
    Responda em PORTUGUÊS DO BRASIL. 
    No "Resumo Executivo", seja direto e impactante. Exemplo: "Este site passa uma imagem de amadorismo que não condiz com o tamanho da sua empresa."
    """

    message = HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}
            },
            {"type": "text", "text": prompt_text},
            # O contexto técnico ajuda a IA a saber se é WordPress, Wix, etc, mas ela não vai citar isso pro cliente
            {"type": "text", "text": f"Contexto Técnico (Use para diagnóstico, mas traduza para linguagem de negócios):\n{html_content[:10000]}"} 
        ]
    )

    try:
        response = await structured_llm.ainvoke([message])
        return response
    except Exception as e:
        print(f"❌ Erro no Gemini: {e}")
        return None