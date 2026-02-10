import base64
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from app.config import settings

async def fetch_site_data(url: str):
    """
    Navega até o site, tira um print e extrai o HTML limpo.
    """
    print(f"🕵️  Iniciando coleta para: {url}")
    
    async with async_playwright() as p:
        # 1. Lança o navegador (Chromium)
        # headless=True significa que ele roda sem abrir janela (mais rápido/servidor)
        # headless=False é bom para ver ele trabalhando (debug)
        browser = await p.chromium.launch(headless=settings.HEADLESS_MODE)
        
        # 2. Cria uma nova aba simulando um Desktop padrão
        page = await browser.new_page(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) SiteAuditBot/1.0"
        )
        
        try:
            # 3. Acessa a URL e espera a rede ficar ociosa ('networkidle')
            # Isso garante que o site carregou tudo (React/Vue/Angular precisam disso)
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 4. Tira o Screenshot e converte para Base64
            # IAs não "abrem arquivos jpg", elas leem strings de texto. Base64 vira texto.
            screenshot_bytes = await page.screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            
            # 5. Pega o HTML Bruto
            raw_html = await page.content()
            
            # 6. Limpeza de HTML (Economia de Tokens)
            # Removemos scripts, svgs gigantes e estilos, pois só queremos a estrutura de texto
            soup = BeautifulSoup(raw_html, "html.parser")
            for tag in soup(["script", "style", "svg", "noscript", "iframe"]):
                tag.decompose()
            
            clean_html = soup.prettify()
            
            print("✅ Coleta finalizada com sucesso!")
            
            return {
                "screenshot": screenshot_b64,
                "html": clean_html[:15000] # Limitamos a 15k caracteres para não estourar a memória da IA agora
            }

        except Exception as e:
            print(f"❌ Erro ao coletar dados: {e}")
            return None
        finally:
            # Sempre fecha o navegador para não travar a memória RAM do computador
            await browser.close()