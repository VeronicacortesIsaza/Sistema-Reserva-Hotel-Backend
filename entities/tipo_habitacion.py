from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship
from database.config import Base
import uuid


class Tipo_Habitacion(Base):
    """
    Representa la entidad tipo de habitacion dentro del sistema de reservas del hotel
    """

    __tablename__ = "tipo_habitacion"

    id_tipo = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_tipo = Column(String)
    descripcion = Column(Text)
    id_usuario_crea = Column(
        UUID(as_uuid=True), ForeignKey("usuario.id_usuario"), nullable=False
    )
    id_usuario_edita = Column(
        UUID(as_uuid=True), ForeignKey("usuario.id_usuario"), nullable=True
    )
    fecha_creacion = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    fecha_edicion = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    habitaciones = relationship("Habitacion", back_populates="tipo_habitacion")

    usuario_crea = relationship(
        "Usuario",
        foreign_keys=[id_usuario_crea],
        back_populates="tipos_habitacion_creados",
    )
    usuario_edita = relationship(
        "Usuario",
        foreign_keys=[id_usuario_edita],
        back_populates="tipos_habitacion_editados",
    )

    def __repr__(self):
        return f"<Tipo_Habitacion(id={self.id_tipo}, nombre_tipo={self.nombre_tipo})>"
