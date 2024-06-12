import pandas as pd
from mysql.connector import connect, Error

# Funcion para conectarse con Mysql
def conecta():
    try:
        dbConexion = connect(host="localhost", user="root", password="12345",
                             database="Trivago")
        #Comprobar si la conexion  se realizo de manera correcta
        if dbConexion.is_connected():
            print("Conexión exitosa a la base de datos")
            return dbConexion
    except Error as e:
        print(f"Error al conectar: {e}")

#Funcion para seleccionar los primeros 5 servicios del archivo csv
def servi_desta(servicios):
    servicios_list = servicios.split(',')[:5] #.split -- Divide cadenas (En este caso dividio la cadena de "Servicios" y toma los primeros 5 elementos).
    servicios_destacados = ','.join(servicios_list) # .join -- Se utilizo para unir los elementos de la lista en una cadena.
    servicios_destacados = servicios_destacados.replace('[', '').replace(']', '').replace("'", "").strip() # Se utilizo replace para quitar caracteres y espacios en blanco.
    return servicios_destacados


def guardar_datos_csv(archivo_csv):
    dbConexion = conecta()
    df = pd.read_csv(archivo_csv, delimiter=';') # Leer el archivo csv
    try:
        cursor = dbConexion.cursor()
        # Insertar en la tabla de Hoteles
        for index, row in df.iterrows(): 
            sql = "INSERT INTO Hoteles (nombre_hotel, estrellas_hotel, ciudad, direccion, precio_por_noche) VALUES (%s, %s, %s, %s, %s)" # Consulta de Mysql para insertar
            val = (row['Nombre'], row['Estrellas'], row['Ciudad'], row['Direccion'], row['Precio por noche']) # Definir valores
            cursor.execute(sql, val) # Ejecutar

        for index, row in df.iterrows():
            # Insertar en la tabla de Opiniones, en este caso se mando a llamar a un sp para que no haya problemas con las llaves foraneas.
            sql_opinion = "CALL insert_id(%s, %s, %s)" # Mandar a llamar al start procedure (Consulta Mysql).
            val_opinion = (row['Nombre'], row['Calificacion'], row['Numero de reseñas']) # Definir valores
            cursor.execute(sql_opinion, val_opinion) # Ejecutar

        for index, row in df.iterrows():
            servicios_destacados = servi_desta(row['Servicios']) # Se manda a llamar a la funcion "servi_desta" para que limpie la columna de Servicios
            sql_servicio = "CALL insert_servicio(%s, %s)" # Mandar a llamar al start procedure que nos permita insertar en la tabla de Servicios
            val_servicio = (row['Nombre'], servicios_destacados) # Definir valores
            cursor.execute(sql_servicio, val_servicio) # Ejecutar
    finally: 
        dbConexion.commit() # Confirmar cambios
        dbConexion.close()  # Cerrar la conexion



if __name__ == "__main__":
    conecta()
    guardar_datos_csv('C:\\Users\\Daniel\\Documents\\hoteles.csv')