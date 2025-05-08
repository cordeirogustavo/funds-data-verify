FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Garantir que o diretório de documentos existe
RUN mkdir -p /app/application/documents

# Define o entrypoint
ENTRYPOINT ["python", "application/main.py"] 