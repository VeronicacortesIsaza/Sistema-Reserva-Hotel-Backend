"""
API de Tipos de Habitación
Este módulo define los endpoints para la gestión de tipos de habitación en el sistema de reservas de hotel.
API de Tipos de Habitación - Endpoints para la gestión de tipos de habitación en el sistema de reservas de hotel.
Endpoints:
- GET /TipoDeHabitacion/:
    Obtiene una lista paginada de todos los tipos de habitación registrados.
    Parámetros opcionales: skip (int), limit (int).
    Respuesta: Lista de objetos TipoHabitacionResponse.
- GET /TipoDeHabitacion/{id_tipo}:
    Obtiene la información de un tipo de habitación específico por su UUID.
    Parámetros: id_tipo (UUID).
    Respuesta: Objeto TipoHabitacionResponse.
- POST /TipoDeHabitacion/:
    Crea un nuevo tipo de habitación.
    Cuerpo de la solicitud: TipoHabitacionCreate.
    Respuesta: Objeto TipoHabitacionResponse con el tipo de habitación creado.
- PUT /TipoDeHabitacion/{id_tipo}:
    Actualiza los datos de un tipo de habitación existente.
    Parámetros: id_tipo (UUID).
    Cuerpo de la solicitud: TipoHabitacionUpdate.
    Respuesta: Objeto TipoHabitacionResponse actualizado.
- DELETE /TipoDeHabitacion/{id_tipo}:
    Elimina un tipo de habitación por su UUID.
    Parámetros: id_tipo (UUID).
    Respuesta: Objeto RespuestaAPI indicando el éxito o fallo de la operación.
Manejo de errores:
- Devuelve HTTP 404 si el tipo de habitación no existe.
- Devuelve HTTP 400 para errores de validación.
- Devuelve HTTP 500 para errores internos del servidor.
Dependencias:
- Requiere una sesión de base de datos proporcionada por get_db.
- Utiliza el CRUD de TipoHabitacion para las operaciones de base de datos.
"""

from typing import List
from uuid import UUID

from crud.tipo_habitacion_crud import TipoHabitacionCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import (
    RespuestaAPI,
    TipoHabitacionResponse,
    TipoHabitacionUpdate,
    TipoHabitacionCreate,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/TipoDeHabitacion", tags=["TipoDeHabitacion"])


@router.get("/", response_model=List[TipoHabitacionResponse])
async def obtener_tipos_habitacion(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los tipos de habitacion con paginación."""
    try:
        tipo_habitacion_crud = TipoHabitacionCRUD(db)
        tipos_habitacion = tipo_habitacion_crud.obtener_tipos_habitacion(db)
        return tipos_habitacion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los tipos de habitacion: {str(e)}",
        )


@router.get("/{id_tipo}", response_model=TipoHabitacionResponse)
async def obtener_tipo_habitacion(id_tipo: UUID, db: Session = Depends(get_db)):
    """Obtener los tipos de habitacion por ID."""
    try:
        tipo_habitacion_crud = TipoHabitacionCRUD(db)
        tipo_habitacion = tipo_habitacion_crud.obtener_tipo_habitacion(db, id_tipo)
        return tipo_habitacion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el tipo de habitacion: {str(e)}",
        )


@router.post(
    "/", response_model=TipoHabitacionResponse, status_code=status.HTTP_201_CREATED
)
async def crear_tipo_habitacion(
    tipo: TipoHabitacionCreate, db: Session = Depends(get_db)
):
    """Crear un nuevo tipo de habitación."""
    try:
        tipo_habitacion_crud = TipoHabitacionCRUD(db)
        tipo_habitacion = tipo_habitacion_crud.crear_tipo_habitacion(db, tipo)
        return tipo_habitacion
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear un tipo de habitación: {str(e)}",
        )


@router.put("/{id_tipo}", response_model=TipoHabitacionResponse)
async def actualizar_tipo_habitacion(
    id_tipo: UUID, tipo_data: TipoHabitacionUpdate, db: Session = Depends(get_db)
):
    """Actualizar un tipo de habitación existente."""
    try:
        tipo_habitacion_crud = TipoHabitacionCRUD(db)

        tipo_existente = tipo_habitacion_crud.obtener_tipo_habitacion(db, id_tipo)
        if not tipo_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de habitación no encontrado",
            )
        campos_actualizacion = {
            "nombre_tipo": tipo_data.nombre_tipo,
            "descripcion": tipo_data.descripcion,
            "id_usuario_edita": tipo_data.id_usuario_edita,
        }
        campos_actualizacion = {
            k: v for k, v in tipo_data.dict().items() if v is not None
        }

        if not campos_actualizacion:
            return tipo_existente

        tipo_actualizado = tipo_habitacion_crud.actualizar_tipo_habitacion(
            db, id_tipo, **campos_actualizacion
        )
        return tipo_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar usuario: {str(e)}",
        )


@router.delete("/{id_tipo}", response_model=RespuestaAPI)
async def eliminar_tipo_habitacion(id_tipo: UUID, db: Session = Depends(get_db)):
    """Eliminar un tipo de habitación."""
    try:
        tipo_habitacion_crud = TipoHabitacionCRUD(db)

        tipo_existente = tipo_habitacion_crud.obtener_tipo_habitacion(db, id_tipo)
        if not tipo_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de habitación no encontrado",
            )

        eliminado = tipo_habitacion_crud.eliminar_tipo_habitacion(db, id_tipo)
        if eliminado:
            return RespuestaAPI(
                mensaje="Tipo de habitación eliminado exitosamente", exito=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar tipo de habitación",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar tipo de habitación: {str(e)}",
        )
