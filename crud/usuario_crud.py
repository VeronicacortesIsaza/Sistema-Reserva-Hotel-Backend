from datetime import datetime
from sqlalchemy.orm import Session
from entities.tipo_habitacion import Tipo_Habitacion
from entities.usuario import Usuario
from sqlalchemy.dialects.postgresql import UUID
from entities.reserva import Reserva
from entities.reserva_servicios import Reserva_Servicios
from entities.servicios_adicionales import Servicios_Adicionales
from entities.habitacion import Habitacion
import re
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends


def validar_telefono(telefono: str) -> bool:
    """Validar formato de teléfono"""
    pattern = r"^\+?[\d\s\-\(\)]{7,15}$"
    return re.match(pattern, telefono) is not None


class UsuarioCRUD:
    """
    Módulo CRUD para la entidad Usuario.

    Administra la creación, consulta, actualización, eliminación y autenticación
    de los usuarios que acceden al sistema.

    Funciones principales:
        - crear_usuario(db: Session, nuevo_usuario: Usuario) -> Usuario
        - obtener_usuario(db: Session, id_usuario: UUID) -> Usuario
        - obtener_usuario_por_nombre(db: Session, nombre_usuario: str) -> Usuario
        - obtener_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]
        - actualizar_usuario(db: Session, id_usuario: UUID, id_usuario_edita: UUID, **kwargs) -> Usuario
        - eliminar_usuario(db: Session, id_usuario: UUID) -> bool
        - autenticar_usuario(self, nombre_usuario: str, contrasena: str) -> Optional[Usuario]

    Notas:
        - Valida que el nombre de usuario sea único y no exceda 50 caracteres.
        - La contraseña no debe exceder 10 caracteres.
    """

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def crear_usuario(db: Session, nuevo_usuario: Usuario):
        try:
            if nuevo_usuario.nombre is None:
                raise ValueError("El nombre es obligatorio")
            if len(nuevo_usuario.nombre) > 100:
                raise ValueError("El nombre no puede exceder 100 caracteres")
            if nuevo_usuario.apellidos is None:
                raise ValueError("Los apellidos son obligatorios")
            if len(nuevo_usuario.apellidos) > 100:
                raise ValueError("Los apellidos no pueden exceder 100 caracteres")
            if nuevo_usuario.telefono is None:
                raise ValueError("El teléfono es obligatorio")
            if not validar_telefono(nuevo_usuario.telefono):
                raise ValueError(
                    "El teléfono debe tener entre 7 y 15 dígitos y puede incluir solo números, espacios, + o guiones"
                )
            if len(nuevo_usuario.telefono) > 13:
                raise ValueError("El teléfono no puede exceder 13 caracteres")
            existente = (
                db.query(Usuario)
                .filter(Usuario.nombre_usuario == nuevo_usuario.nombre_usuario)
                .first()
            )
            if nuevo_usuario.tipo_usuario is None:
                raise ValueError("El tipo de usuario es obligatorio")
            tipos_usuarios = {"Administrador", "Cliente"}
            if nuevo_usuario.tipo_usuario not in tipos_usuarios:
                raise ValueError(
                    f"Tipo de usuario inválido. Debe ser uno de: {tipos_usuarios}"
                )
            if nuevo_usuario.nombre_usuario is None:
                raise ValueError("El nombre de usuario es obligatorio")
            if len(nuevo_usuario.nombre_usuario) > 50:
                raise ValueError("El nombre de usuario no puede exceder 50 caracteres")
            if existente:
                raise ValueError(
                    f"El nombre de usuario '{nuevo_usuario.nombre_usuario}' ya está en uso."
                )
            if nuevo_usuario.clave is None:
                raise ValueError("La clave es obligatoria")
            if len(nuevo_usuario.clave) > 10:
                raise ValueError("La clave no puede exceder 10 caracteres")
            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)
            return nuevo_usuario
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def obtener_usuario(db: Session, id_usuario: UUID):
        return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    @staticmethod
    def obtener_usuario_por_nombre(db: Session, nombre_usuario: str):
        return (
            db.query(Usuario)
            .filter(Usuario.nombre_usuario == nombre_usuario.strip())
            .first()
        )

    @staticmethod
    def obtener_usuarios(db: Session, skip: int = 0, limit: int = 100):
        usuarios = db.query(Usuario).offset(skip).limit(limit).all()
        if not usuarios:
            raise ValueError("No hay usuarios registrados")
        return usuarios

    @staticmethod
    def actualizar_usuario(db: Session, id_usuario: UUID, **kwargs):
        try:
            usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
            if not usuario:
                raise ValueError("Usuario no encontrado")
            telefono = kwargs.get("telefono", None)

            if telefono not in (None, ""):
                if not validar_telefono(telefono):
                    raise ValueError(
                        "El teléfono debe tener entre 7 y 15 dígitos y puede incluir solo números, espacios, + o guiones"
                    )
                if len(telefono) > 13:
                    raise ValueError("El teléfono no puede exceder 13 caracteres")
            if "nombre_usuario" in kwargs:
                nuevo_nombre = kwargs["nombre_usuario"].strip()
                if len(nuevo_nombre) > 50:
                    raise ValueError("El nombre de usuario no puede exceder 50 caracteres")
                existente = (
                    db.query(Usuario).filter(Usuario.nombre_usuario == nuevo_nombre).first()
                )
                if existente and existente.id_usuario != id_usuario:
                    raise ValueError("Ya existe un usuario con ese nombre")
                kwargs["nombre_usuario"] = nuevo_nombre

            if "clave" in kwargs and len(kwargs["clave"]) > 10:
                raise ValueError("La clave no puede exceder 10 caracteres")

            usuario.fecha_edicion = datetime.now()
            for key, value in kwargs.items():
                if hasattr(usuario, key):
                    setattr(usuario, key, value)

            db.commit()
            db.refresh(usuario)
            return usuario
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def eliminar_usuario(db: Session, id_usuario: UUID) -> bool:
        try:
            ID_USUARIO_SISTEMA = UUID("00000000-0000-0000-0000-000000000000")

            usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
            if not usuario:
                raise ValueError("Usuario no encontrado")

            reservas = db.query(Reserva).filter(Reserva.id_usuario == id_usuario).all()
            for reserva in reservas:
                db.query(Reserva_Servicios).filter(
                    Reserva_Servicios.id_reserva == reserva.id_reserva
                ).delete()
            db.query(Reserva).filter(Reserva.id_usuario == id_usuario).delete()

            for t in (
                db.query(Tipo_Habitacion)
                .filter(Tipo_Habitacion.id_usuario_crea == id_usuario)
                .all()
            ):
                t.id_usuario_crea = ID_USUARIO_SISTEMA

            for h in (
                db.query(Habitacion)
                .filter(Habitacion.id_usuario_crea == id_usuario)
                .all()
            ):
                h.id_usuario_crea = ID_USUARIO_SISTEMA

            for s in (
                db.query(Servicios_Adicionales)
                .filter(Servicios_Adicionales.id_usuario_crea == id_usuario)
                .all()
            ):
                s.id_usuario_crea = ID_USUARIO_SISTEMA

            db.commit()
            db.delete(usuario)
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            print(f"Error al eliminar usuario: {e}")
            raise e

    @staticmethod
    def autenticar_usuario(db: Session, nombre_usuario: str, contrasena: str):
        """
        Autenticar un usuario usando nombre de usuario o email y contraseña en texto plano.
        """
        usuario = (
            db.query(Usuario)
            .filter(
                (Usuario.nombre_usuario == nombre_usuario)
                | (Usuario.nombre_usuario == nombre_usuario)
            )
            .first()
        )
        if usuario and usuario.clave == contrasena:
            return usuario
        return None

    @staticmethod
    def obtener_usuarios_admin(db: Session):
        """Obtener todos los usuarios que sean administradores."""
        try:
            admis = (
                db.query(Usuario)
                .filter(Usuario.tipo_usuario.ilike("Administrador"))
                .all()
            )
            if not admis:
                raise ValueError("No hay administradores registrados")
            return admis
        except Exception as e:
            raise ValueError(f"Error al obtener administradores: {str(e)}")

    @staticmethod
    def obtener_usuarios_cliente(db: Session):
        """Obtener todos los usuarios que sean clientes."""
        try:
            clientes = (
                db.query(Usuario).filter(Usuario.tipo_usuario.ilike("Cliente")).all()
            )
            if not clientes:
                raise ValueError("No hay clientes registrados")
            return clientes
        except Exception as e:
            raise ValueError(f"Error al obtener clientes: {str(e)}")

    @staticmethod
    def cambio_contraseña(db, id_usuario: UUID, clave_actual: str, clave_nueva: str):
        usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        if not usuario:
            raise ValueError("Usuario no encontrado")
        if usuario.clave != clave_actual:
            raise ValueError("La clave actual es incorrecta")
        if len(clave_nueva) > 10:
            raise ValueError("La nueva clave no puede exceder 10 caracteres")
        if clave_nueva == clave_actual:
            raise ValueError("La nueva clave debe ser diferente a la actual")

        usuario.clave = clave_nueva
        usuario.fecha_edicion = datetime.now()
        db.commit()
        db.refresh(usuario)
        return usuario
