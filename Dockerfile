FROM python:3.12-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copia todo o conteúdo para uma subpasta 'desafio_lu_estilo'
COPY . /app/desafio_lu_estilo

# Define o PYTHONPATH para incluir o diretório raiz do app
ENV PYTHONPATH=/app

# Expõe a porta 8000
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "desafio_lu_estilo.main:app", "--host", "0.0.0.0", "--port", "8000"]
