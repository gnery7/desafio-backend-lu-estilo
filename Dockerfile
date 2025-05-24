# Utiliza uma imagem oficial do Python como base
FROM python:3.12-slim

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . .

# Instala as dependências
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expõe a porta que a aplicação irá rodar
EXPOSE 8000

# Comando para iniciar o servidor FastAPI com Uvicorn
CMD ["uvicorn", "desafio_lu_estilo.main:app", "--host", "0.0.0.0", "--port", "8000"]
