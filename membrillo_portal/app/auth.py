"""Autenticacion por token (Bearer) para la API JSON.

Hash de contrasenas con bcrypt. Token firmado con itsdangerous (sin tabla nueva).
Dependencias FastAPI para exigir sesion / rol admin via header Authorization.
"""
import os
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy.orm import Session

from . import models
from .db import get_db

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-membrillo")
TOKEN_MAX_AGE = 8 * 60 * 60  # 8 horas
_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="membrillo-auth")

# auto_error=False -> permite endpoints donde el token es opcional
_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def autenticar(db: Session, email: str, password: str) -> Optional[models.Usuario]:
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if user and user.activo and verify_password(password, user.hashed_password):
        return user
    return None


# ----------- Tokens -----------

def crear_token(user: models.Usuario) -> str:
    return _serializer.dumps({"user_id": user.id, "rol": user.rol})


def leer_token(token: str) -> Optional[dict]:
    try:
        return _serializer.loads(token, max_age=TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def usuario_token(db: Session, token: Optional[str]) -> Optional[models.Usuario]:
    if not token:
        return None
    data = leer_token(token)
    if not data:
        return None
    return db.query(models.Usuario).filter(
        models.Usuario.id == data["user_id"], models.Usuario.activo == 1
    ).first()


def serializar_usuario(user: models.Usuario) -> dict:
    return {"id": user.id, "nombre": user.nombre, "email": user.email,
            "rol": user.rol, "cliente_id": user.cliente_id}


# ----------- Dependencias -----------

def usuario_opcional(
    cred: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Optional[models.Usuario]:
    token = cred.credentials if cred else None
    return usuario_token(db, token)


def bearer_user(
    cred: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> models.Usuario:
    user = usuario_token(db, cred.credentials if cred else None)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No autenticado")
    return user


def bearer_admin(
    cred: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> models.Usuario:
    user = usuario_token(db, cred.credentials if cred else None)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No autenticado")
    if user.rol != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acceso solo para administradores")
    return user


def asegurar_admin(db: Session) -> None:
    """Crea el usuario admin por defecto si no existe (demo academico)."""
    email = os.getenv("ADMIN_EMAIL", "admin@membrillo.gt")
    if db.query(models.Usuario).filter(models.Usuario.email == email).first():
        return
    password = os.getenv("ADMIN_PASSWORD", "membrillo123")
    admin = models.Usuario(
        nombre="Administrador",
        email=email,
        hashed_password=hash_password(password),
        rol="admin",
        activo=1,
    )
    db.add(admin)
    db.commit()
