from sqlalchemy import Column, UUID, ForeignKey
from sqlalchemy.orm import relationship
from database.config import Base


class Reserva_Servicios(Base):
    """
    Representa la tabla de asociación entre las entidades Reserva y Servicios_Adicionales.
    Esta clase define una relación de varios a varios entre reservas y servicios adicionales.
    Cada instancia vincula una reserva (`id_reserva`) con un servicio adicional (`id_servicio`).
    """

    __tablename__ = "reserva_servicios"

    id_reserva = Column(
        UUID(as_uuid=True), ForeignKey("reserva.id_reserva"), primary_key=True
    )
    id_servicio = Column(
        UUID(as_uuid=True),
        ForeignKey("servicios_adicionales.id_servicio"),
        primary_key=True,
    )

    reserva = relationship("Reserva", back_populates="servicios")
    servicio = relationship(
        "Servicios_Adicionales", back_populates="reservas_servicios"
    )

    def __repr__(self):
        return f"<Reserva_Servicios(id_reserva={self.id_reserva}, id_servicio={self.id_servicio})>"
