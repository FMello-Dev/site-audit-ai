import streamlit as st
import asyncio
import nest_asyncio # Importante para Playwright rodar no Streamlit
from app.services.auditor import fetch_site_data
from app.services.llm_service import analyze_with_gemini

# Correção para loops assíncronos no Streamlit
nest_asyncio.apply()

# Configuração da Página
st.set_page_config(page_title="SiteAudit AI", page_icon="🕵️‍♂️", layout="wide")

st.markdown("""
<style>
    .metric-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("🕵️‍♂️ SiteAudit AI - Auditoria Inteligente")
st.markdown("### Versão Cloud (Deploy)")

# Instalação dos navegadores no boot (Gambiarra necessária para nuvem)
def install_playwright():
    import os
    # Só roda se não achar o navegador
    print("Verificando navegadores...")
    os.system("playwright install chromium")

# Sidebar
with st.sidebar:
    st.header("Configuração")
    url_input = st.text_input("URL do Site", placeholder="https://...")
    instruction_input = st.text_area("Instruções (Opcional)")
    analyze_btn = st.button("🔍 Iniciar Auditoria")
    
    # Botão de emergência para instalar navegador se der erro
    if st.button("🔧 Reinstalar Navegadores (Debug)"):
        with st.spinner("Instalando..."):
            install_playwright()
            st.success("Concluído!")

if analyze_btn and url_input:
    if not url_input.startswith("http"):
        st.error("A URL deve começar com http:// ou https://")
    else:
        with st.spinner("🤖 O Robô está navegando na nuvem..."):
            try:
                # 1. Chamada Direta ao Playwright (Sem API)
                # Precisamos rodar o async dentro do sync do Streamlit
                site_data = asyncio.run(fetch_site_data(url_input))
                
                if not site_data:
                    st.error("Falha ao acessar o site. O Playwright pode não estar instalado corretamente na nuvem.")
                else:
                    # 2. Chamada Direta ao Gemini
                    analysis = asyncio.run(analyze_with_gemini(
                        html_content=site_data["html"],
                        screenshot_b64=site_data["screenshot"],
                        instruction=instruction_input
                    ))
                    
                    if analysis:
                        # Exibição dos Resultados (Copiado do seu frontend original)
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            score = analysis.score
                            st.metric(label="Nota Geral", value=f"{score}/100")
                            if score > 80: st.progress(score, text="Excelente 🟢")
                            elif score > 50: st.progress(score, text="Médio 🟡")
                            else: st.progress(score, text="Crítico 🔴")
                        
                        with col2:
                            st.subheader("📝 Resumo Executivo")
                            st.write(analysis.summary)
                        
                        st.divider()
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.success("✅ Pontos Fortes")
                            for item in analysis.strengths:
                                with st.expander(f"**{item.category}**"):
                                    st.write(item.description)
                        with c2:
                            st.error("❌ Pontos de Melhoria")
                            for item in analysis.weaknesses:
                                with st.expander(f"**{item.category}**"):
                                    st.write(item.description)
                                    st.info(f"💡 {item.suggestion}")

            except Exception as e:
                st.error(f"Erro Crítico: {e}")