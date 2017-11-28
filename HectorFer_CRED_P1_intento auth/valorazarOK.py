#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import urllib,httplib
import re, string, time, schedule
import datetime
import MySQLdb
from beebotte import *

DB_HOST = 'localhost'      # Host BBDD local MySQL
DB_USER = 'root'           # nombre usuario BBDD local MySQL
DB_PASS = 'qwerty'         # contraseña BBDD local MySQL
DB_NAME = 'numeros_azar'   # nombre de la database empleada dentro de la BBDD local MySQL

accesskey  = '4c00f678730355d593d69987efe758e4' 					# accesskey cuenta de BBDD externa beebotte
secretkey  = '9ba8461134d4450954dad21aeaaee68a2e72fc77c9f6777963d1ed7168c7a526'		# secretkey cuenta de BBDD externa beebotte
hostname   = 'api.beebotte.com'								# hostname cuenta de BBDD externa beebotte
bbt = BBT( accesskey, secretkey) #hostname = hostname)					# Accedo a mi cuenta de BBDD externa beebotte

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


def job():
    
    htmlfile = urllib.urlopen("http://www.numeroalazar.com.ar/")    #Abrir/descargar la pagina web
    htmltext = htmlfile.read()                                      #Leer la pagina web

    pattern = re.compile('[0-9]+\.[0-9][0-9]')			    #Patron de expresiones regulares
    valor = re.findall(pattern, htmltext) 			    #Búqueda en la página, los patrones regulares
    print valor					 #(Depuracion)Pinta en pantalla todos los valores que coincidan con la expresion regular (1 o 2 digitos,punto,2 digitos)
    valorbuscado = valor[2]			 		    #Selecciono el valor que deseo 
    print valorbuscado				 #(Depuracion)Pinta en pantalla el valor que deseo seleccionar
    print time.strftime("%Y/%m/%d")		 #(Depuracion)Pinta en pantalla la fecha de la recogida del valor
    print time.strftime("%H:%M:%S")		 #(Depuracion)Pinta en pantalla la hora de la recogida del valor

    # Se ejecuta la solicitud SQL query usando el metodo execute(), anteriormente codificado 
    query = "INSERT INTO TABLA_DATOS (Datos,Hora,Fecha) VALUES (%f,'%s','%s')" %(float(valorbuscado), time.strftime("%H:%M:%S"),time.strftime("%Y/%m/%d"))
    run_query(query)

    bbt.write("Channel2","Datos", float(valorbuscado))               #Almaceno en BBDD externa beebotte(en el canal Channel2, en el recurso datos) el valor deseado
    bbt.write("Channel2","Hora", str(time.strftime("%H:%M:%S")))     #Almaceno en BBDD externa beebotte(en el canal Channel2, en el recurso hora) la hora de recogida
    bbt.write("Channel2","Fecha", str(time.strftime("%Y/%m/%d")))    #Almaceno en BBDD externa beebotte(en el canal Channel2, en el recurso hora) la fecha de recogida

schedule.every(2).minutes.do(job)       # El schedule hace ejecutar la funcion anterior cada 2 min (Recogida automatica de datos cada 2 min)

while 1:
    schedule.run_pending()
    time.sleep(1)
