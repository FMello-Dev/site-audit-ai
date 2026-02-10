import streamlit as st
import requests
import base64
import json

# Configuração da Página (Título e Ícone)
st.set_page_config(page_title="SiteAudit AI", page_icon="🕵️‍♂️", layout="wide")

# Estilo CSS Customizado para deixar mais bonito
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.title("🕵️‍♂️ SiteAudit AI - Auditoria Inteligente")
st.markdown("### Análise de UI/UX e SEO com Visão Computacional")

# Sidebar (Barra Lateral para Inputs)
with st.sidebar:
    st.header("Configuração da Análise")
    url_input = st.text_input("URL do Site", placeholder="https://exemplo.com.br")
    instruction_input = st.text_area("Instruções Específicas (Opcional)", 
                                     placeholder="Ex: Verifique se o botão de compra está visível...")
    
    analyze_btn = st.button("🔍 Iniciar Auditoria", use_container_width=True)
    
    st.info("ℹ️ O sistema acessará o site em tempo real, capturará uma imagem e analisará o código e o design.")

# Lógica Principal
if analyze_btn and url_input:
    if not url_input.startswith("http"):
        st.error("⚠️ A URL deve começar com http:// ou https://")
    else:
        with st.spinner("🤖 O Robô está navegando no site e analisando... (Isso leva uns 15s)"):
            try:
                # Chamada para a SUA API (Backend)
                response = requests.post(
                    "http://localhost:8000/analyze",
                    json={"url": url_input, "custom_instruction": instruction_input}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # --- ÁREA DE RESULTADOS ---
                    
                    # 1. Topo: Score e Resumo
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        # Exibe o Score como um medidor
                        score = data.get('score', 0)
                        st.metric(label="Nota Geral (Score)", value=f"{score}/100")
                        
                        # Barra de progresso colorida
                        if score > 80:
                            st.progress(score, text="Excelente 🟢")
                        elif score > 50:
                            st.progress(score, text="Médio 🟡")
                        else:
                            st.progress(score, text="Crítico 🔴")

                    with col2:
                        st.subheader("📝 Resumo Executivo")
                        st.write(data.get('summary', 'Sem resumo.'))

                    st.divider()

                    # 2. Pontos Fortes e Fracos (Lado a Lado)
                    c_strengths, c_weaknesses = st.columns(2)

                    with c_strengths:
                        st.success("✅ Pontos Fortes")
                        for item in data.get('strengths', []):
                            with st.expander(f"**{item['category']}**: {item['description'][:50]}..."):
                                st.write(f"**Detalhe:** {item['description']}")
                                st.write(f"💡 **Sugestão:** {item['suggestion']}")

                    with c_weaknesses:
                        st.error("❌ Pontos de Melhoria")
                        for item in data.get('weaknesses', []):
                            with st.expander(f"**{item['category']}**: {item['description'][:50]}..."):
                                st.write(f"**Detalhe:** {item['description']}")
                                st.write(f"💡 **Ação Recomendada:** {item['suggestion']}")

                    st.divider()

                    # 3. JSON Bruto (Para debug ou curiosidade)
                    with st.expander("Ver JSON Completo da API"):
                        st.json(data)

                else:
                    st.error(f"Erro na API: {response.text}")

            except Exception as e:
                st.error(f"Não foi possível conectar ao servidor. O Backend está rodando? Erro: {e}")

elif analyze_btn and not url_input:
    st.warning("Por favor, insira uma URL válida.")