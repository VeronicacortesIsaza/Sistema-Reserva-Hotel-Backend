"""
Este módulo define la aplicación principal FastAPI para un sistema de gestión de reservas de hotel.
Incluye la configuración de middlewares, inclusión de routers para diferentes recursos (usuarios, habitaciones, reservas, servicios, autenticación, etc.), y eventos de inicio para la inicialización de la base de datos.
Provee endpoints RESTful para la gestión de usuarios, habitaciones, reservas, servicios adicionales, tipos de habitación y autenticación.
La documentación interactiva está disponible en /docs y /redoc.
Funciones:
- startup_event: Evento que se ejecuta al iniciar la aplicación, configurando la base de datos.
- root: Endpoint raíz que retorna información básica de la API.
- main: Función principal para ejecutar el servidor FastAPI con Uvicorn.
Routers incluidos:
- auth: Autenticación de usuarios.
- usuario: Gestión de usuarios.
- habitacion: Gestión de habitaciones.
- reserva: Gestión de reservas.
- reserva_servicios: Gestión de servicios asociados a reservas.
- servicios_adicionales: Gestión de servicios adicionales.
- tipo_habitacion: Gestión de tipos de habitación.
Sistema de gestión de productos con ORM SQLAlchemy y Neon PostgreSQL
API REST con FastAPI - Sin interfaz de consola
"""

import uvicorn
from apis import (
    usuario,
    habitacion,
    reserva,
    reserva_servicios,
    servicios_adicionales,
    tipo_habitacion,
    auth,
)
from database.config import create_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sistema de Gestión de Reservas",
    description="API REST para gestión de usuarios, habitaciones, servicios adicionales, tipos de habitacion, reserva servicios y reservas con autenticación",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(habitacion.router)
app.include_router(reserva.router)
app.include_router(reserva_servicios.router)
app.include_router(servicios_adicionales.router)
app.include_router(tipo_habitacion.router)


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    print("Iniciando Sistema de Gestión de Productos...")
    print("Configurando base de datos...")
    create_tables()
    print("Sistema listo para usar.")
    print("Documentación disponible en: http://localhost:8000/docs")


@app.get("/", tags=["raíz"])
async def root():
    """Endpoint raíz que devuelve información básica de la API."""
    return {
        "mensaje": "Bienvenido al Sistema de Gestión de reservas",
        "version": "1.0.0",
        "documentacion": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "autenticacion": "/auth",
            "usuarios": "/usuarios",
            "habitaciones": "/habitaciones",
            "resservas": "/reservas",
            "reserva servicios": "/reserva servicios",
            "tipos de habitacion": "/tipos de habitacion",
            "servicios adicionales": "/servicios adicionales",
        },
    }


def main():
    """Función principal para ejecutar el servidor"""
    print("Iniciando servidor FastAPI...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()