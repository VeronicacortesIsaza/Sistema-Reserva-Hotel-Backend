from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    String,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from database.config import Base
import uuid


class Habitacion(Base):
    """
    Representa la entidad de habitación de hotel.
    """

    __tablename__ = "habitacion"

    id_habitacion = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(Integer, nullable=False, unique=True)
    id_tipo = Column(
        UUID(as_uuid=True), ForeignKey("tipo_habitacion.id_tipo"), nullable=False
    )
    tipo = Column(String(20), nullable=False)
    precio = Column(Float, nullable=False)
    disponible = Column(Boolean, default=True, nullable=False)

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

    tipo_habitacion = relationship("Tipo_Habitacion", back_populates="habitaciones")
    reservas = relationship("Reserva", back_populates="habitacion")

    usuario_crea = relationship(
        "Usuario", foreign_keys=[id_usuario_crea], back_populates="habitaciones_creadas"
    )
    usuario_edita = relationship(
        "Usuario",
        foreign_keys=[id_usuario_edita],
        back_populates="habitaciones_editadas",
    )

    def __repr__(self):
        return f"<Habitacion(id={self.id_habitacion}, numero={self.numero}, tipo={self.tipo}, precio={self.precio}, disponible={self.disponible})>"
