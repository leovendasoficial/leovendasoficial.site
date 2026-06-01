import os
import time
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

JWT_SECRET = os.getenv("ADMIN_JWT_SECRET", "change-me-super-secret")
JWT_EXPIRE_SECONDS = int(os.getenv("ADMIN_JWT_EXPIRE_SECONDS", "86400"))  # 24h

# Default admin: admin / admin123 (troque via variáveis de ambiente em produção)
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS_HASH = os.getenv("ADMIN_PASS_HASH", "")  # se vazio, usa senha default abaixo
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def _verify_password(plain: str) -> bool:
    if ADMIN_PASS_HASH:
        return pwd_context.verify(plain, ADMIN_PASS_HASH)
    # fallback simples
    return plain == DEFAULT_ADMIN_PASSWORD

def login(username: str, password: str) -> str:
    if username != ADMIN_USER or not _verify_password(password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    now = int(time.time())
    payload = {"sub": username, "iat": now, "exp": now + JWT_EXPIRE_SECONDS}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def require_admin(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub") or "admin"
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
