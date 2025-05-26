import os
from fastapi import FastAPI, Depends, HTTPException, status, Request, Path as PathParam, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from pathlib import Path as FilePath
import logging
from logging.handlers import RotatingFileHandler

from desafio_lu_estilo.database import Base, engine, get_db
from desafio_lu_estilo.models import (
    ClientCreate, ClientUpdate, ClientOut, ClientORM,
    ProductCreate, ProductUpdate, Product, ProductORM,
    OrderCreate, OrderUpdate, Order, OrderORM, OrderProductORM,
    WhatsappMessage, UserORM
)
from desafio_lu_estilo.auth import router as auth_router, get_current_user, get_password_hash, oauth2_scheme
from desafio_lu_estilo.utils import send_whatsapp_message_to

# Logger de erros
os.makedirs("logs", exist_ok=True)
log_handler = RotatingFileHandler("logs/error.log", maxBytes=1000000, backupCount=5)
log_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
log_handler.setFormatter(log_formatter)
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.ERROR)
logger.addHandler(log_handler)

# Inicialização
Base.metadata.create_all(bind=engine)
app = FastAPI(title="API - Lu Estilo", description="API para cadastro de clientes, produtos, pedidos e envio simulado de WhatsApp.", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arquivos estáticos
static_dir = FilePath(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def root():
    return FileResponse(static_dir / "index.html")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# CLIENTES
@app.post("/clients/", response_model=ClientOut)
def create_client(client: ClientCreate, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    if db.query(ClientORM).filter_by(cpf=client.cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    if db.query(ClientORM).filter_by(email=client.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    db_client = ClientORM(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return ClientOut.model_validate(db_client)

@app.get("/clients/", response_model=list[ClientOut])
def list_clients(skip: int = 0, limit: int = 10, name: str = Query(None), email: str = Query(None), db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    query = db.query(ClientORM)
    if name:
        query = query.filter(ClientORM.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(ClientORM.email.ilike(f"%{email}%"))
    clients = query.offset(skip).limit(limit).all()
    return [ClientOut.model_validate(client) for client in clients]

@app.get("/clients/{client_id}", response_model=ClientOut)
def get_client_by_id(client_id: int, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    client = db.query(ClientORM).filter_by(id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return ClientOut.model_validate(client)

@app.put("/clients/{id}", response_model=ClientOut)
def update_client(updated_data: ClientUpdate, id: int = PathParam(gt=0), db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    client = db.query(ClientORM).filter_by(id=id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if updated_data.email and updated_data.email != client.email:
        if db.query(ClientORM).filter(ClientORM.email == updated_data.email, ClientORM.id != id).first():
            raise HTTPException(status_code=400, detail="Email já em uso")
    for field, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return ClientOut.model_validate(client)

@app.delete("/clients/{id}")
def delete_client(id: int, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    client = db.query(ClientORM).filter_by(id=id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(client)
    db.commit()
    return {"detail": "Cliente deletado com sucesso"}

# PRODUTOS
@app.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    db_product = ProductORM(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return Product.model_validate(db_product)

@app.get("/products/", response_model=list[Product])
def list_products(skip: int = 0, limit: int = 10, section: str = Query(None), min_price: float = Query(None), max_price: float = Query(None), available: bool = Query(None), db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    query = db.query(ProductORM)
    if section:
        query = query.filter(ProductORM.section.ilike(f"%{section}%"))
    if min_price is not None:
        query = query.filter(ProductORM.sale_price >= min_price)
    if max_price is not None:
        query = query.filter(ProductORM.sale_price <= max_price)
    if available:
        query = query.filter(ProductORM.initial_stock > 0)
    return [Product.model_validate(p) for p in query.offset(skip).limit(limit).all()]

@app.get("/products/{product_id}", response_model=Product)
def get_product_by_id(product_id: int, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    product = db.query(ProductORM).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return Product.model_validate(product)

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, updated_data: ProductUpdate, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    product = db.query(ProductORM).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    for field, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return Product.model_validate(product)

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    product = db.query(ProductORM).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(product)
    db.commit()
    return {"detail": "Produto deletado com sucesso"}

# PEDIDOS
@app.post("/orders/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    for product_id in order.products:
        product = db.query(ProductORM).filter_by(id=product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Produto {product_id} não encontrado")
        if product.initial_stock <= 0:
            raise HTTPException(status_code=400, detail=f"Produto {product.description} sem estoque disponível")

    db_order = OrderORM(client_id=order.client_id, status=order.status)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for product_id in order.products:
        db.add(OrderProductORM(order_id=db_order.id, product_id=product_id, quantity=1))
        db.query(ProductORM).filter_by(id=product_id).update({ProductORM.initial_stock: ProductORM.initial_stock - 1})

    db.commit()
    db.refresh(db_order)
    return Order.model_validate(db_order)

@app.get("/orders/", response_model=list[Order])
def list_orders(skip: int = 0, limit: int = 10, status: str = Query(None), client_id: int = Query(None), db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    query = db.query(OrderORM)
    if status:
        query = query.filter(OrderORM.status.ilike(f"%{status}%"))
    if client_id:
        query = query.filter(OrderORM.client_id == client_id)
    return [Order.model_validate(p) for p in query.offset(skip).limit(limit).all()]

@app.get("/orders/{order_id}", response_model=Order)
def get_order_by_id(order_id: int, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    order = db.query(OrderORM).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return Order.model_validate(order)

@app.put("/orders/{order_id}", response_model=Order)
def update_order(order_id: int, updated_data: OrderUpdate = Body(...), db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    order = db.query(OrderORM).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if updated_data.status:
        order.status = updated_data.status
    if updated_data.products:
        db.query(OrderProductORM).filter_by(order_id=order.id).delete()
        for product_id in updated_data.products:
            db.add(OrderProductORM(order_id=order.id, product_id=product_id, quantity=1))
    db.commit()
    db.refresh(order)
    return Order.model_validate(order)

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    order = db.query(OrderORM).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    db.query(OrderProductORM).filter_by(order_id=order_id).delete()
    db.delete(order)
    db.commit()
    return {"detail": "Pedido deletado com sucesso"}

# WHATSAPP
@app.post("/whatsapp/send", response_model=dict)
def send_whatsapp(message: WhatsappMessage, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    client = db.query(ClientORM).filter_by(id=message.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return send_whatsapp_message_to(client, message.message)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc} | Path: {request.url}")
    return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor. A equipe técnica foi notificada."})

@app.get("/orders/", response_model=list[Order])
def list_orders(
    skip: int = 0,
    limit: int = 10,
    status: str = Query(None),
    client_id: int = Query(None),
    section: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db),
    user: UserORM = Depends(get_current_user)
) -> list[Order]:
    query = db.query(OrderORM)

    if status:
        query = query.filter(OrderORM.status.ilike(f"%{status}%"))
    if client_id:
        query = query.filter(OrderORM.client_id == client_id)
    if start_date:
        query = query.filter(func.date(OrderORM.order_date) >= start_date)
    if end_date:
        query = query.filter(func.date(OrderORM.order_date) <= end_date)
    if section:
        query = query.join(OrderProductORM).join(ProductORM).filter(ProductORM.section.ilike(f"%{section}%")).distinct()

    pedidos = query.offset(skip).limit(limit).all()
    return [Order.model_validate(p) for p in pedidos]

@app.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)) -> Product:
    db_product = ProductORM(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return Product.model_validate(db_product)

@app.get("/products/", response_model=list[Product])
def list_products(
    skip: int = 0,
    limit: int = 10,
    section: str = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None),
    available: bool = Query(None),
    db: Session = Depends(get_db),
    user: UserORM = Depends(get_current_user)
) -> list[Product]:
    query = db.query(ProductORM)
    if section:
        query = query.filter(ProductORM.section.ilike(f"%{section}%"))
    if min_price is not None:
        query = query.filter(ProductORM.sale_price >= min_price)
    if max_price is not None:
        query = query.filter(ProductORM.sale_price <= max_price)
    if available:
        query = query.filter(ProductORM.initial_stock > 0)
    produtos = query.offset(skip).limit(limit).all()
    return [Product.model_validate(p) for p in produtos]

# Auth router
app.include_router(auth_router)
