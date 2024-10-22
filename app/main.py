from typing import Optional
from fastapi import Query
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.face_recognition import registrar_usuario, comparar_rostro, obtener_marcajes, obtener_usuarios, actualizar_usuario
from app.models import *

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Permite tu origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

@app.get("/")
def read_root():
    return {"mensaje": "API en funcionamiento"}

@app.post("/registrar_usuario/")
def api_registrar_usuario(data: UsuarioRegistro):
    try:
        codigousuarior = registrar_usuario(data)
        return {
            "CodigoUsuario": codigousuarior,
            "mensaje": "Usuario registrado correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/actualizar_usuario/")
def api_actualizar_usuario(data: UsuarioRegistro):
    try:
        codigousuarior = actualizar_usuario(data)
        return {
            "CodigoUsuario": codigousuarior,
            "mensaje": "Usuario actualizado correctamente"
        }
    except Exception as e:
        if str(e) == 'Usuario no encontrado':
            return {"mensaje": "Usuario no encontrado"}
        else:
            raise HTTPException(status_code=400, detail=str(e))

@app.post("/comparar_rostro/")
def api_comparar_rostro(data: UsuarioLogin):
    try:
        es_similar = comparar_rostro(data.imagen_base64, data.nombre, data.observacion)
        return {"mensaje": es_similar}
    except Exception as e:
        if str(e) == 'Usuario no encontrado':
            return {"mensaje": "Usuario no encontrado"}
        else:
            raise HTTPException(status_code=400, detail=str(e))
        
@app.get("/obtener_usuarios/", response_model=UsuarioResponse)
def api_obtener_usuarios(codigousuario: Optional[str] = None):
    try:
        Usuarios = obtener_usuarios(codigousuario)  # Obtener datos de la BD
        return {
            "Usuario": Usuarios,
            "mensaje": "Usuarios obtenidos correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/obtener_marcajes/", response_model=MarcajeResponse)
def api_obtener_marcajes(codigousuario: Optional[str] = None, EnTiempo: Optional[str] = None, FechaInicio: Optional[str] = None, FechaFin: Optional[str] = None):
    try:
        marcajes = obtener_marcajes(codigousuario,EnTiempo,FechaInicio,FechaFin)  # Obtener datos de la BD
        return {
            "Marcaje": marcajes,
            "mensaje": "Marcajes obtenidos correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
