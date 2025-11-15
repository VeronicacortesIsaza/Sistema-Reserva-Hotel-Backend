from sqlalchemy import String, Column, DateTime, func
from database.config import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship


class Usuario(Base):
    """
    Representa la entidad usuario
    """

    __tablename__ = "usuario"

    id_usuario = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    tipo_usuario = Column(String(20), nullable=False)
    nombre_usuario = Column(String(50), nullable=False, unique=True)
    clave = Column(String(10), nullable=False)
    fecha_creacion = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    fecha_edicion = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    habitaciones_creadas = relationship(
        "Habitacion",
        foreign_keys="[Habitacion.id_usuario_crea]",
        back_populates="usuario_crea",
    )
    habitaciones_editadas = relationship(
        "Habitacion",
        foreign_keys="[Habitacion.id_usuario_edita]",
        back_populates="usuario_edita",
    )

    servicios_creados = relationship(
        "Servicios_Adicionales",
        foreign_keys="[Servicios_Adicionales.id_usuario_crea]",
        back_populates="usuario_crea",
    )
    servicios_editados = relationship(
        "Servicios_Adicionales",
        foreign_keys="[Servicios_Adicionales.id_usuario_edita]",
        back_populates="usuario_edita",
    )

    tipos_habitacion_creados = relationship(
        "Tipo_Habitacion",
        foreign_keys="[Tipo_Habitacion.id_usuario_crea]",
        back_populates="usuario_crea",
    )
    tipos_habitacion_editados = relationship(
        "Tipo_Habitacion",
        foreign_keys="[Tipo_Habitacion.id_usuario_edita]",
        back_populates="usuario_edita",
    )

    reservas = relationship(
        "Reserva", foreign_keys="[Reserva.id_usuario]", back_populates="usuario"
    )
    reservas_creadas = relationship(
        "Reserva",
        foreign_keys="[Reserva.id_usuario_crea]",
        back_populates="usuario_crea",
    )
    reservas_editadas = relationship(
        "Reserva",
        foreign_keys="[Reserva.id_usuario_edita]",
        back_populates="usuario_edita",
    )

    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, nombre_usuario={self.nombre_usuario}, tipo={self.tipo_usuario})>"
