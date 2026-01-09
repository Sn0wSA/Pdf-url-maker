import asyncio # <--- 1. IMPORTAR ASYNCIO
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from playwright.async_api import async_playwright

app = FastAPI(title="API Geradora de PDF")

@app.get("/")
def home():
    return {"status": "online", "msg": "Use o endpoint /gerar-pdf?url=..."}

@app.get("/gerar-pdf")
async def gerar_pdf(url: str = Query(..., description="URL para converter")):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="A URL deve começar com http:// ou https://")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await browser.new_context()
            page = await context.new_page()
            
            print(f"Acessando: {url}")
            # Aumentei o timeout de navegação para garantir
            await page.goto(url, timeout=90000) 
            
            # --- MUDANÇA PRINCIPAL AQUI ---
            print("Aguardando carregamento da rede...")
            try:
                # 1. Tenta esperar a rede ficar ociosa (aumentei para 30s)
                await page.wait_for_load_state("networkidle", timeout=30000)
            except:
                print("Aviso: A rede não parou totalmente, mas vamos continuar...")

            # 2. Espera FORÇADA de 5 segundos para renderização visual (React/Angular)
            # Isso garante que o ícone de loading suma mesmo se a rede já parou
            print("Aguardando renderização final...")
            await asyncio.sleep(5) 

            # 3. (Opcional) Role a página para baixo para forçar carregamento de imagens "lazy load"
            # await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # await asyncio.sleep(1)
            
            # Gera o PDF
            pdf_bytes = await page.pdf(format="A4", print_background=True)
            
            await browser.close()
            
            return Response(
                content=pdf_bytes, 
                media_type="application/pdf",
                headers={"Content-Disposition": "inline; filename=arquivo.pdf"}
            )
            
    except Exception as e:
        print(f"Erro CRÍTICO: {e}")
        return Response(content=f"Erro no servidor: {str(e)}", status_code=500)