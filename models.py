from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from desafio_lu_estilo.database import Base
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
import re

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

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
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
    model_config = ConfigDict(from_attributes=True)

class WhatsAppMessage(BaseModel):
    client_id: int
    message: str
