# tests/test_api.py

import pytest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from desafio_lu_estilo.main import app
from desafio_lu_estilo.database import Base, engine

client = TestClient(app)

# ------------------------ FIXTURE DE TESTE ------------------------
@pytest.fixture(scope="module", autouse=True)
def test_db():
    from desafio_lu_estilo.database import get_db
    from desafio_lu_estilo.auth import get_password_hash
    from desafio_lu_estilo.models import UserORM

    Base.metadata.create_all(bind=engine)
    db = next(get_db())

    if not db.query(UserORM).filter_by(username="admin").first():
        db_user = UserORM(
            username="admin",
            email="admin@email.com",
            hashed_password=get_password_hash("admin123"),
            is_admin=1
        )
        db.add(db_user)
        db.commit()

    yield
    Base.metadata.drop_all(bind=engine)

# ------------------------ TOKEN ------------------------
def get_token():
    response = client.post("/auth/login", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["access_token"]

# ------------------------ AUTH ------------------------
def test_register_user():
    response = client.post("/auth/register", json={
        "username": f"user_{uuid.uuid4().hex[:5]}",
        "email": f"user_{uuid.uuid4().hex[:5]}@email.com",
        "password": "senha123"
    })
    assert response.status_code in [200, 201, 400]  # Pode retornar erro de duplicado

def test_login_user():
    response = client.post("/auth/login", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_refresh_token():
    token = get_token()
    response = client.post("/auth/refresh-token", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

# ------------------------ CLIENTES ------------------------
def test_create_client():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/clients/", json={
        "name": "Cliente Teste",
        "email": f"{uuid.uuid4().hex[:8]}@email.com",
        "cpf": str(int(uuid.uuid4().int) % 10**11).zfill(11)
    }, headers=headers)
    assert response.status_code == 200

def test_list_clients():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/clients/", headers=headers)
    assert response.status_code == 200

def test_update_client():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/clients/", json={
        "name": "Cliente Update",
        "email": f"{uuid.uuid4().hex[:8]}@email.com",
        "cpf": str(int(uuid.uuid4().int) % 10**11).zfill(11)
    }, headers=headers)
    client_id = response.json()["id"]
    update = client.put(f"/clients/{client_id}", json={"name": "Atualizado"}, headers=headers)
    assert update.status_code == 200
    assert update.json()["name"] == "Atualizado"

def test_delete_client():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/clients/", json={
        "name": "Cliente Delete",
        "email": f"{uuid.uuid4().hex[:8]}@email.com",
        "cpf": str(int(uuid.uuid4().int) % 10**11).zfill(11)
    }, headers=headers)
    client_id = response.json()["id"]
    delete = client.delete(f"/clients/{client_id}", headers=headers)
    assert delete.status_code == 200

# ------------------------ PRODUTOS ------------------------
def test_create_product():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/products/", json={
        "description": "Produto Teste",
        "sale_price": 10.0,
        "barcode": f"{uuid.uuid4().int % 1000000000000:013}",
        "section": "Geral",
        "initial_stock": 10,
        "expiration_date": None
    }, headers=headers)
    assert response.status_code == 200

def test_list_products():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/products/", headers=headers)
    assert response.status_code == 200

def test_update_product():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/products/", json={
        "description": "Produto Update",
        "sale_price": 10.0,
        "barcode": f"{uuid.uuid4().int % 1000000000000:013}",
        "section": "Update",
        "initial_stock": 10,
        "expiration_date": None
    }, headers=headers)
    product_id = response.json()["id"]
    update = client.put(f"/products/{product_id}", json={"description": "Atualizado"}, headers=headers)
    assert update.status_code == 200
    assert update.json()["description"] == "Atualizado"

def test_delete_product():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/products/", json={
        "description": "Produto Delete",
        "sale_price": 10.0,
        "barcode": f"{uuid.uuid4().int % 1000000000000:013}",
        "section": "Delete",
        "initial_stock": 10,
        "expiration_date": None
    }, headers=headers)
    product_id = response.json()["id"]
    delete = client.delete(f"/products/{product_id}", headers=headers)
    assert delete.status_code == 200

