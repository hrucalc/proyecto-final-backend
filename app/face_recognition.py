import base64
import cv2
import numpy as np
from mtcnn.mtcnn import MTCNN
import sqlite3
from datetime import datetime
from io import BytesIO
from PIL import Image
from typing import Optional
from app.database import crear_bd

def decodificar_imagen_base64(base64_string):
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    img_np = np.array(img)
    img_cv2 = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    return img_cv2

def registrar_usuario(data):
    crear_bd()
    imagen_cv2 = decodificar_imagen_base64(data.imagen_base64)
    detector = MTCNN()
    pixeles = cv2.cvtColor(imagen_cv2, cv2.COLOR_BGR2RGB)
    caras = detector.detect_faces(pixeles)

    if len(caras) == 0:
        raise Exception("No se detectó ningún rostro")

    x1, y1, ancho, alto = caras[0]['box']
    x2, y2 = x1 + ancho, y1 + alto
    cara_reg = imagen_cv2[y1:y2, x1:x2]
    cara_reg = cv2.resize(cara_reg, (150, 200), interpolation=cv2.INTER_CUBIC)

    _, buffer = cv2.imencode('.jpg', cara_reg)
    img_byte_arr = buffer.tobytes()

    conexion = sqlite3.connect('proyectoia.db')
    cursor = conexion.cursor()

    # Verificar si el usuario ya existe
    cursor.execute('''
    SELECT COUNT(1) FROM Usuarios WHERE Nombre = ?
    ''', (data.nombre,))
    resultado = cursor.fetchone()

    if resultado[0] > 0:
        conexion.close()
        raise Exception("El usuario ya existe")

    # Insertar el nuevo usuario si no existe
    cursor.execute('''
    INSERT INTO Usuarios (Nombre, HoraDeEntrada, HoraDeSalida, Imagen, Activo)
    VALUES (?, ?, ?, ?, ?)
    ''', (data.nombre, data.hora_entrada, data.hora_salida, img_byte_arr, 1))

    cursor.execute('SELECT CodigoUsuario FROM Usuarios WHERE Nombre = ?', (data.nombre,))
    result = cursor.fetchone()

    conexion.commit()
    conexion.close()

    return result[0]


def actualizar_usuario(data):
    crear_bd()
    conexion = sqlite3.connect('proyectoia.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM Usuarios WHERE CodigoUsuario = ?', (data.codigoUsuario,))
    result = cursor.fetchone()

    if result:
        if data.imagen_base64 == '':
            cursor.execute('''UPDATE Usuarios 
                                    SET Activo = ?
                                WHERE CodigoUsuario = ?''', (0 if data.activo == 1 else 1, data.codigoUsuario))
            conexion.commit()
            conexion.close()
            return data.codigoUsuario

        imagen_cv2 = decodificar_imagen_base64(data.imagen_base64)
        detector = MTCNN()
        pixeles = cv2.cvtColor(imagen_cv2, cv2.COLOR_BGR2RGB)
        caras = detector.detect_faces(pixeles)
        if len(caras) == 0:
            raise Exception("No se detectó ningún rostro")
        
        x1, y1, ancho, alto = caras[0]['box']
        x2, y2 = x1 + ancho, y1 + alto
        cara_reg = imagen_cv2[y1:y2, x1:x2]
        cara_reg = cv2.resize(cara_reg, (150, 200), interpolation=cv2.INTER_CUBIC)

        _, buffer = cv2.imencode('.jpg', cara_reg)
        img_byte_arr = buffer.tobytes()

        cursor.execute('''UPDATE Usuarios 
                        SET Nombre = ?,
                            HoraDeEntrada = ?,
                            HoraDeSalida = ?,
                            Imagen = ?
                        WHERE CodigoUsuario = ?''', (data.nombre, data.hora_entrada, data.hora_salida, img_byte_arr,result[0]))
        
        conexion.commit()
        conexion.close()
        return result[0]

    else:
        raise Exception("Usuario no encontrado")

