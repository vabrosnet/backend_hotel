from flask import Flask, request, jsonify
from datetime import datetime
from flask import request
from flask_cors import CORS

import mysql.connector
from werkzeug.utils import secure_filename
import os
import time

#import config.conexion as conexion

app = Flask(__name__)
CORS(app)


class Catalogo:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host, 
            user=user, 
            password=password
            )
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS reservas (
            codigo INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
            fecha_llegada DATE NOT NULL,
            fecha_salida DATE NOT NULL,
            habitacion VARCHAR(255) NOT NULL,
            apellido VARCHAR(255) NOT NULL,
            nombre VARCHAR(255) NOT NULL,
            dni INT NOT NULL,
            telefono VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL)''')
        self.conn.commit()

        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def listar_reservas(self):
        self.cursor.execute("SELECT * FROM reservas")
        reservas = self.cursor.fetchall()
        return reservas
    
    def consultar_reserva(self, codigo):
        self.cursor.execute(f"SELECT * FROM reservas WHERE codigo = {codigo}")
        return self.cursor.fetchone()
    
    def agregar_reserva(self, fecha_llegada, fecha_salida, habitacion, apellido, nombre, dni, telefono, email):
        consulta = "SELECT * FROM reservas WHERE fecha_llegada = %s AND fecha_salida = %s AND habitacion = %s"
        self.cursor.execute(consulta, (fecha_llegada, fecha_salida, habitacion))
                
        reserva_existe = self.cursor.fetchone()
        if reserva_existe:
            return False

        sql = "INSERT INTO reservas (fecha_llegada, fecha_salida, habitacion, apellido, nombre, dni, telefono, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        valores = (fecha_llegada, fecha_salida, habitacion, apellido, nombre, dni, telefono, email)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return True

    def modificar_reserva(self, codigo, fecha_llegada, fecha_salida, habitacion, apellido, nombre, dni, telefono, email):
        sql = "UPDATE reservas SET fecha_llegada = %s, fecha_salida = %s, habitacion = %s, apellido = %s, nombre = %s, dni = %s, telefono = %s, email = %s WHERE codigo = %s"
        valores = (fecha_llegada, fecha_salida, habitacion, apellido, nombre, dni, telefono, email, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def eliminar_reserva(self, codigo):
        self.cursor.execute(f"DELETE FROM reservas WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    #Fin clase

catalogo = Catalogo(host='localhost', user='root', password='123456',
database='hotel_argentino')
ruta_destino = './static/imagenes/'


#Listar reservas
@app.route("/reservas", methods=["GET"])
def listar_reservas():
    reservas = catalogo.listar_reservas()
    return jsonify(reservas)

#Ver una reserva
@app.route("/reservas/<int:codigo>", methods=["GET"])
def mostrar_reserva(codigo):
    reserva = catalogo.consultar_reserva(codigo)
    if reserva:
        return jsonify(reserva)
    else:
        return "Reserva no encontrada", 404

#Agregar reserva
@app.route("/reservas", methods=["POST"])
def agregar_reserva():
    fecha_llegada = request.form['fecha_llegada']
    fecha_salida = request.form['fecha_salida']
    habitacion = request.form['habitacion']
    apellido = request.form['apellido']
    nombre = request.form['nombre']
    dni = request.form['dni']
    telefono = request.form['telefono']
    email = request.form['email']
    
    if catalogo.agregar_reserva(fecha_llegada, fecha_salida, habitacion, apellido, nombre, dni, telefono, email):
        return jsonify({"mensaje": "Reserva agregada"}), 201
    else:
        return jsonify({"mensaje": "Reserva ya existe"}), 400

#Modificar reserva
@app.route("/reservas/<int:codigo>", methods=["PUT"])
def modificar_reserva(codigo):
    nueva_fecha_llegada = request.form.get('fecha_llegada')
    nueva_fecha_salida = request.form.get('fecha_salida')
    nueva_habitacion = request.form.get('habitacion')
    nueva_apellido = request.form.get('apellido')
    nueva_nombre = request.form.get('nombre')
    nueva_dni = request.form.get('dni')
    nueva_telefono = request.form.get('telefono')
    nueva_email = request.form.get('email')

    if catalogo.modificar_reserva(codigo, nueva_fecha_llegada, nueva_fecha_salida, nueva_habitacion, nueva_apellido, nueva_nombre, nueva_dni, nueva_telefono, nueva_email):
        return jsonify({"mensaje": "Reserva modificada"}), 200
    else:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404

#Eliminar reserva
@app.route("/reservas/<int:codigo>", methods=["DELETE"])
def eliminar_reserva(codigo):
    reserva = catalogo.consultar_reserva(codigo)
    if reserva:
        if catalogo.eliminar_reserva(codigo):
            return jsonify({"mensaje": "Reserva eliminada"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar la reserva"}), 500
    else:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404

if __name__ == "__main__":
    app.run(debug=True)
