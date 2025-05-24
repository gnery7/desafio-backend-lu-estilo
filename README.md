# 🚀 API - Desafio Backend Lu Estilo

API RESTful desenvolvida com **FastAPI**, **SQLAlchemy**, **JWT** e **SQLite**, permitindo o gerenciamento de clientes, produtos, pedidos e o envio simulado de mensagens via WhatsApp.

---

## 📦 Requisitos

- Python 3.12+
- Virtualenv recomendado

Instalação de dependências:
```bash
pip install -r requirements.txt
```

---

## ▶️ Como rodar o projeto

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd desafio_lu_estilo
```

2. Rode o servidor local:
```bash
uvicorn desafio_lu_estilo.main:app --reload
```

3. Acesse a documentação interativa:
- http://127.0.0.1:8000/docs

---

## 🔐 Autenticação

- Use o endpoint `/auth/login` com:
  ```
  username: admin
  password: admin123
  ```
- O token JWT retornado deve ser usado como `Bearer Token` nos endpoints protegidos.

---

## 🧪 Rodando os testes

Execute todos os testes com:
```bash
pytest
```

Todos os testes devem passar sem warnings, com cobertura de:
- Login
- Criação de clientes, produtos e pedidos
- Paginação e filtros
- Validação de dados
- Simulação de envio de mensagem via WhatsApp

---

## 📬 Endpoints principais

| Método | Rota                 | Descrição                             |
|--------|----------------------|---------------------------------------|
| POST   | `/auth/login`        | Login e geração de token JWT          |
| POST   | `/clients/`          | Criação de cliente                    |
| GET    | `/clients/`          | Listagem com paginação                |
| POST   | `/products/`         | Criação de produto                    |
| GET    | `/products/`         | Listagem com paginação                |
| POST   | `/orders/`           | Criação de pedido                     |
| POST   | `/whatsapp/send`     | Envio simulado de mensagem WhatsApp   |
| GET    | `/health`            | Verificação de saúde da API           |

---

## ✅ Tecnologias e Padrões Utilizados

- ✅ FastAPI
- ✅ SQLAlchemy
- ✅ Pydantic v2 com `ConfigDict`
- ✅ Autenticação JWT
- ✅ Testes com `pytest`
- ✅ Banco de dados SQLite para dev
- ✅ Simulação de integração com APIs externas
- ✅ Código compatível com Python 3.12+

---

## 📅 Última atualização

24/05/2025

---

Feito com 💻 por [Seu Nome]
