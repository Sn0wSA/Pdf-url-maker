from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from playwright.async_api import async_playwright

app = FastAPI(title="API Geradora de PDF")

@app.get("/")
def home():
    return {"status": "online", "msg": "Use o endpoint /gerar-pdf?url=..."}

@app.get("/gerar-pdf")
async def gerar_pdf(url: str = Query(..., description="URL para converter")):
    # Validação simples
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="A URL deve começar com http:// ou https://")

    try:
        async with async_playwright() as p:
            # --no-sandbox e --disable-dev-shm-usage são OBRIGATÓRIOS para rodar em Docker/Render
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await browser.new_context()
            page = await context.new_page()
            
            print(f"Acessando: {url}")
            await page.goto(url, timeout=60000) # Timeout de 60 segundos
            
            # Espera o site carregar a rede (networkidle)
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except:
                print("Aviso: Timeout esperando networkidle, gerando PDF mesmo assim...")

            # Gera o PDF em memória
            pdf_bytes = await page.pdf(format="A4", print_background=True)
            
            await browser.close()
            
            return Response(
                content=pdf_bytes, 
                media_type="application/pdf",
                headers={"Content-Disposition": "inline; filename=arquivo.pdf"}
            )
            
    except Exception as e:
        print(f"Erro: {e}")
        return Response(content=f"Erro no servidor: {str(e)}", status_code=500)