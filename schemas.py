"""
Este módulo define los esquemas Pydantic para un sistema de gestión hotelera, incluyendo autenticación de usuarios, tipos de habitaciones, habitaciones, servicios adicionales, reservas y servicios de reserva.
Clases:
- UsuarioLogin: Esquema para credenciales de inicio de sesión de usuario.
- CambioContraseña: Esquema para el cambio de contraseña de usuario.
- RespuestaAPI: Esquema estándar de respuesta de API.
- UsuarioBase: Esquema base para información de usuario.
- UsuarioCreate: Esquema para la creación de un nuevo usuario.
- UsuarioUpdate: Esquema para la actualización de información de usuario.
- UsuarioResponse: Esquema para retornar información de usuario, incluyendo metadatos.
- TipoHabitacionBase: Esquema base para información de tipo de habitación.
- TipoHabitacionCreate: Esquema para la creación de un nuevo tipo de habitación.
- TipoHabitacionUpdate: Esquema para la actualización de tipo de habitación.
- TipoHabitacionResponse: Esquema para retornar información de tipo de habitación, incluyendo metadatos.
- HabitacionBase: Esquema base para información de habitación.
- HabitacionCreate: Esquema para la creación de una nueva habitación.
- HabitacionUpdate: Esquema para la actualización de información de habitación.
- HabitacionResponse: Esquema para retornar información de habitación, incluyendo metadatos.
- ServicioAdicionalBase: Esquema base para información de servicio adicional.
- ServicioAdicionalCreate: Esquema para la creación de un nuevo servicio adicional.
- ServicioAdicionalUpdate: Esquema para la actualización de servicio adicional.
- ServicioAdicionalResponse: Esquema para retornar información de servicio adicional, incluyendo metadatos.
- ReservaBase: Esquema base para información de reserva.
- ReservaCreate: Esquema para la creación de una nueva reserva.
- ReservaUpdate: Esquema para la actualización de información de reserva.
- ReservaResponse: Esquema para retornar información de reserva, incluyendo usuario relacionado y metadatos.
- ReservaServicioBase: Esquema base para la relación reserva-servicio.
- ReservaServicioCreate: Esquema para la creación de una nueva relación reserva-servicio.
- ReservaServicioResponse: Esquema para retornar la relación reserva-servicio, incluyendo información relacionada de reserva y servicio.
Todos los esquemas utilizan BaseModel de Pydantic para validación y serialización de datos.
"""

from datetime import datetime, date
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel
import re


class UsuarioLogin(BaseModel):
    nombre_usuario: str
    clave: str


class CambioContraseña(BaseModel):
    clave_actual: str
    clave_nueva: str


class RespuestaAPI(BaseModel):
    exito: bool
    mensaje: str
    datos: Optional[Any] = None


class UsuarioBase(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    tipo_usuario: Optional[str] = None
    nombre_usuario: Optional[str] = None
    clave: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_edicion: Optional[datetime] = None


class UsuarioCreate(UsuarioBase):
    pass


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    nombre_usuario: Optional[str] = None
    clave: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id_usuario: UUID
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime]

    class Config:
        from_attributes = True


class TipoHabitacionBase(BaseModel):
    nombre_tipo: Optional[str] = None
    descripcion: Optional[str] = None


class TipoHabitacionCreate(TipoHabitacionBase):
    id_usuario_crea: Optional[UUID] = None


class TipoHabitacionUpdate(BaseModel):
    nombre_tipo: Optional[str] = None
    descripcion: Optional[str] = None
    id_usuario_edita: Optional[UUID] = None


class TipoHabitacionResponse(TipoHabitacionBase):
    id_tipo: UUID
    id_usuario_crea: UUID
    id_usuario_edita: Optional[UUID] = None
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime]

    class Config:
        from_attributes = True


class HabitacionBase(BaseModel):
    numero: Optional[int] = None
    id_tipo: Optional[UUID] = None
    precio: Optional[float] = None
    disponible: bool = True
    id_usuario_crea: Optional[UUID] = None


class HabitacionCreate(HabitacionBase):
    pass


class HabitacionUpdate(BaseModel):
    numero: Optional[int] = None
    id_tipo: Optional[UUID] = None
    precio: Optional[float] = None
    disponible: Optional[bool] = None
    id_usuario_edita: Optional[UUID] = None


class HabitacionResponse(HabitacionBase):
    id_habitacion: UUID
    id_tipo: UUID
    tipo: str
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime]

    class Config:
        from_attributes = True


class ServicioAdicionalBase(BaseModel):
    nombre_servicio: Optional[str] = None
    precio: Optional[float] = None
    descripcion: Optional[str] = None
    id_usuario_crea: Optional[UUID] = None

class ServicioAdicionalCreate(ServicioAdicionalBase):
    pass


class ServicioAdicionalUpdate(BaseModel):
    nombre_servicio: Optional[str] = None
    precio: Optional[float] = None
    descripcion: Optional[str] = None
    id_usuario_edita: Optional[UUID] = None


class ServicioAdicionalResponse(ServicioAdicionalBase):
    id_servicio: UUID
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime]

    class Config:
        from_attributes = True


class ReservaBase(BaseModel):
    
    fecha_entrada: Optional[date] = None
    numero_de_personas: Optional[int] = None
    noches: Optional[int] = None
    estado_reserva: Optional[str] = None


class ReservaCreate(ReservaBase):
    id_usuario: Optional[UUID] = None
    id_habitacion: Optional[UUID] = None


class ReservaUpdate(BaseModel):
    fecha_entrada: Optional[date] = None
    estado_reserva: Optional[str] = None
    numero_de_personas: Optional[int] = None
    noches: Optional[int] = None
    id_habitacion: Optional[UUID] = None
    id_usuario_edita: Optional[UUID] = None


class ReservaResponse(ReservaBase):
    id_reserva: UUID
    id_usuario: UUID
    id_habitacion: Optional[UUID] = None
    fecha_salida: Optional[date] = None
    costo_total: float
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime]

    usuario: Optional[UsuarioResponse] = None

    class Config:
        from_attributes = True


class ReservaServicioBase(BaseModel):
    id_reserva: Optional[UUID] = None
    id_servicio: Optional[UUID] = None


class ReservaServicioCreate(ReservaServicioBase):
    pass


class ReservaServicioResponse(ReservaServicioBase):
    reserva: Optional[ReservaResponse] = None
    servicio: Optional[ServicioAdicionalResponse] = None

    class Config:
        from_attributes = True

class UsuarioAuthResponse(BaseModel):
    usuario: UsuarioResponse
    access_token: str
    token_type: str = "bearer"