from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from entities.tipo_habitacion import Tipo_Habitacion
from datetime import datetime
from entities.habitacion import Habitacion

from entities.usuario import Usuario


class TipoHabitacionCRUD:
    """
    Módulo CRUD para la entidad Tipo_Habitacion.

    Permite gestionar los tipos de habitación que existen en el hotel
    (sencilla, doble, suite, etc.).

    Funciones principales:
        - crear_tipo_habitacion(db: Session, tipo: Tipo_Habitacion) -> Tipo_Habitacion
        - obtener_tipo_habitacion(db: Session, id_tipo: UUID) -> Tipo_Habitacion
        - obtener_tipos_habitacion(db: Session) -> List[Tipo_Habitacion]
        - eliminar_tipo_habitacion(db: Session, id_tipo: UUID) -> bool

    Notas:
        - Se valida que no se repitan tipos de habitación con el mismo nombre.
    """

    def __init__(self, db):
        self.db = db

    @staticmethod
    def crear_tipo_habitacion(db: Session, tipo: Tipo_Habitacion):
        if tipo.nombre_tipo is None:
            raise ValueError("El nombre del tipo de habitación es obligatorio")
        if not tipo.nombre_tipo.strip():
            raise ValueError("El nombre del tipo de habitación no puede estar vacío")
        existente = (
            db.query(Tipo_Habitacion)
            .filter(Tipo_Habitacion.nombre_tipo == tipo.nombre_tipo)
            .first()
        )
        if existente:
            raise ValueError("El tipo de habitación ya existe")
        if tipo.descripcion is None:
            raise ValueError("La descripción del tipo de habitación es obligatoria")
        if not tipo.descripcion.strip():
            raise ValueError(
                "La descripción del tipo de habitación no puede estar vacía"
            )
        if tipo.id_usuario_crea is None:
            raise ValueError(
                "El ID del usuario que crea el tipo de habitación es obligatorio"
            )
        usuario_existe = (
            db.query(Usuario).filter(Usuario.id_usuario == tipo.id_usuario_crea).first()
        )
        if not usuario_existe:
            raise ValueError("El usuario que crea el tipo de habitación no existe")

        fecha_creacion = datetime.now()

        nuevo_tipo = Tipo_Habitacion(
            nombre_tipo=tipo.nombre_tipo.strip(),
            descripcion=tipo.descripcion.strip(),
            id_usuario_crea=tipo.id_usuario_crea,
            fecha_creacion=fecha_creacion,
        )

        db.add(nuevo_tipo)
        db.commit()
        db.refresh(nuevo_tipo)
        return nuevo_tipo

    @staticmethod
    def obtener_tipo_habitacion(db: Session, id_tipo: UUID):
        tipo = (
            db.query(Tipo_Habitacion).filter(Tipo_Habitacion.id_tipo == id_tipo).first()
        )
        if not tipo:
            raise ValueError("Tipo de habitación no encontrado")
        return tipo

    @staticmethod
    def obtener_tipos_habitacion(db: Session):
        tipos = db.query(Tipo_Habitacion).all()
        if not tipos:
            raise ValueError("No hay tipos de habitación registrados")
        return tipos

    @staticmethod
    def eliminar_tipo_habitacion(db: Session, id_tipo: UUID) -> bool:
        tipo = (
            db.query(Tipo_Habitacion).filter(Tipo_Habitacion.id_tipo == id_tipo).first()
        )
        habitaciones_asociadas = (
            db.query(Habitacion).filter(Habitacion.id_tipo == id_tipo).all()
        )
        if habitaciones_asociadas:
            raise ValueError(
                "No se puede eliminar el tipo de habitación porque hay habitaciones asociadas"
            )
        db.delete(tipo)
        db.commit()
        return True

    @staticmethod
    def actualizar_tipo_habitacion(db: Session, id_tipo: UUID, **campos_actualizacion):
        tipo = (
            db.query(Tipo_Habitacion).filter(Tipo_Habitacion.id_tipo == id_tipo).first()
        )
        if "nombre_tipo" in campos_actualizacion:
            nuevo_nombre = campos_actualizacion["nombre_tipo"].strip()
            if not nuevo_nombre:
                raise ValueError(
                    "El nombre del tipo de habitación no puede estar vacío"
                )

            existente = (
                db.query(Tipo_Habitacion)
                .filter(
                    Tipo_Habitacion.nombre_tipo == nuevo_nombre,
                    Tipo_Habitacion.id_tipo != id_tipo,
                )
                .first()
            )
            if existente:
                raise ValueError("Ya existe un tipo de habitación con ese nombre")

            campos_actualizacion["nombre_tipo"] = nuevo_nombre

        if campos_actualizacion.get("id_usuario_edita") is None:
            raise ValueError(
                "El ID del usuario que edita el tipo de habitación es obligatorio"
            )

        usuario = (
            db.query(Usuario)
            .filter(Usuario.id_usuario == campos_actualizacion.get("id_usuario_edita"))
            .first()
        )
        if not usuario:
            raise ValueError("El usuario que edita no existe")
        for key, value in campos_actualizacion.items():
            if hasattr(tipo, key) and value is not None:
                setattr(tipo, key, value)

        tipo.fecha_edicion = datetime.now()

        db.commit()
        db.refresh(tipo)
        return tipo
