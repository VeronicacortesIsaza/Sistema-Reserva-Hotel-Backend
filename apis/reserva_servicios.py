"""
Este módulo proporciona endpoints RESTful para crear, obtener y eliminar asociaciones entre reservas y servicios adicionales en un sistema de reservas de hotel. Utiliza FastAPI para la definición de rutas y SQLAlchemy para la interacción con la base de datos.
Endpoints disponibles:
Excepciones manejadas:
Módulo de API para gestionar la relación entre reservas y servicios adicionales.
Proporciona endpoints para crear, obtener y eliminar asociaciones entre reservas y servicios adicionales.
Utiliza FastAPI y SQLAlchemy para manejar las solicitudes y operaciones de base de datos.
Endpoints:
- GET /reserva_servicios/ : Obtiene todas las asociaciones de reservas con servicios adicionales.
- POST /reserva_servicios/ : Crea una nueva asociación entre una reserva y un servicio adicional.
- DELETE /reserva_servicios/{id_reserva} : Elimina una asociación entre una reserva y un servicio adicional.
- GET /reserva_servicios/reserva/{id_reserva} : Obtiene todos los servicios adicionales asociados a una reserva específica.
- GET /reserva_servicios/servicio/{id_servicio} : Obtiene todas las reservas que tienen asociado un servicio adicional específico.
Excepciones:
- HTTP_404_NOT_FOUND: Cuando la reserva o servicio adicional no existe.
- HTTP_400_BAD_REQUEST: Cuando los datos proporcionados no son válidos.
- HTTP_500_INTERNAL_SERVER_ERROR: Para errores inesperados en el servidor.
Retorna:
- List[ReservaServicioResponse]: Lista de asociaciones reserva-servicio.
- ReservaServicioResponse: Detalle de una asociación reserva-servicio.
- RespuestaAPI: Mensaje de éxito o error en operaciones de eliminación.
"""

from typing import List
from uuid import UUID

from crud.reserva_servicios_crud import ReservaServiciosCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from entities.reserva_servicios import Reserva_Servicios
from schemas import (
    RespuestaAPI,
    ReservaServicioCreate,
    ReservaServicioResponse,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reserva_servicios", tags=["reserva_servicios"])


@router.get("/", response_model=List[ReservaServicioResponse])
async def obtener_reservas_servicios(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
):
    """Obtener todos los registros de reservas con sus servicios adicionales."""
    try:
        reservas_servicios_crud = ReservaServiciosCRUD(db)
        registros = reservas_servicios_crud.obtener_reservas_servicios(
            db, skip=skip, limit=limit
        )
        return registros
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener reservas-servicios: {str(e)}",
        )


@router.post(
    "/", response_model=ReservaServicioResponse, status_code=status.HTTP_201_CREATED
)
async def crear_reserva_servicio(
    reserva_servicio_data: ReservaServicioCreate, db: Session = Depends(get_db)
):
    """Asociar un servicio adicional a una reserva existente."""
    try:
        reservas_servicios_crud = ReservaServiciosCRUD(db)
        nuevo_registro = Reserva_Servicios(
            id_reserva=reserva_servicio_data.id_reserva,
            id_servicio=reserva_servicio_data.id_servicio,
        )

        registro = reservas_servicios_crud.crear_reserva_servicio(db, nuevo_registro)
        return registro
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear reserva-servicio: {str(e)}",
        )


@router.delete("/{id_reserva}", response_model=RespuestaAPI)
async def eliminar_reserva_servicio(id_reserva: UUID, db: Session = Depends(get_db)):
    """Eliminar un vínculo entre una reserva y un servicio adicional."""
    try:
        reservas_servicios_crud = ReservaServiciosCRUD(db)
        eliminado = reservas_servicios_crud.eliminar_reserva_servicio(db, id_reserva)
        if eliminado:
            return RespuestaAPI(
                mensaje="Reserva-servicio eliminada exitosamente",
                exito=True,
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar reserva-servicio: {str(e)}",
        )


@router.get("/reserva/{id_reserva}", response_model=List[ReservaServicioResponse])
async def obtener_servicios_por_reserva(
    id_reserva: UUID, db: Session = Depends(get_db)
):
    """Obtener todos los servicios adicionales asociados a una reserva específica."""
    try:
        reservas_servicios_crud = ReservaServiciosCRUD(db)
        registros = reservas_servicios_crud.obtener_servicios_por_reserva(
            db, id_reserva
        )
        return registros
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener servicios por reserva: {str(e)}",
        )


@router.get("/servicio/{id_servicio}", response_model=List[ReservaServicioResponse])
async def obtener_reservas_por_servicio(
    id_servicio: UUID, db: Session = Depends(get_db)
):
    """Obtener todas las reservas que tienen asociado un servicio adicional específico."""
    try:
        reservas_servicios_crud = ReservaServiciosCRUD(db)
        registros = reservas_servicios_crud.obtener_reservas_por_servicio(
            db, id_servicio
        )
        return registros
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener reservas por servicio: {str(e)}",
        )
