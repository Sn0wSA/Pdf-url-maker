# Usa a imagem oficial do Playwright (já contém Python, Linux e os Navegadores)
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do seu PC para o Container
COPY requirements.txt .
COPY api.py .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Garante a instalação do Chromium e suas dependências de sistema
RUN playwright install chromium
RUN playwright install-deps

# Comando de inicialização
# O Render injeta a porta na variável ambiente $PORT
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port $PORT"]