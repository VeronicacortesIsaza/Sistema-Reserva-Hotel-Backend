from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.config import get_db
from crud.usuario_crud import UsuarioCRUD
from schemas import UsuarioLogin, UsuarioAuthResponse
from utils.jwt_manager import crear_token

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/login", response_model=UsuarioAuthResponse)
def login(login_data: UsuarioLogin, db: Session = Depends(get_db)):
    """Autenticar un usuario con nombre de usuario y clave, devolver JWT"""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.autenticar_usuario(
            db, login_data.nombre_usuario, login_data.clave
        )

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas o usuario inactivo",
            )

        token = crear_token({
            "sub": str(usuario.id_usuario),
            "nombre_usuario": usuario.nombre_usuario,
            "tipo_usuario": usuario.tipo_usuario
        })

        return {
            "usuario": {
                "id_usuario": str(usuario.id_usuario),
                "nombre": usuario.nombre,
                "apellidos": usuario.apellidos,
                "nombre_usuario": usuario.nombre_usuario,
                "tipo_usuario": usuario.tipo_usuario,
                "fecha_creacion": usuario.fecha_creacion,
                "fecha_edicion": usuario.fecha_edicion,
            },
            "access_token": token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el login: {str(e)}",
        )