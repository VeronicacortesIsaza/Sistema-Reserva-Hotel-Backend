from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from entities.reserva_servicios import Reserva_Servicios
from entities.reserva import Reserva
from entities.servicios_adicionales import Servicios_Adicionales
from sqlalchemy.orm import joinedload


class ReservaServiciosCRUD:
    """
    Módulo CRUD para la entidad Reserva_Servicios.

    Administra la relación entre las reservas y los servicios adicionales contratados.

    Funciones principales:
        - crear_reserva_servicio(db: Session, reserva_servicio: Reserva_Servicios) -> Reserva_Servicios
        - obtener_reserva_servicio(db: Session, id_reserva_servicio: UUID) -> Reserva_Servicios
        - obtener_reservas_servicios(db: Session, skip: int = 0, limit: int = 100) -> List[Reserva_Servicios]
        - eliminar_reserva_servicio(db: Session, id_reserva_servicio: UUID) -> bool
    """

    def __init__(self, db):
        self.db = db

    @staticmethod
    def crear_reserva_servicio(db: Session, reserva_servicio: Reserva_Servicios):
        if not reserva_servicio.id_reserva:
            raise ValueError("El registro debe estar asociado a una reserva")

        reserva = (
            db.query(Reserva)
            .filter(Reserva.id_reserva == reserva_servicio.id_reserva)
            .first()
        )
        if not reserva:
            raise ValueError("La reserva asociada no existe")
        if not reserva_servicio.id_servicio:
            raise ValueError("El registro debe estar asociado a un servicio adicional")

        servicio = (
            db.query(Servicios_Adicionales)
            .filter(Servicios_Adicionales.id_servicio == reserva_servicio.id_servicio)
            .first()
        )
        if not servicio:
            raise ValueError("El servicio asociado no existe")

        reserva.costo_total += servicio.precio

        nuevo_registro = Reserva_Servicios(
            id_reserva=reserva_servicio.id_reserva,
            id_servicio=reserva_servicio.id_servicio,
        )

        db.add(nuevo_registro)
        db.commit()
        db.refresh(nuevo_registro)

        return nuevo_registro
    
    @staticmethod
    def obtener_reservas_servicios(db: Session, skip: int = 0, limit: int = 100):
        reservas_servicios = (
            db.query(Reserva_Servicios)
            .options(
                joinedload(Reserva_Servicios.reserva).joinedload(Reserva.usuario),
                joinedload(Reserva_Servicios.servicio)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        return reservas_servicios

    @staticmethod
    def obtener_servicios_por_reserva(db: Session, id_reserva: UUID):
        servicios = (
            db.query(Reserva_Servicios)
            .options(
                joinedload(Reserva_Servicios.reserva).joinedload(Reserva.usuario),
                joinedload(Reserva_Servicios.servicio)
            )
            .filter(Reserva_Servicios.id_reserva == id_reserva)
            .all()
        )

        reserva = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
        if not reserva:
            raise ValueError("La reserva especificada no existe")

        return servicios

    @staticmethod
    def obtener_reservas_por_servicio(db: Session, id_servicio: UUID):
        reservas = (
            db.query(Reserva_Servicios)
            .filter(Reserva_Servicios.id_servicio == id_servicio)
            .all()
        )
        servicio = (
            db.query(Servicios_Adicionales)
            .filter(Servicios_Adicionales.id_servicio == id_servicio)
            .first()
        )
        if not servicio:
            raise ValueError("El servicio adicional especificado no existe")
        if not reservas:
            raise ValueError("No hay reservas asociadas a este servicio adicional")
        return reservas

    @staticmethod
    def eliminar_reserva_servicio(db: Session, id_reserva: UUID) -> bool:
        rs = (
            db.query(Reserva_Servicios)
            .filter(Reserva_Servicios.id_reserva == id_reserva)
            .first()
        )
        if not rs:
            raise ValueError("Reserva-Servicio no encontrado")
        db.delete(rs)
        db.commit()
        return True
