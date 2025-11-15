from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "tu_clave_super_secreta"
ALGORITHM = "HS256"

def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt