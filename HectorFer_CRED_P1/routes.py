#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, url_for
from flask import request
import urllib,httplib
import re, string, time, schedule
import datetime
import MySQLdb, os, time, atexit, requests
from beebotte import *
  
app = Flask(__name__)

DB_HOST = 'localhost'      # Host BBDD local MySQL
DB_USER = 'root'           # nombre usuario BBDD local MySQL
DB_PASS = 'qwerty'         # contraseña BBDD local MySQL
DB_NAME = 'numeros_azar'   # nombre de la database empleada dentro de la BBDD local MySQL

accesskey  = '4c00f678730355d593d69987efe758e4' 					# accesskey cuenta de BBDD externa beebotte
secretkey  = '9ba8461134d4450954dad21aeaaee68a2e72fc77c9f6777963d1ed7168c7a526'		# secretkey cuenta de BBDD externa beebotte
hostname   = 'api.beebotte.com'								# hostname cuenta de BBDD externa beebotte
bbt = BBT( accesskey, secretkey, hostname = hostname)					# Accedo a mi cuenta de BBDD externa beebotte


def run_query(query=''): 								# Funcion para acceder y almacenar datos en la BBDD local MySQL
    datos = [DB_HOST, DB_USER, DB_PASS, DB_NAME] 
 
    conn = MySQLdb.connect(*datos) # Conectar a la base de datos 
    cursor = conn.cursor()         # Crear un cursor 
    cursor.execute(query)          # Ejecutar una consulta 
 
    if query.upper().startswith('SELECT'): 
        data = cursor.fetchall()   # Traer los resultados de un select 
    else: 
        conn.commit()              # Hacer efectiva la escritura de datos 
        data = None 
 
    cursor.close()                 # Cerrar el cursor 
    conn.close()                   # Cerrar la conexión 
 
    return data

  
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/', methods=['POST'])
def usuario_pulsa_boton():
    global flag
    fijarumbral=0 
    boton = request.form
    if 'mid_value' in boton:
        if(flag):
            procedencia_local = 'Local'
            valor_medio_local_aux = run_query('SELECT avg(Datos)FROM TABLA_DATOS')
            valor_medio_local = valor_medio_local_aux[0][0]
            flag=0
        else:
            procedencia_local = 'externa'
            leer_ext = bbt.read("Channel2", "Datos", limit=222)
            auto_aux=0
            for i in range(0,222):
                auto_aux = auto_aux + leer_ext[i]['data']
            automatico=auto_aux/222
            valor_medio_local=automatico
            flag=1
        return render_template('home.html', valor_medio= valor_medio_local, procedencia = procedencia_local)
    else:      
        posible_umbral = boton['fijarumbral']
	que = "SELECT * FROM TABLA_DATOS where Datos > " + posible_umbral
        umb = run_query(que)
        pattern2 = re.compile('[0-9]+\.[0-9][0-9]')
        value = re.findall(pattern2,str(umb)) 
    return render_template('home.html', umbral_umbral=umb[0][0],Hora_umbral=umb[0][1],Fecha_umbral=umb[0][2],supera_umbral=value)

@app.route('/umbral')
def umbral():
    #queryquery = run_query('SELECT * FROM TABLA_DATOS where Datos <=50 ORDER BY Fecha DESC LIMIT 2')
    queryquery = run_query('SELECT * FROM TABLA_DATOS where Datos <=50 ORDER BY Fecha DESC LIMIT 1')
    #return render_template('umbral.html', Datos=queryquery[1][0],Hora=queryquery[1][1],Fecha=queryquery[1][2])
    return render_template('umbral.html', Datos=queryquery[0][0],Hora=queryquery[0][1],Fecha=queryquery[0][2])
  
@app.route('/UltimoValor')
def UltimoValor():
    lecturadato = bbt.read("Channel2", "Datos", limit=1)
    lecturadato_aux = lecturadato[0]
    lecturadato_aux2= lecturadato_aux['data']
    lecturahora = bbt.read("Channel2", "Hora", limit=1)
    lecturahora_aux = lecturahora[0]
    lecturahora_aux2= lecturahora_aux['data']
    lecturafecha = bbt.read("Channel2", "Fecha", limit=1)
    lecturafecha_aux = lecturafecha[0]
    lecturafecha_aux2= lecturafecha_aux['data']
    query78 = run_query('SELECT * FROM TABLA_DATOS ORDER BY Fecha DESC LIMIT 3000')
    return render_template('UltimoValor.html', Datos=query78[0][0],Hora=query78[0][1],Fecha=query78[0][2],Datos_ext = lecturadato_aux2,Hora_ext = lecturahora_aux2,Fecha_ext = lecturafecha_aux2)

if __name__ == '__main__':
    flag=0 
    app.debug = True
    app.run(host ='0.0.0.0')