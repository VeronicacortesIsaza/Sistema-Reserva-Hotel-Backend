from datetime import datetime, timedelta
from http.client import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from entities.habitacion import Habitacion
from entities.reserva import Reserva
from entities.reserva_servicios import Reserva_Servicios
from entities.usuario import Usuario


class ReservaCRUD:
    """
    Módulo CRUD para la entidad Reserva.

    Gestiona las reservas realizadas por los clientes, validando fechas
    y asociando correctamente a cliente y habitación.

    Funciones principales:
        - crear_reserva(db: Session, reserva: Reserva) -> Reserva
        - obtener_reserva(db: Session, id_reserva: UUID) -> Reserva
        - obtener_reservas(db: Session) -> List[Reserva]
        - actualizar_reserva(db: Session, id_reserva: UUID, **kwargs) -> Reserva
        - eliminar_reserva(db: Session, id_reserva: UUID) -> bool
        - obtener_reservas_activas(db: Session) -> List[Reserva]
        - actualizar_costo_total(db: Session, id_reserva: UUID, monto_extra: float) -> Reserva

    Notas:
        - Se valida que la fecha de entrada sea menor a la de salida.
        - Al cancelar una reserva se recomienda actualizar el estado de la habitación.
    """

    def __init__(self, db):
        self.db = db

    @staticmethod
    def crear_reserva(db: Session, reserva: Reserva):
        if not reserva.fecha_entrada:
            raise ValueError("La fecha de entrada es obligatoria")
        if reserva.fecha_entrada < datetime.now().date():
            raise ValueError("La fecha de entrada debe ser posterior a la fecha actual")
        if not reserva.numero_de_personas:
            raise ValueError("El número de personas es obligatorio")
        if reserva.numero_de_personas <= 0:
            raise ValueError("El número de personas debe ser mayor a 0")
        if not reserva.noches:
            raise ValueError("El número de noches es obligatorio")
        if reserva.noches <= 0:
            raise ValueError("El número de noches debe ser mayor a 0")
        if not reserva.estado_reserva:
            raise ValueError("El estado de la reserva es obligatorio")
        estados = ["Activa", "Cancelada"]
        if reserva.estado_reserva not in estados:
            raise ValueError(
                f"Estado de reserva inválido. Debe ser uno de: {', '.join(estados)}"
            )
        if not reserva.id_usuario:
            raise ValueError("El ID del usuario asociado a la reserva es obligatorio")
        usuario_existe = (
            db.query(Usuario).filter(Usuario.id_usuario == reserva.id_usuario).first()
        )
        if not usuario_existe:
            raise ValueError("El usuario asociado no existe")
        if not reserva.id_habitacion:
            raise ValueError("El ID de la habitación es obligatorio")
        habitacion = (
            db.query(Habitacion)
            .filter(Habitacion.id_habitacion == reserva.id_habitacion)
            .first()
        )
        if not habitacion:
            raise ValueError("La habitación asociada no existe")
        if not habitacion.disponible:
            raise ValueError("La habitación no está disponible")
        reserva.estado_reserva = "Activa"
        reserva.fecha_creacion = datetime.now()
        reserva.costo_total = habitacion.precio * reserva.noches
        reserva.fecha_salida = reserva.fecha_entrada + timedelta(days=reserva.noches)
        habitacion.disponible = False
        reserva.fecha_creacion = datetime.now()
        reserva.id_usuario_crea = usuario_existe.id_usuario

        db.add(reserva)
        db.commit()
        db.refresh(reserva)
        return reserva

    @staticmethod
    def obtener_reserva(db: Session, id_reserva: UUID):
        reserva = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
        if not reserva:
            raise ValueError("Reserva no encontrada")
        return reserva

    @staticmethod
    def obtener_reservas(db: Session, skip: int = 0, limit: int = 100):
        reservas = db.query(Reserva).offset(skip).limit(limit).all()
        if not reservas:
            raise ValueError("No hay reservas registradas")
        return reservas

    @staticmethod
    def actualizar_reserva(db: Session, id_reserva: UUID, **kwargs):
        reserva = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
        if not reserva:
            raise ValueError("Reserva no encontrada")

        # Validaciones de número de personas y noches
        if "numero_de_personas" in kwargs and kwargs["numero_de_personas"] is not None:
            if kwargs["numero_de_personas"] <= 0:
                raise ValueError("El número de personas debe ser mayor a 0")

        if "noches" in kwargs and kwargs["noches"] is not None:
            if kwargs["noches"] <= 0:
                raise ValueError("El número de noches debe ser mayor a 0")

        # Validación de estado
        if "estado_reserva" in kwargs and kwargs["estado_reserva"] is not None:
            estados = ["Activa", "Cancelada"]
            nuevo_estado = kwargs["estado_reserva"]
            habitacion_actual = (
                db.query(Habitacion)
                .filter(Habitacion.id_habitacion == reserva.id_habitacion)
                .first()
            )
            if nuevo_estado not in estados:
                raise ValueError(f"Estado inválido. Debe ser: {', '.join(estados)}")

            # ✅ Si pasa de ACTIVA → CANCELADA → liberar habitación
            if reserva.estado_reserva == "Activa" and nuevo_estado == "Cancelada":
                if habitacion_actual:
                    habitacion_actual.disponible = True
            if reserva.estado_reserva == "Cancelada" and nuevo_estado == "Activa":
                if habitacion_actual:
                    if not habitacion_actual.disponible:
                        raise ValueError(
                            "La habitación asociada está ocupada. No se puede activar la reserva."
                        )
                    # ✅ Está libre → volver a ocuparla
                    habitacion_actual.disponible = False

        fecha_entrada = kwargs.get("fecha_entrada", reserva.fecha_entrada)
        noches = kwargs.get("noches", reserva.noches)
        fecha_salida = fecha_entrada + timedelta(days=noches)

        if fecha_entrada and fecha_salida and fecha_entrada >= fecha_salida:
            raise ValueError("La fecha de entrada debe ser anterior a la fecha de salida")

        # Cambio de habitación
        if "id_habitacion" in kwargs and kwargs["id_habitacion"] is not None:
            nueva_habitacion = (
                db.query(Habitacion)
                .filter(Habitacion.id_habitacion == kwargs["id_habitacion"])
                .first()
            )

            if not nueva_habitacion:
                raise ValueError("La nueva habitación no existe")

            if not nueva_habitacion.disponible:
                raise ValueError("La nueva habitación no está disponible")

            # ✅ Liberar habitación actual solo si la reserva está activa
            habitacion_actual = (
                db.query(Habitacion)
                .filter(Habitacion.id_habitacion == reserva.id_habitacion)
                .first()
            )

            if habitacion_actual and reserva.estado_reserva == "Activa":
                habitacion_actual.disponible = True

            # ✅ Ocupa la nueva habitación
            nueva_habitacion.disponible = False
            reserva.id_habitacion = kwargs["id_habitacion"]

            # Recalcular costo total
            reserva.costo_total = nueva_habitacion.precio * noches

        # Aplicar cambios normales
        reserva.fecha_salida = fecha_salida
        reserva.fecha_edicion = datetime.now()

        for key, value in kwargs.items():
            if hasattr(reserva, key):
                setattr(reserva, key, value)

        db.commit()
        db.refresh(reserva)
        return reserva

    def eliminar_reserva(self, db: Session, id_reserva: UUID):
        reserva = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
        if not reserva:
            raise ValueError("La reserva no existe.")

        db.query(Reserva_Servicios).filter(
            Reserva_Servicios.id_reserva == id_reserva
        ).delete()

        db.delete(reserva)
        db.commit()
        return True

    @staticmethod
    def obtener_reservas_por_usuario(db: Session, id_usuario: UUID):
        reservas = db.query(Reserva).filter(Reserva.id_usuario == id_usuario).all()
        if not reservas:
            raise ValueError("No se encontraron reservas para el usuario especificado")
        return reservas

    @staticmethod
    def obtener_reservas_activas(db: Session):
        activas = db.query(Reserva).filter(Reserva.estado_reserva == "Activa").all()
        if not activas:
            raise ValueError("No hay reservas activas en este momento")
        return activas

    @staticmethod
    def obtener_reservas_canceladas(db: Session):
        canceladas = (
            db.query(Reserva).filter(Reserva.estado_reserva == "Cancelada").all()
        )
        if not canceladas:
            raise ValueError("No hay reservas canceladas en este momento")
        return canceladas
    