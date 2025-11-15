from datetime import datetime
from sqlalchemy import true, func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from entities.habitacion import Habitacion
from entities.tipo_habitacion import Tipo_Habitacion
from entities.usuario import Usuario
from entities.reserva import Reserva
from fastapi import HTTPException


class HabitacionCRUD:
    """
    Módulo CRUD para la entidad Habitación.

    Define las operaciones relacionadas con la gestión de habitaciones en el hotel.
    Incluye validaciones de número único y precio positivo.

    Funciones principales:
        - crear_habitacion(db: Session, habitacion: Habitacion) -> Habitacion
        - obtener_habitacion(db: Session, id_habitacion: UUID) -> Habitacion
        - obtener_habitaciones(db: Session) -> List[Habitacion]
        - actualizar_habitacion(db: Session, id_habitacion: UUID, **kwargs) -> Habitacion
        - eliminar_habitacion(db: Session, id_habitacion: UUID) -> bool
    """

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def crear_habitacion(db: Session, habitacion: Habitacion):
        try:
            if not habitacion.numero:
                raise ValueError("El número de la habitación es obligatorio")
            if habitacion.numero <= 0:
                raise ValueError("El numero de habitacion debe ser mayor a 0")

            if not habitacion.id_tipo:
                raise ValueError("El tipo de habitación es obligatorio")

            tipo_registro = (
                db.query(Tipo_Habitacion)
                .filter(Tipo_Habitacion.id_tipo == habitacion.id_tipo)
                .first()
            )
            if not tipo_registro:
                raise ValueError("El tipo de habitación no existe")

            if habitacion.precio is None:
                raise ValueError("El precio de la habitación es obligatorio")
            if habitacion.precio <= 0:
                raise ValueError("El precio debe ser mayor a 0")

            if habitacion.disponible is None:
                habitacion.disponible = True
            if habitacion.disponible not in {True, False}:
                raise ValueError("El campo 'disponible' debe ser True o False")

            existente = (
                db.query(Habitacion)
                .filter(Habitacion.numero == habitacion.numero)
                .first()
            )
            if existente:
                raise ValueError("El número de habitación ya está en uso")

            usuario_existe = (db.query(Usuario).filter(Usuario.id_usuario == habitacion.id_usuario_crea).first())
            if not usuario_existe:
                raise ValueError("El usuario que crea la habitación no existe.")
            habitacion.fecha_creacion = datetime.now()
            habitacion.id_tipo = tipo_registro.id_tipo
            habitacion.tipo = tipo_registro.nombre_tipo
            db.add(habitacion)
            db.commit()
            db.refresh(habitacion)
            return habitacion
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    @staticmethod
    def obtener_habitacion(db: Session, id_habitacion: UUID):
        return (
            db.query(Habitacion)
            .filter(Habitacion.id_habitacion == id_habitacion)
            .first()
        )

    @staticmethod
    def obtener_habitaciones(db: Session):
        habitaciones = db.query(Habitacion).all()
        if not habitaciones:
            raise ValueError("No hay habitaciones registradas")
        return habitaciones

    @staticmethod
    def obtener_habitaciones_disponibles(db: Session):
        habitaciones = db.query(Habitacion).filter(Habitacion.disponible == True).all()
        if not habitaciones:
            raise ValueError("No hay habitaciones disponibles")
        return habitaciones

    @staticmethod
    def actualizar_habitacion(db: Session, id_habitacion: UUID, **kwargs):
        try:
            habitacion = (
                db.query(Habitacion)
                .filter(Habitacion.id_habitacion == id_habitacion)
                .first()
            )
            if not habitacion:
                raise ValueError("Habitación no encontrada")

            if "id_usuario_edita" in kwargs:
                usuario = (
                    db.query(Usuario)
                    .filter(Usuario.id_usuario == kwargs["id_usuario_edita"])
                    .first()
                )
                if not usuario:
                    raise ValueError("El usuario que edita no existe")
                habitacion.id_usuario_edita = kwargs["id_usuario_edita"]

            if "disponible" in kwargs:
                habitacion.disponible = kwargs["disponible"]

            if "numero" in kwargs and kwargs["numero"] is not None:
                if kwargs["numero"] <= 0:
                    raise ValueError("El número de habitación debe ser mayor a 0")
                existente = (
                    db.query(Habitacion)
                    .filter(
                        Habitacion.numero == kwargs["numero"],
                        Habitacion.id_habitacion != id_habitacion,
                    )
                    .first()
                )
            if existente:
                raise ValueError("El número de habitación ya está en uso")

            if "precio" in kwargs and kwargs["precio"] is not None:
                if kwargs["precio"] < 0:
                    raise ValueError("El precio debe ser mayor o igual a 0")
            habitacion.fecha_edicion = datetime.now()
            for key, value in kwargs.items():
                if hasattr(habitacion, key) and value is not None:
                    setattr(habitacion, key, value)

            db.commit()
            db.refresh(habitacion)
            return habitacion
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def eliminar_habitacion(db: Session, id_habitacion: UUID) -> bool:
        habitacion = (
            db.query(Habitacion)
            .filter(Habitacion.id_habitacion == id_habitacion)
            .first()
        )
        if not habitacion:
            raise ValueError("Habitación no encontrada")
        db.delete(habitacion)
        db.commit()
        return True

    from fastapi import HTTPException
    from sqlalchemy import func

    @staticmethod
    def cambiar_estado_habitacion(db: Session, id_habitacion: UUID):
        habitacion = db.query(Habitacion).filter_by(id_habitacion=id_habitacion).first()
        if not habitacion:
            raise HTTPException(status_code=404, detail="Habitación no encontrada")

        reserva_activa = (
            db.query(Reserva)
            .filter(
                Reserva.id_habitacion == id_habitacion,
                func.lower(Reserva.estado_reserva) == "activa",
            )
            .first()
        )

        if reserva_activa:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"No se puede cambiar el estado: habitación asociada a una reserva activa ({reserva_activa.id_reserva}).",
            )

        habitacion.disponible = not habitacion.disponible
        db.commit()
        db.refresh(habitacion)
        return habitacion

    @staticmethod
    def obtener_habitaciones_por_tipo(db: Session, tipo: str):
        tipo_registro = (
            db.query(Tipo_Habitacion)
            .filter(Tipo_Habitacion.nombre_tipo.ilike(f"%{tipo}%"))
            .first()
        )
        if not tipo_registro:
            raise ValueError(
                f"No existe un registro de tipo '{tipo.capitalize()}' en la base de datos"
            )
        return (
            db.query(Habitacion)
            .filter(Habitacion.id_tipo == tipo_registro.id_tipo)
            .all()
        )

    @staticmethod
    def obtener_habitacion_por_numero(db: Session, numero: int):
        habitacion = db.query(Habitacion).filter(Habitacion.numero == numero).first()
        if not habitacion:
            raise ValueError(f"No existen habitaciones con el número '{numero}'")
        return habitacion