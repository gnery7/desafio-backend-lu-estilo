from fastapi import Path as PathParam
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from desafio_lu_estilo.database import Base
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, Field
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import re

SECRET_KEY = "sua_chave_secreta_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Modelos ORM (SQLAlchemy)
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

# Modelos Pydantic (Schemas)
class User(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class ClientBase(BaseModel):
    name: str
    email: EmailStr
    cpf: str

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v):
        if not re.match(r"^\d{11}$", v):
            raise ValueError("CPF deve conter exatamente 11 dígitos")
        return v

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    description: str
    sale_price: float
    barcode: str
    section: str
    initial_stock: int
    expiration_date: datetime | None = None
    image_url: str | None = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class OrderProductOut(BaseModel):
    product_id: int
    quantity: int
    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    client_id: int
    status: str = "pending"
    products: list[int]

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    order_date: datetime
    products: list[OrderProductOut]
    model_config = ConfigDict(from_attributes=True)

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    products: Optional[list[int]] = None

class WhatsappMessage(BaseModel):
    client_id: int = Field(..., description="ID do cliente que receberá a mensagem")
    message: str = Field(..., description="Conteúdo da mensagem a ser enviada")

class ClientOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    cpf: str
    model_config = ConfigDict(from_attributes=True)

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Integer, default=0)

# Esquemas Pydantic
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_admin: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None

class ProductUpdate(BaseModel):
    description: Optional[str] = None
    sale_price: Optional[float] = None
    barcode: Optional[str] = None
    section: Optional[str] = None
    stock: Optional[int] = None
    expiration_date: Optional[str] = None

    class Config:
        from_attributes = True
