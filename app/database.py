import sqlite3

def crear_bd():
    conexion = sqlite3.connect('proyectoia.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuarios (
        CodigoUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT NOT NULL,
        HoraDeEntrada TEXT,
        HoraDeSalida TEXT,
        Imagen BLOB,
        Activo INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Marcaje (
        CodigoMarcaje INTEGER PRIMARY KEY AUTOINCREMENT,
        CodigoUsuario INTEGER,
        FechaMarcajeEntrada TEXT,
        FechaMarcajeSalida TEXT,
        EnTiempo INTEGER,
        Observacion TEXT,
        FOREIGN KEY (CodigoUsuario) REFERENCES Usuarios (CodigoUsuario)
    )
    ''')

    conexion.commit()
    conexion.close()
