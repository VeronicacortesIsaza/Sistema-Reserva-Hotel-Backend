from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Float, func
from sqlalchemy.orm import relationship
from database.config import Base
import uuid


class Servicios_Adicionales(Base):
    """_
    Representa la entidad servicios adicionales
    """

    __tablename__ = "servicios_adicionales"

    id_servicio = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_servicio = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    descripcion = Column(String, nullable=False)
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

    reservas_servicios = relationship("Reserva_Servicios", back_populates="servicio")

    usuario_crea = relationship(
        "Usuario", foreign_keys=[id_usuario_crea], back_populates="servicios_creados"
    )
    usuario_edita = relationship(
        "Usuario", foreign_keys=[id_usuario_edita], back_populates="servicios_editados"
    )

    def __repr__(self):
        return f"<Servicios_Adicionales(id={self.id_servicio}, nombre={self.nombre_servicio}, precio={self.precio}), descripcion={self.descripcion})>"
