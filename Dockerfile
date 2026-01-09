# Usa a imagem oficial
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

COPY requirements.txt .

# --- MUDANÇA 1: De api.py para app.py ---
COPY app.py .

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps

# --- MUDANÇA 2: De api:app para app:app ---
# Isso diz ao uvicorn: "Vá no arquivo app.py e procure a variável app"
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]