from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from desafio_lu_estilo.database import get_db
from desafio_lu_estilo.models import UserORM, UserCreate, Token
router = APIRouter(prefix="/auth", tags=["Auth"])

# Configurações
SECRET_KEY = "minha_chave_secreta_super_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Funções auxiliares
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_user(db: Session, username: str, password: str):
    user = db.query(UserORM).filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# Endpoints
@router.post("/login", response_model=Token, summary="Login do usuário")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = verify_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")

@router.post("/register", status_code=201, summary="Registrar novo usuário", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserORM).filter_by(username=user.username).first():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    db_user = UserORM(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        is_admin=user.is_admin or False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Usuário criado com sucesso"}

@router.post("/refresh-token", response_model=Token, summary="Gerar novo token JWT")
def refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    new_token = create_access_token(data={"sub": username})
    return Token(access_token=new_token, token_type="bearer")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserORM:
    credentials_exception = HTTPException(status_code=401, detail="Token inválido")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UserORM).filter_by(username=username).first()
    if user is None:
        raise credentials_exception
    return user