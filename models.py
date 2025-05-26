from datetime import datetime, timedelta, timezone
from typing import Optional
import re
from fastapi import Path as PathParam, HTTPException, status
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, Field
from jose import JWTError, jwt
from passlib.context import CryptContext

from desafio_lu_estilo.database import Base

# ---------------------- CONFIGURAÇÃO JWT ----------------------
SECRET_KEY = "sua_chave_secreta_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------------------- MODELOS ORM (SQLAlchemy) ----------------------
class ClientORM(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    cpf = Column(String, unique=True, index=True)

class ProductORM(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    sale_price = Column(Float)
    barcode = Column(String, unique=True, index=True)
    section = Column(String)
    initial_stock = Column(Integer)
    expiration_date = Column(DateTime, nullable=True)
    image_url = Column(String, nullable=True)

class OrderORM(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    status = Column(String, default="pending")
    order_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    client = relationship("ClientORM")
    products = relationship("OrderProductORM", back_populates="order")

class OrderProductORM(Base):
    __tablename__ = "order_products"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    order = relationship("OrderORM", back_populates="products")

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Integer, default=0)

# ---------------------- SCHEMAS (Pydantic) ----------------------
class User(BaseModel):
    username: str = Field(..., example="usuario123", description="Nome de usuário")
    password: str = Field(..., example="senha123", description="Senha do usuário")
    is_admin: bool = Field(False, description="Define se o usuário é administrador")

class UserCreate(BaseModel):
    username: str = Field(..., example="usuario123", description="Nome de usuário")
    email: EmailStr = Field(..., example="email@example.com", description="E-mail do usuário")
    password: str = Field(..., example="senha123", description="Senha do usuário")
    is_admin: bool = Field(False, description="Define se o usuário é administrador")

class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(..., example="bearer")

class ClientBase(BaseModel):
    name: str = Field(..., example="Maria da Silva", description="Nome completo do cliente")
    email: EmailStr = Field(..., example="maria@email.com", description="E-mail do cliente")
    cpf: str = Field(..., example="12345678901", description="CPF com 11 dígitos")

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v):
        if not re.match(r"^\d{11}$", v):
            raise ValueError("CPF deve conter exatamente 11 dígitos")
        return v

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Novo Nome")
    email: Optional[EmailStr] = Field(None, example="novo@email.com")
    cpf: Optional[str] = Field(None, example="98765432100")

class ClientOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    cpf: str
    model_config = ConfigDict(from_attributes=True)

class Client(ClientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    description: str = Field(..., example="Blusa Feminina", description="Descrição do produto")
    sale_price: float = Field(..., example=89.90, description="Preço de venda")
    barcode: str = Field(..., example="7891234567890", description="Código de barras")
    section: str = Field(..., example="Moda Feminina", description="Seção do produto")
    initial_stock: int = Field(..., example=10, description="Estoque inicial")
    expiration_date: datetime | None = Field(None, example="2025-12-31T00:00:00Z", description="Validade (se aplicável)")
    image_url: str | None = Field(None, example="https://exemplo.com/imagem.jpg", description="URL da imagem do produto")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    description: Optional[str] = Field(None, example="Novo Produto")
    sale_price: Optional[float] = Field(None, example=99.90)
    barcode: Optional[str] = Field(None, example="1234567890123")
    section: Optional[str] = Field(None, example="Moda Masculina")
    stock: Optional[int] = Field(None, example=5)
    expiration_date: Optional[str] = Field(None, example="2025-12-31T00:00:00Z")

    class Config:
        from_attributes = True

class Product(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class OrderProductOut(BaseModel):
    product_id: int = Field(..., example=1)
    quantity: int = Field(..., example=2)
    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    client_id: int = Field(..., example=1, description="ID do cliente")
    status: str = Field("pending", example="pending", description="Status do pedido")
    products: list[int] = Field(..., example=[1, 2], description="Lista de IDs dos produtos")

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, example="shipped")
    products: Optional[list[int]] = Field(None, example=[1, 3])

class Order(OrderBase):
    id: int
    order_date: datetime
    products: list[OrderProductOut]
    model_config = ConfigDict(from_attributes=True)

class WhatsappMessage(BaseModel):
    client_id: int = Field(..., description="ID do cliente que receberá a mensagem", example=1)
    message: str = Field(..., description="Conteúdo da mensagem a ser enviada", example="Olá! Seu produto já está disponível.")
