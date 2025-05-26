
# 💅 Desafio Backend - Lu Estilo

API RESTful construída com **FastAPI**, **SQLAlchemy 2**, **Pydantic v2**, com autenticação via JWT, banco de dados SQLite, migrações com Alembic e testes automatizados com `pytest`.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.2-success)
![Status](https://img.shields.io/badge/status-finalizado-green)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📚 Sumário

- [Sobre](#sobre)
- [Tecnologias](#tecnologias)
- [Como rodar o projeto](#como-rodar-o-projeto)
- [Autenticação](#autenticação)
- [Endpoints](#endpoints)
- [Testes](#testes)
- [Migrações com Alembic](#migrações-com-alembic)
- [🐳 Deploy com Docker](#🐳-deploy-com-docker)
- [Licença](#licença)

## 📌 Sobre

Este projeto é uma API de controle de clientes, produtos e pedidos para a loja Lu Estilo. Inclui envio simulado de mensagens via WhatsApp, autenticação JWT, filtros avançados, e suporte a imagens de produtos.

## 🚀 Tecnologias

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Alembic (migrações)
- Pydantic v2 (`ConfigDict`, `field_validator`)
- SQLite (desenvolvimento)
- Pytest
- Uvicorn

## ⚙️ Como rodar o projeto

```bash
git clone https://github.com/gnery7/desafio_lu_estilo.git
cd desafio_lu_estilo
python -m venv venv
venv\Scripts\activate  # ou source venv/bin/activate no Linux/Mac
pip install -r requirements.txt
uvicorn desafio_lu_estilo.main:app --reload
```

Acesse:
- http://127.0.0.1:8000/docs — Swagger UI
- http://127.0.0.1:8000/static/index.html — Interface visual

## 🔐 Autenticação

Use:
```json
POST /auth/login
{
  "username": "admin",
  "password": "admin123"
}
```

Adicione nos headers:
```
Authorization: Bearer <token>
```

## 📬 Endpoints principais

| Método | Rota                  | Protegido | Descrição                                        |
|--------|-----------------------|-----------|--------------------------------------------------|
| POST   | /auth/login           | ❌        | Geração de token JWT                             |
| POST   | /auth/register        | ❌        | Registro de novo usuário                         |
| POST   | /auth/refresh-token   | ✅        | Geração de novo token JWT                        |
| GET    | /clients              | ✅        | Listar clientes (filtros por nome, email)        |
| POST   | /clients              | ✅        | Criar cliente com validação de CPF e email únicos|
| PUT    | /clients/{id}         | ✅        | Atualizar cliente                                |
| DELETE | /clients/{id}         | ✅        | Excluir cliente                                  |
| GET    | /products             | ✅        | Listar produtos (filtros por seção, preço, estoque) |
| POST   | /products             | ✅        | Criar produto (suporte a `image_url`)            |
| GET    | /orders               | ✅        | Listar pedidos (filtros por data, cliente, seção, status, id) |
| POST   | /orders               | ✅        | Criar pedido (valida estoque)                    |
| PUT    | /orders/{id}          | ✅        | Atualizar pedido (status ou produtos)            |
| DELETE | /orders/{id}          | ✅        | Deletar pedido                                   |
| POST   | /whatsapp/send        | ✅        | Simular envio de mensagem via WhatsApp           |
| GET    | /health               | ❌        | Verificação de saúde da API                      |

## 🧪 Testes

Execute os testes com:
```bash
pytest
```

Cobertura de:
- Autenticação JWT
- Registro e login
- Ações de CRUD completo (clientes, produtos, pedidos)
- Filtros por nome, email, preço, seção, status, data, id
- Validações (CPF, estoque)
- WhatsApp simulado
- Erros tratados e protegidos por token

## 🛠️ Migrações com Alembic

1. Inicializar o Alembic (se ainda não existir):
```bash
alembic init alembic
```

2. Configure o `alembic.ini` com seu caminho de banco e use:
```bash
alembic revision --autogenerate -m "create tables"
alembic upgrade head
```

3. Para aplicar as migrações:
```bash
alembic upgrade head
```

## 🐳 Deploy com Docker

1. Clone o projeto:
```bash
git clone https://github.com/gnery7/desafio_lu_estilo.git
cd desafio_lu_estilo
```

2. Suba com Docker Compose:
```bash
docker-compose up --build
```

3. Acesse:
- http://localhost:8000/docs — Swagger UI
- http://localhost:8000/static/index.html — Interface visual

## 📝 Licença

Este projeto está licenciado sob a licença [MIT](LICENSE).
