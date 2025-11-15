"""
    Módulo de endpoints para la gestión de servicios adicionales en el sistema de reservas de hotel.
    Este módulo define las rutas de la API para crear, obtener, actualizar y eliminar servicios adicionales.
    Utiliza FastAPI y SQLAlchemy para la gestión de peticiones y operaciones en la base de datos.
    Endpoints:
        - GET /servicios_adicionales/: Obtiene una lista de servicios adicionales.
        - GET /servicios_adicionales/{id_servicio}: Obtiene un servicio adicional por su ID.
        - POST /servicios_adicionales/: Crea un nuevo servicio adicional.
        - PUT /servicios_adicionales/{id_servicio}: Actualiza un servicio adicional existente.
        - DELETE /servicios_adicionales/{id_servicio}: Elimina un servicio adicional por su ID.
    Excepciones:
        - HTTP_404_NOT_FOUND: Cuando el servicio adicional no existe.
        - HTTP_400_BAD_REQUEST: Cuando los datos proporcionados no son válidos.
        - HTTP_500_INTERNAL_SERVER_ERROR: Para errores inesperados en el servidor.
    Retorna:
        - List[ServicioAdicionalResponse]: Lista de servicios adicionales.
        - ServicioAdicionalResponse: Detalle de un servicio adicional.
        - RespuestaAPI: Mensaje de éxito o error en operaciones de eliminación.
"""

from typing import List
from uuid import UUID

from crud.servicios_adicionales_crud import ServiciosAdicionalesCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from entities.servicios_adicionales import Servicios_Adicionales
from schemas import (
    RespuestaAPI,
    ServicioAdicionalCreate,
    ServicioAdicionalResponse,
    ServicioAdicionalUpdate,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/servicios_adicionales", tags=["servicios_adicionales"])


@router.get("/", response_model=List[ServicioAdicionalResponse])
async def obtener_servicios_adicionales(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    try:
        servicio_adicional_crud = ServiciosAdicionalesCRUD(db)
        servicios = servicio_adicional_crud.obtener_servicios(
            db, skip=skip, limit=limit
        )
        return servicios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener servicios: {str(e)}",
        )


@router.get("/{id_servicio}", response_model=ServicioAdicionalResponse)
async def obtener_servicio(id_servicio: UUID, db: Session = Depends(get_db)):
    try:
        servicio_adicional_crud = ServiciosAdicionalesCRUD(db)
        servicio = servicio_adicional_crud.obtener_servicio(db, id_servicio)
        if not servicio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado"
            )
        return servicio
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener servicio: {str(e)}",
        )


@router.post(
    "/", response_model=ServicioAdicionalResponse, status_code=status.HTTP_201_CREATED
)
async def crear_servicio(
    servicio_data: ServicioAdicionalCreate, db: Session = Depends(get_db)
):
    try:
        servicio_adicional_crud = ServiciosAdicionalesCRUD(db)
        servicio_nuevo = Servicios_Adicionales(
            nombre_servicio=servicio_data.nombre_servicio,
            descripcion=servicio_data.descripcion,
            precio=servicio_data.precio,
            id_usuario_crea=servicio_data.id_usuario_crea,
        )
        servicio = servicio_adicional_crud.crear_servicio(db, servicio_nuevo)
        return servicio
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear servicio adicional: {str(e)}",
        )


@router.put("/{id_servicio}", response_model=ServicioAdicionalResponse)
async def actualizar_servicio(
    id_servicio: UUID,
    servicio_data: ServicioAdicionalUpdate,
    db: Session = Depends(get_db),
):
    try:
        servicio_adicional_crud = ServiciosAdicionalesCRUD(db)
        servicio_existente = servicio_adicional_crud.obtener_servicio(db, id_servicio)
        if not servicio_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado"
            )
        campos_a_actualizar = servicio_data.dict(exclude_unset=True)
        servicio_actualizado = servicio_adicional_crud.actualizar_servicio(
            db, id_servicio, **campos_a_actualizar
        )
        return servicio_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar servicio: {str(e)}",
        )


@router.delete("/{id_servicio}", response_model=RespuestaAPI)
async def eliminar_servicio(id_servicio: UUID, db: Session = Depends(get_db)):
    try:
        servicio_adicional_crud = ServiciosAdicionalesCRUD(db)
        servicio_existente = servicio_adicional_crud.obtener_servicio(db, id_servicio)
        eliminado = servicio_adicional_crud.eliminar_servicio(
            db, servicio_existente.id_servicio
        )

        if eliminado:
            return RespuestaAPI(mensaje="Servicio eliminado exitosamente", exito=True)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar servicio: {str(e)}",
        )