def comparar_rostro(base64_imagen, nombre_usuario, observacion):
    crear_bd()
    img1_cv2 = decodificar_imagen_base64(base64_imagen)
    conexion = sqlite3.connect('proyectoia.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM Usuarios WHERE Nombre = ? OR codigousuario = ?', (nombre_usuario,nombre_usuario))
    result = cursor.fetchone()
    respuesta = ""
    if result:
        with open("temp.jpg", 'wb') as f:
            f.write(result[4])
        img2_cv2 = cv2.imread("temp.jpg", 0)

        def orb_sim(img1, img2):
            orb = cv2.ORB_create()
            kpa, descr_a = orb.detectAndCompute(img1, None)
            kpb, descr_b = orb.detectAndCompute(img2, None)
            comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = comp.match(descr_a, descr_b)
            regiones_similares = [i for i in matches if i.distance < 70]
            if len(matches) == 0:
                return 0
            return len(regiones_similares) / len(matches)

        img1 = cv2.cvtColor(img1_cv2, cv2.COLOR_BGR2GRAY)
        similitud = orb_sim(img1, img2_cv2)

        if similitud >= 0.95:
            # Obtener horas de entrada y salida del usuario
            codigo_usuario = result[0]
            hora_entrada = result[2]
            hora_salida = result[3]
            now = datetime.now().strftime("%H:%M")

            cursor.execute('''SELECT * FROM Marcaje WHERE CodigoUsuario = ? AND SUBSTR(FechaMarcajeEntrada, 1, 10) = ?''',
                                (codigo_usuario, datetime.now().strftime("%Y-%m-%d")))
            marcaje_entrada = cursor.fetchone()

            # Verificar si la hora actual está dentro del rango de entrada y salida
            if now < hora_salida:
                if marcaje_entrada:
                    respuesta = "Ya se ha tomado asistencia de entrada"
                else:
                    # Registrar la hora de entrada en la tabla Marcaje
                    EnTiempo = 1 if now < hora_entrada else 0
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute('''
                    INSERT INTO Marcaje (CodigoUsuario, FechaMarcajeEntrada, EnTiempo, Observacion)
                    VALUES (?, ?, ?, ?)
                    ''', (codigo_usuario, now, EnTiempo, observacion))
                    respuesta = "Marcaje de entrada exitoso"
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''SELECT * FROM Marcaje WHERE CodigoUsuario = ? AND SUBSTR(FechaMarcajeSalida, 1, 10) = ?''',
                                (codigo_usuario, datetime.now().strftime("%Y-%m-%d")))
                marcaje_salida = cursor.fetchone()
                if marcaje_salida:
                    respuesta = "Ya se ha tomado asistencia de salida"
                else:
                    if marcaje_entrada:
                        cursor.execute('''UPDATE Marcaje 
                        SET FechaMarcajeSalida = ? 
                        WHERE CodigoUsuario = ? 
                        AND SUBSTR(FechaMarcajeEntrada, 1, 10) = ?''', (now, codigo_usuario, datetime.now().strftime("%Y-%m-%d")))
                        respuesta = "Marcaje de salida exitoso"
                    else:
                        respuesta = "Marcaje de salida exitoso"
                        # Registrar la hora de entrada en la tabla Marcaje
                        EnTiempo = 1 if now < hora_entrada else 0
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute('''
                        INSERT INTO Marcaje (CodigoUsuario, FechaMarcajeSalida, EnTiempo, Observacion)
                        VALUES (?, ?, ?, ?)
                        ''', (codigo_usuario, now, EnTiempo, observacion))
        else:
            respuesta = "Rostro Incorrecto"
        conexion.commit()
        conexion.close()
        return respuesta
    else:
        raise Exception("Usuario no encontrado")

def obtener_marcajes(codigousuario: Optional[str], EnTiempo: Optional[str], FechaInicio: Optional[str], FechaFin: Optional[str]):
    crear_bd()
    conexion = sqlite3.connect('proyectoia.db')
    cursor = conexion.cursor()

    # Construcción dinámica de la consulta
    query = '''
                SELECT
                    M.CodigoMarcaje, 
                    Nombre, FechaMarcajeEntrada, FechaMarcajeSalida, EnTiempo, Observacion 
                FROM Marcaje M
                INNER JOIN Usuarios U ON U.CodigoUsuario = M.CodigoUsuario WHERE 1=1 
                '''
    parametros = []

    if codigousuario:
        query += " AND M.CodigoUsuario = ?"
        parametros.append(codigousuario)

    if EnTiempo:
        query += " AND M.EnTiempo = ?"
        parametros.append(EnTiempo)

    if FechaInicio and FechaFin:
        query += " AND M.FechaMarcajeEntrada BETWEEN ? AND ?"
        parametros.append(FechaInicio + ' 00:00:00')
        parametros.append(FechaFin + ' 23:00:00')

    query += " ORDER BY M.CodigoMarcaje DESC;"


    # Consulta a la tabla Marcaje
    cursor.execute(query, parametros)

    registros = cursor.fetchall()
    conexion.close()

    # Formatear los resultados en una lista de diccionarios para cada marcaje
    marcajes = []
    for registro in registros:
        marcaje = {
            "CodigoMarcaje": registro[0],
            "Usuario": registro[1] if registro[1] is not None else "",
            "FechaEntrada": registro[2] if registro[2] is not None else "",
            "FechaSalida": registro[3] if registro[3] is not None else "",
            "EnTiempo": registro[4],
            "Observacion": registro[5] if registro[5] is not None else ""
        }
        marcajes.append(marcaje)
    
    return marcajes

def obtener_usuarios(codigousuario: Optional[str]):
    crear_bd()
    conexion = sqlite3.connect('proyectoia.db')
    cursor = conexion.cursor()

    # Construcción dinámica de la consulta
    query = "SELECT CodigoUsuario, Nombre, HoraDeEntrada, HoraDeSalida, Imagen, Activo FROM Usuarios "
    parametros = []

    if codigousuario:
        query += " WHERE CodigoUsuario = ?"
        parametros.append(codigousuario)

    cursor.execute(query, parametros)
    registros = cursor.fetchall()
    conexion.close()

    # Formatear los resultados en una lista de diccionarios para cada marcaje
    usuarios = []
    for registro in registros:
        usuario = {
            "codigoUsuario": registro[0],
            "nombre": registro[1],
            "HoraDeEntrada": registro[2],
            "HoraDeSalida": registro[3],
            "Foto": base64.b64encode(registro[4]).decode('utf-8') if codigousuario else "",
            "activo": registro[5]
        }
        usuarios.append(usuario)
    
    return usuarios
