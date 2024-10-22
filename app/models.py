from pydantic import BaseModel
from typing import List

class UsuarioRegistro(BaseModel):
    codigoUsuario: int
    nombre: str
    hora_entrada: str
    hora_salida: str
    imagen_base64: str
    activo: int

class UsuarioLogin(BaseModel):
    nombre: str
    imagen_base64: str
    observacion: str

class Usuarios(BaseModel):
    codigoUsuario: int
    nombre: str
    HoraDeEntrada: str
    HoraDeSalida: str
    Foto: str
    activo: int

class UsuarioResponse(BaseModel):
    Usuario: List[Usuarios]
    mensaje: str

class MarcajeModel(BaseModel):
    CodigoMarcaje: int
    Usuario: str
    FechaEntrada: str
    FechaSalida: str
    EnTiempo: int
    Observacion: str

class MarcajeResponse(BaseModel):
    Marcaje: List[MarcajeModel]
    mensaje: str
