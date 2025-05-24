from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import jwt
import httpx
from pathlib import Path

from desafio_lu_estilo.database import SessionLocal, get_db, Base, engine
from desafio_lu_estilo.models import (
    ClientORM, ProductORM, OrderORM, OrderProductORM,
    User, Token, Client, ClientCreate, Product, ProductCreate,
    Order, OrderCreate, WhatsAppMessage
)

# Configurações
SECRET_KEY = "lu_estilo_secret_key_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
WHATSAPP_API_URL = "https://api.fakewhatsapp.com/send"
WHATSAPP_API_KEY = "fake-api-key"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
app = FastAPI()

# Permitir CORS para acesso via navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos (HTML/JS)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# Mock de usuários
users_db = {
    "admin": {
        "username": "admin",
        "password": "admin123",
        "is_admin": True
    }
}

# Criar tabelas se não existirem
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API da Lu Estilo! Acesse /docs para a documentação."}

@app.get("/web")
def serve_html():
    return FileResponse(Path(__file__).parent / "static" / "index.html")

# Funções auxiliares
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or user["password"] != password:
        return False
    return user

# Dependência
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
        return users_db[username]
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

# Rotas de autenticação
@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha incorretos")
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# Rotas de clientes
@app.post("/clients/", response_model=Client)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = ClientORM(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.get("/clients/", response_model=List[Client])
def read_clients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(ClientORM).offset(skip).limit(limit).all()

# Rotas de produtos
@app.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductORM(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[Product])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(ProductORM).offset(skip).limit(limit).all()

# Rotas de pedidos
@app.post("/orders/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = OrderORM(client_id=order.client_id, status=order.status)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

# Rota de envio WhatsApp
@app.post("/whatsapp/send")
async def send_whatsapp_message(message: WhatsAppMessage, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"status": "success", "message": "Mensagem enviada com sucesso (simulação)."}

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}
