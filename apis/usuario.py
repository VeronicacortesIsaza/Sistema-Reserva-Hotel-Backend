"""
Este módulo define los endpoints relacionados con la gestión de usuarios en el sistema de reservas de hotel.
Incluye operaciones para crear, obtener, actualizar, eliminar usuarios, así como para cambiar contraseñas y filtrar usuarios por tipo (administrador o cliente).
Endpoints:
- GET /usuarios/ : Obtiene una lista paginada de todos los usuarios.
- GET /usuarios/{id_usuario} : Obtiene un usuario específico por su ID.
- GET /usuarios/nombreusuario/{nombre_usuario} : Obtiene un usuario por su nombre de usuario.
- POST /usuarios/ : Crea un nuevo usuario.
- PUT /usuarios/{id_usuario} : Actualiza completamente un usuario existente.
- DELETE /usuarios/{id_usuario} : Elimina un usuario por su ID.
- GET /usuarios/admin/lista : Obtiene una lista de todos los usuarios administradores.
- GET /usuarios/cliente/lista : Obtiene una lista de todos los usuarios clientes.
- PATCH /usuarios/{id_usuario} : Actualiza parcialmente la contraseña de un usuario.
Dependencias:
- FastAPI
- SQLAlchemy
- Esquemas y entidades personalizados para usuarios
- CRUD de usuario
Excepciones:
- HTTPException: Se utiliza para manejar errores y devolver respuestas HTTP adecuadas en caso de fallos en las operaciones.
"""

from typing import List
from uuid import UUID
from datetime import datetime

from crud.usuario_crud import UsuarioCRUD
from entities.usuario import Usuario
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import (
    CambioContraseña,
    RespuestaAPI,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
async def obtener_usuarios(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los usuarios con paginación."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuarios = usuario_crud.obtener_usuarios(db, skip=skip, limit=limit)
        return usuarios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}",
        )


@router.get("/{id_usuario}", response_model=UsuarioResponse)
async def obtener_usuario(id_usuario: UUID, db: Session = Depends(get_db)):
    """Obtener un usuario por ID."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.obtener_usuario(db, id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )
        return usuario
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}",
        )


@router.get("/nombreusuario/{nombre_usuario}", response_model=UsuarioResponse)
async def obtener_usuario_por_nombre_usuario(
    nombre_usuario: str, db: Session = Depends(get_db)
):
    """Obtener un usuario por nombre de usuario."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.obtener_usuario_por_nombre(db, nombre_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}",
        )


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario."""
    try:
        usuario_crud = UsuarioCRUD(db)
        nuevo_usuario = Usuario(
            nombre=usuario_data.nombre,
            apellidos=usuario_data.apellidos,
            telefono=usuario_data.telefono,
            tipo_usuario=usuario_data.tipo_usuario,
            nombre_usuario=usuario_data.nombre_usuario,
            clave=usuario_data.clave,
            fecha_creacion=datetime.now(),
        )
        usuario = usuario_crud.crear_usuario(db, nuevo_usuario)
        return usuario
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}",
        )


@router.put("/{id_usuario}", response_model=UsuarioResponse)
async def actualizar_usuario(
    id_usuario: UUID, usuario_data: UsuarioUpdate, db: Session = Depends(get_db)
):
    """Actualizar un usuario existente."""
    try:
        usuario_crud = UsuarioCRUD(db)

        usuario_existente = usuario_crud.obtener_usuario(db, id_usuario)
        if not usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        campos_actualizacion = {
            k: v for k, v in usuario_data.dict().items() if v is not None
        }

        if not campos_actualizacion:
            return usuario_existente

        usuario_actualizado = usuario_crud.actualizar_usuario(
            db, id_usuario, id_usuario_edita=id_usuario, **campos_actualizacion
        )
        return usuario_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar usuario: {str(e)}",
        )


@router.delete("/{id_usuario}", response_model=RespuestaAPI)
async def eliminar_usuario(id_usuario: UUID, db: Session = Depends(get_db)):
    """Eliminar un usuario."""
    try:
        usuario_crud = UsuarioCRUD(db)

        usuario_existente = usuario_crud.obtener_usuario(db, id_usuario)
        if not usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        eliminado = usuario_crud.eliminar_usuario(db, id_usuario)
        if eliminado:
            return RespuestaAPI(mensaje="Usuario eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar usuario",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar usuario: {str(e)}",
        )


@router.get("/admin/lista", response_model=List[UsuarioResponse])
async def obtener_usuarios_admin(db: Session = Depends(get_db)):
    """Obtener todos los usuarios administradores."""
    try:
        usuario_crud = UsuarioCRUD(db)
        admins = usuario_crud.obtener_usuarios_admin(db)
        return admins
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener administradores: {str(e)}",
        )


@router.get("/cliente/lista", response_model=List[UsuarioResponse])
async def obtener_usuarios_cliente(db: Session = Depends(get_db)):
    """Obtener todos los usuarios clientes."""
    try:
        usuario_crud = UsuarioCRUD(db)
        clientes = usuario_crud.obtener_usuarios_cliente(db)
        return clientes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clientes: {str(e)}",
        )


@router.patch("/{id_usuario}", response_model=UsuarioResponse)
async def actualizar_clave_usuario(
    id_usuario: UUID, usuario_data: CambioContraseña, db: Session = Depends(get_db)
):
    """Actualizar parcialmente un usuario (solo los campos enviados)."""
    try:
        usuario_crud = UsuarioCRUD(db)
        campos_actualizacion = {
            k: v for k, v in usuario_data.dict().items() if v is not None
        }
        usuario_actualizado = usuario_crud.cambio_contraseña(
            db,
            id_usuario,
            clave_actual=usuario_data.clave_actual,
            clave_nueva=usuario_data.clave_nueva,
        )
        return usuario_actualizado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")
