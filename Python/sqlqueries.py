import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta
    

class QueriesSQLite:
    def create_connection(path):
        connection = None
        try:
            connection = sqlite3.connect(path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")
        return connection

    def execute_query(connection, query, data_tuple):
        cursor = connection.cursor()
        try:
            cursor.execute(query, data_tuple)
            connection.commit()
            print("Query executed successfully")
            return cursor.lastrowid
        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_read_query(connection, query, data_tuple=()):
        cursor = connection.cursor()
        result = None
        try:
            cursor.execute(query, data_tuple)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")

    def create_tables():
        connection = QueriesSQLite.create_connection("BankDB.sqlite")
        tabla_usuarios = """
        CREATE TABLE IF NOT EXISTS usuarios(
            username TEXT PRIMARY KEY, 
            nombre TEXT NOT NULL, 
            password TEXT NOT NULL,
            tipo TEXT NOT NULL
        );
        """
      
        tabla_Grupos = """
        CREATE TABLE IF NOT EXISTS Grupos(
         codigo TEXT PRIMARY KEY, 
         nombre TEXT NOT NULL, 
         fecha de ingreso TEXT NOT NULL, 
         Numero de estudiantes INTEGER NOT NULL
        );
        """
        
        tabla_Estudiantes = """
        CREATE TABLE IF NOT EXISTS Estudiantes(
         Cedula INTEGER PRIMARY KEY, 
         Nombre TEXT NOT NULL,
         Banco TEXT  NOT NULL,
         Numero REAL NOT NULL,
         Grupo TEXT NOT NULL,
         total REAL NOT NULL, 
         fecha DATE,
         FOREIGN KEY(Grupo) REFERENCES Grupos(nombre)
        );
        """

        QueriesSQLite.execute_query(connection, tabla_usuarios, tuple())
        QueriesSQLite.execute_query(connection, tabla_Grupos, tuple())
        QueriesSQLite.execute_query(connection, tabla_Estudiantes, tuple())



if __name__=="__main__":
    # Crear la conexión y las tablas
    connection = QueriesSQLite.create_connection("BankDB.sqlite")
    

    # Insertar un usuario de prueba
    #crear_usuario = """
    #INSERT INTO usuarios (username, nombre, password, tipo)
    #VALUES (?, ?, ?, ?);
    #"""
    #usuario_tuple = ('Pepito', 'Perez', '1111', 'admin')
    #QueriesSQLite.execute_query(connection, crear_usuario, usuario_tuple)

    # Leer los usuarios de la tabla
    #select_usuarios = "SELECT * FROM usuarios"
    #usuarios = QueriesSQLite.execute_read_query(connection, select_usuarios)
    #if usuarios:
    #    for usuario in usuarios:
    #        print(usuario)
    #else:
    #    print("No se encontraron usuarios.")
