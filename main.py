from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import jwt
import httpx
from desafio_lu_estilo.database import SessionLocal, get_db, Base, engine
from desafio_lu_estilo.models import (
    ClientORM, ProductORM, OrderORM, OrderProductORM,
    User, Token, Client, ClientCreate, Product, ProductCreate, 
    Order, OrderCreate, WhatsAppMessage
)

# Configurações
Base.metadata.create_all(bind=engine)
SECRET_KEY = "lu_estilo_secret_key_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
WHATSAPP_API_URL = "https://api.fakewhatsapp.com/send"
WHATSAPP_API_KEY = "fake-api-key"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Inicialização
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ["http://127.0.0.1:8000"] para mais segurança
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static"
)

# Mock de usuários
users_db = {
    "admin": {
        "username": "admin",
        "password": "admin123",
        "is_admin": True
    }
}

# Funções auxiliares
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or user["password"] != password:
        return False
    return user

# Dependência de sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Autenticação via token JWT
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return users_db[username]
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# Rota raiz
@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API da Lu Estilo! Acesse /docs para a documentação."}

# Rotas de Autenticação
@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Rotas de Clientes
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

# Rotas de Produtos
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

# Rotas de Pedidos
@app.post("/orders/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = OrderORM(
        client_id=order.client_id,
        status=order.status
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

# Rota de envio de WhatsApp (simulada)
@app.post("/whatsapp/send", status_code=status.HTTP_200_OK)
async def send_whatsapp_message(
    message: WhatsAppMessage, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client = db.query(ClientORM).filter(ClientORM.id == message.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    print(f"[Simulado] Enviando mensagem para {client.email}: {message.message}")
    return {"status": "success", "message": "Mensagem enviada com sucesso"}

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}
