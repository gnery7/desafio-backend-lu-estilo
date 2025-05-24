# 💅 Desafio Backend - Lu Estilo

API RESTful construída com **FastAPI**, **SQLAlchemy** e **Pydantic v2**, com autenticação via JWT, banco de dados SQLite e testes automatizados com `pytest`.

---

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-success)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 📚 Sumário

- [Sobre](#sobre)
- [Tecnologias](#tecnologias)
- [Como rodar o projeto](#como-rodar-o-projeto)
- [Autenticação](#autenticação)
- [Endpoints](#endpoints)
- [Testes](#testes)
- [Licença](#licença)

---

## 📌 Sobre

Este projeto é uma API de controle de clientes, produtos e pedidos para a loja Lu Estilo. Inclui envio simulado de mensagens via WhatsApp e autenticação com JWT.

---

## 🚀 Tecnologias

- Python 3.12
- FastAPI
- SQLAlchemy 2
- Pydantic v2 (`ConfigDict`, `field_validator`)
- SQLite (desenvolvimento)
- Pytest
- Uvicorn
- httpx (para simulação de API externa)

---

## ⚙️ Como rodar o projeto

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/desafio-backend-lu-estilo.git
cd desafio-backend-lu-estilo
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
venv\Scripts\activate  # ou source venv/bin/activate no Linux/Mac
pip install -r requirements.txt
```

3. Execute a API:
```bash
uvicorn desafio_lu_estilo.main:app --reload
```

4. Acesse:
- http://127.0.0.1:8000/docs — Swagger UI
- http://127.0.0.1:8000/redoc — Redoc

---

## 🔐 Autenticação

Use o endpoint `/auth/login` com:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

- O token JWT retornado deve ser usado como Bearer Token nos headers:
```
Authorization: Bearer <token>
```

---

## 📬 Endpoints principais

| Método | Rota                    | Protegido | Descrição                           |
|--------|-------------------------|-----------|-------------------------------------|
| POST   | /auth/login             | ❌        | Geração de token JWT                |
| POST   | /clients/               | ✅        | Criar cliente                       |
| GET    | /clients/?skip=&limit=  | ✅        | Listar clientes com paginação       |
| POST   | /products/              | ✅        | Criar produto                       |
| GET    | /products/?skip=&limit= | ✅        | Listar produtos com paginação       |
| POST   | /orders/                | ✅        | Criar pedido                        |
| POST   | /whatsapp/send          | ✅        | Enviar mensagem WhatsApp (simulado) |
| GET    | /health                 | ❌        | Verificação de saúde da API         |

---

## 🧪 Testes

Execute os testes com:

```bash
pytest
```

Os testes cobrem:

- Login e geração de token
- Criação de clientes, produtos e pedidos
- Paginação
- Validação de CPF
- Simulação de envio via WhatsApp
- Acesso com token inválido

---

## 🛡️ Licença

Este projeto está sob licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🤝 Contribuindo

Pull requests são bem-vindos! Para melhorias ou correções:

1. Fork este repositório
2. Crie sua branch (`git checkout -b minha-feature`)
3. Commit suas mudanças (`git commit -am 'feat: nova feature'`)
4. Push para a branch (`git push origin minha-feature`)
5. Abra um Pull Request

---

## 📅 Atualizado em

24/05/2025

---