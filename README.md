# Sistema de Gestión de Hotel  

Este proyecto implementa un **sistema de gestión para un hotel**
desarrollado en **Python 3.8** utilizando **SQLAlchemy** para la
persistencia de datos y **FastAPI** para exponer servicios mediante
**APIs RESTful**.

El sistema permite la autenticación de usuarios, gestión de clientes,
habitaciones, reservas y servicios adicionales, con control de roles
(**administrador** y **cliente**).

---

## Estructura del Proyecto

```
Sistema_Reserva_Hotel/
│
├── apis/      
│   ├── auth.py                 
│   ├── habitacion.py
│   ├── reserva.py
│   ├── reserva_servicios.py
│   ├── servicios_adicionales.py
│   ├── tipo_habitacion.py
│   └── usuario.py
│
├── utils/ 
│   └── jwt_manager.py 
│ 
├── auth/                         
│   └── security.py
│ 
├── crud/                         
│   ├── habitacion_crud.py
│   ├── reserva_crud.py
│   ├── reserva_servicios_crud.py
│   ├── servicios_adicionales_crud.py
│   ├── tipo_habitacion_crud.py
│   └── usuario_crud.py
│
├── database/                     
│   └── config.py                 
│
├── entities/                     
│   ├── __init__.py
│   ├── habitacion.py
│   ├── reserva_servicios.py
│   ├── reserva.py
│   ├── servicios_adicionales.py
│   ├── tipo_habitacion.py
│   └── usuario.py
│
├── migrations/
│   ├── versions/
│   │   └── 0832f30327b7_create_tables.py
│   ├── env.py
│   └── script.py.mako
│               
├── .env
├── .gitignore 
├── alembic.ini
├── main.py   
├── README.md
├── requirements.txt
└── schemas.py                     
```

---

## Requisitos Previos

- **Python 3.8 o superior**  
- **PostgreSQL** (o el motor definido en `database/config.py`)  
- **Dependencias** (instalarlas con el archivo `requirements.txt`):  

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` incluye:  
- `sqlalchemy`  
- `psycopg2-binary`  
- `bcrypt` (opcional, para manejo de contraseñas cifradas)

---


### Inicio de Sesión
- El sistema solicitará **nombre de usuario** y **contraseña**.  
- El sistema devuelve un **token de acceso** válido por un tiempo
  definido.\
---

## Descripción de la Lógica de Negocio

El sistema cubre los siguientes procesos principales:

### Gestión de Usuarios
- Creación de usuarios (administradores y clientes).  
- Actualización, consulta y eliminación.  
- Cambio de contraseña y actualización de perfil.  

### Gestión de Habitaciones
- Registro de habitaciones con tipo, precio y disponibilidad.  
- Modificación y consulta de estado (disponible, reservada, mantenimiento).  

### Gestión de Reservas
- Creación de reservas asociadas a clientes y habitaciones.  
- Validación de fechas de entrada y salida.  
- Cálculo automático del número de noches y costo total.  
- Control de estados: **Activa**, **Cancelada**.  

### Servicios Adicionales
- Registro y asociación de servicios (desayuno, spa, transporte, etc.) a una reserva.  
- Suma de costos adicionales a la cuenta final del cliente.  

### Autenticación
- Acceso mediante **nombre de usuario** y contraseña.  
- Distinción de roles:  
  - **Administrador**: acceso completo a todas las gestiones.  
  - **Cliente**: acceso restringido a su perfil y reservas.  

---

## Notas
- La lógica de negocio sigue encapsulada en la clase `SistemaGestion` y en los CRUDs.\
- La capa `apis` expone esa lógica vía **FastAPI** para consumo externo.\
- La capa `auth` maneja cifrado de contraseñas y emisión/verificación de **JWT**.\
-   Se mantiene separación clara entre entidades, persistencia y presentación. 

---

## Cómo Ejecutar el Sistema

1. **Clonar el repositorio**  

```bash
git clone https://github.com/VeronicacortesIsaza/Sistema-Reserva-Hotel-Backend.git
cd SistemaReservaHotel
```

2. **Instalar dependencias**  

```bash
pip install -r requirements.txt
```

3. **Ejecutar el sistema**  

```bash
python main.py
```

Al ejecutar el sistema, la consola mostrará el enlace del servidor local
Puedes abrirlo en tu navegador para acceder a la documentación interactiva de la API
Debes ingresar a: ```bash http://localhost:8000/docs```


Ejemplo de salida en consola:
```bash
  @app.on_event("startup")
Iniciando servidor FastAPI...
INFO:     Will watch for changes in these directories: ['C:\\Users\\billares clud\\Documents\\Sistema_Reserva_Hotel']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [13596] using StatReload
INFO:     Started server process [20640]
INFO:     Waiting for application startup.
Iniciando Sistema de Gestión de Productos...
Configurando base de datos...
Sistema listo para usar.
Documentación disponible en: http://localhost:8000/docs
INFO:     Application startup complete.
```
---
