# 📘 Proyecto Final Backend: Reconocimiento Facial y Control de Asistencia

Este proyecto es un sistema de backend para un sistema de control de asistencia utilizando reconocimiento facial. La API está construida con **FastAPI** y emplea reconocimiento facial basado en la biblioteca **OpenCV** y **MTCNN**. La aplicación permite registrar usuarios, actualizar sus datos, verificar la identidad a través de comparación facial, y gestionar registros de asistencia en una base de datos **SQLite**.

## 🏗️ Estructura del Proyecto

```
/app
├── main.py                 # Archivo principal con las rutas de la API.
├── models.py               # Modelos Pydantic para la API.
├── face_recognition.py     # Lógica de reconocimiento facial y operaciones en la base de datos.
├── database.py             # Configuración y creación de la base de datos SQLite.
```

## 🚀 Instalación

Sigue estos pasos para instalar y ejecutar el proyecto en tu entorno local:

1. **Clona este repositorio**:
   ```bash
   git clone https://github.com/hrucalc/proyecto-final-backend.git
   ```
2. **Navega al directorio del proyecto**:
   ```bash
   cd proyecto-final-backend
   ```
3. **Crea un entorno virtual (opcional pero recomendado)**:
   ```bash
   python -m venv venv
   ```
4. **Activa el entorno virtual**:
   - En Windows:
     ```bash
     venv\Scripts\activate
     ```
   - En Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
5. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuración

No es necesario realizar una configuración adicional, ya que la base de datos `proyectoia.db` se crea automáticamente al iniciar la aplicación si no existe. Asegúrate de que las dependencias estén instaladas correctamente.

## 📌 Endpoints Disponibles

### 1. **Registrar Usuario**
   - **Método**: `POST`
   - **Ruta**: `/registrar_usuario/`
   - **Descripción**: Registra un nuevo usuario en la base de datos.
   - **Cuerpo de la Solicitud**:
     ```json
     {
       "nombre": "Juan Perez",
       "hora_entrada": "08:00",
       "hora_salida": "17:00",
       "imagen_base64": "base64_string"
     }
     ```
   - **Respuesta**: Código del usuario registrado.

### 2. **Actualizar Usuario**
   - **Método**: `POST`
   - **Ruta**: `/actualizar_usuario/`
   - **Descripción**: Actualiza la información de un usuario registrado.
   - **Cuerpo de la Solicitud**:
     ```json
     {
       "codigoUsuario": 1,
       "nombre": "Juan Perez Actualizado",
       "hora_entrada": "08:30",
       "hora_salida": "17:30",
       "imagen_base64": "base64_string",
       "activo": 1
     }
     ```
   - **Respuesta**: Código del usuario actualizado.

### 3. **Comparar Rostro**
   - **Método**: `POST`
   - **Ruta**: `/comparar_rostro/`
   - **Descripción**: Compara la imagen proporcionada con la almacenada en la base de datos para verificar la identidad del usuario.
   - **Cuerpo de la Solicitud**:
     ```json
     {
       "imagen_base64": "base64_string",
       "nombre_usuario": "Juan Perez",
       "observacion": "Llegó puntual"
     }
     ```
   - **Respuesta**: Mensaje de éxito o error en el marcaje.

### 4. **Obtener Usuarios**
   - **Método**: `GET`
   - **Ruta**: `/obtener_usuarios/`
   - **Descripción**: Obtiene la lista de usuarios registrados.
   - **Parámetros** (opcional): 
     - `codigousuario`: ID del usuario específico para filtrar.
   - **Respuesta**: Lista de usuarios registrados.

### 5. **Obtener Marcajes**
   - **Método**: `GET`
   - **Ruta**: `/obtener_marcajes/`
   - **Descripción**: Recupera los registros de marcaje filtrados por usuario, si fue a tiempo, y fechas.
   - **Parámetros** (opcional):
     - `codigousuario`: ID del usuario.
     - `EnTiempo`: Indicador de si la entrada fue a tiempo (1 = sí, 0 = no).
     - `FechaInicio`: Fecha de inicio del rango de consulta.
     - `FechaFin`: Fecha de fin del rango de consulta.
   - **Respuesta**: Lista de registros de marcajes.

## 📜 Base de Datos

La base de datos utilizada en este proyecto es **SQLite**. El archivo `proyectoia.db` se crea automáticamente si no existe al iniciar la aplicación. A continuación, se describen las tablas utilizadas:

### 1. **Usuarios**
   - **CodigoUsuario**: Identificador único del usuario (autoincremental).
   - **Nombre**: Nombre del usuario.
   - **HoraDeEntrada**: Hora esperada de entrada.
   - **HoraDeSalida**: Hora esperada de salida.
   - **Imagen**: Imagen del usuario almacenada en formato BLOB.
   - **Activo**: Estado del usuario (1 = activo, 0 = inactivo).

### 2. **Marcaje**
   - **CodigoMarcaje**: Identificador único de cada registro de marcaje (autoincremental).
   - **CodigoUsuario**: Relación con el usuario que realizó el marcaje.
   - **FechaMarcajeEntrada**: Fecha y hora de entrada registrada.
   - **FechaMarcajeSalida**: Fecha y hora de salida registrada.
   - **EnTiempo**: Indicador si la entrada fue a tiempo (1 = sí, 0 = no).
   - **Observacion**: Comentarios u observaciones adicionales.

## 🛠️ Tecnologías Utilizadas

- **Python**: Lenguaje de programación principal.
- **FastAPI**: Framework para la creación de la API REST.
- **OpenCV**: Biblioteca para la manipulación de imágenes y procesamiento de visión computacional.
- **MTCNN**: Detector de rostros basado en Redes Neuronales.
- **SQLite**: Base de datos ligera y sencilla para almacenamiento local.
- **Pydantic**: Validación de datos y esquemas con Python.

## 📋 Requisitos del Sistema

- **Python** 3.7 o superior.
- Librerías detalladas en el archivo `requirements.txt`.

## 🖼️ Ejecución de la Aplicación

1. **Inicia el servidor**:
   ```bash
   uvicorn app.main:app --reload
   ```
2. **Accede a la documentación de la API** a través de [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## 👥 Contribuciones

¡Las contribuciones son bienvenidas! Si deseas contribuir, sigue estos pasos:

1. Realiza un _fork_ del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y _commits_ (`git commit -am 'Agregué una nueva funcionalidad'`).
4. Sube la rama (`git push origin feature/nueva-funcionalidad`).
5. Crea un nuevo _Pull Request_.

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Puedes ver más detalles en el archivo `LICENSE`.