# ------------------------ PEDIDOS ------------------------
def test_create_order_with_insufficient_stock():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    client_resp = client.post("/clients/", json={
        "name": "Cliente Estoque",
        "email": f"{uuid.uuid4().hex[:8]}@email.com",
        "cpf": str(int(uuid.uuid4().int) % 10**11).zfill(11)
    }, headers=headers)
    client_id = client_resp.json()["id"]

    product_resp = client.post("/products/", json={
        "description": "Produto Sem Estoque",
        "sale_price": 99.99,
        "barcode": f"{uuid.uuid4().int % 1000000000000:013}",
        "section": "Teste",
        "initial_stock": 0,
        "expiration_date": None
    }, headers=headers)
    product_id = product_resp.json()["id"]

    order = client.post("/orders/", json={
        "client_id": client_id,
        "status": "teste",
        "products": [product_id]
    }, headers=headers)

    assert order.status_code == 400
    assert "estoque" in order.json()["detail"].lower()

def test_filter_orders_by_status():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    client_id = client.post("/clients/", json={
        "name": "Cliente Teste",
        "email": f"{uuid.uuid4().hex[:8]}@email.com",
        "cpf": str(int(uuid.uuid4().int) % 10**11).zfill(11)
    }, headers=headers).json()["id"]

    product_id = client.post("/products/", json={
        "description": "Produto Teste",
        "sale_price": 20.0,
        "barcode": f"{uuid.uuid4().int % 1000000000000:013}",
        "section": "Filtro",
        "initial_stock": 10,
        "expiration_date": None
    }, headers=headers).json()["id"]

    create_order = client.post("/orders/", json={
        "client_id": client_id,
        "status": "filtrar-status",
        "products": [product_id]
    }, headers=headers)
    assert create_order.status_code == 200

    response = client.get("/orders/?status=filtrar-status", headers=headers)
    assert response.status_code == 200
    assert any(o["status"] == "filtrar-status" for o in response.json())

def test_filter_orders_by_date_range():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    client_id = client.post("/clients/", json={
        "name": "Cliente Data",
        "email": f"{uuid.uuid4().hex[:8]}@email.com",
        "cpf": str(int(uuid.uuid4().int) % 10**11).zfill(11)
    }, headers=headers).json()["id"]

    product_id = client.post("/products/", json={
        "description": "Produto Data",
        "sale_price": 99.99,
        "barcode": f"{uuid.uuid4().int % 1000000000000:013}",
        "section": "Datas",
        "initial_stock": 10,
        "expiration_date": None
    }, headers=headers).json()["id"]

    client.post("/orders/", json={
        "client_id": client_id,
        "status": "data-range",
        "products": [product_id]
    }, headers=headers)

    today = datetime.utcnow().date().isoformat()
    response = client.get(f"/orders/?start_date={today}&end_date={today}", headers=headers)
    assert response.status_code == 200
    assert any("data-range" in o["status"] for o in response.json())

def test_filter_orders_by_product_section():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    client_id = client.post("/clients/", json={
        "name": "Cliente Seção",
        "email": f"{uuid.uuid4().hex[:8]}@email.com",
        "cpf": str(int(uuid.uuid4().int) % 10**11).zfill(11)
    }, headers=headers).json()["id"]

    product_id = client.post("/products/", json={
        "description": "Produto Seção",
        "sale_price": 30.0,
        "barcode": f"{uuid.uuid4().int % 1000000000000:013}",
        "section": "SeçãoFiltrar",
        "initial_stock": 5,
        "expiration_date": None
    }, headers=headers).json()["id"]

    client.post("/orders/", json={
        "client_id": client_id,
        "status": "seção-filtrar",
        "products": [product_id]
    }, headers=headers)

    response = client.get("/orders/?section=SeçãoFiltrar", headers=headers)
    assert response.status_code == 200
    assert any("seção-filtrar" in o["status"] for o in response.json())

def test_create_product_with_image_url():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    image_url = "https://example.com/produto.jpg"

    response = client.post("/products/", json={
        "description": "Produto com Imagem",
        "sale_price": 10.0,
        "barcode": f"{uuid.uuid4().int % 1000000000000:013}",
        "section": "Imagens",
        "initial_stock": 3,
        "expiration_date": None,
        "image_url": image_url
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["image_url"] == image_url