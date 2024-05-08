import math
import cv2
import numpy as np
from typing import List, Tuple, Any
import paho.mqtt.client as mqtt
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import time
import logging

import socket 
import time
import json
import serial

logging.basicConfig(level=logging.INFO)

# Funcion para calculas la estimacion de la distancia con respecto del aruco y la camara, se envia el ID objetivo
#ID objetivo corresponde al que vamos a buscar
def Estimation(ID_Objetivo):

    # Función para verificar si una matriz es una matriz de rotación válida
    coordenadas = [0,0,0,0]
    
    def isRotationMatrix(R):
        Rt = np.transpose(R)  # Transponer la matriz de rotación
        shouldBeIdentity = np.dot(Rt, R)  # Producto punto de la transpuesta con la matriz original
        I = np.identity(3, dtype=R.dtype)  # Matriz de identidad 3x3
        n = np.linalg.norm(I - shouldBeIdentity)  # Norma de la diferencia entre I y shouldBeIdentity
        return n < 1e-6  # Devuelve True si la norma es menor que 1e-6

    # Función para convertir una matriz de rotación en ángulos de Euler
    def rotationMatrixToEulerAngles(R):
        assert (isRotationMatrix(R))  # Verificar si la matriz de rotación es válida
        sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])  # Calcular sy
        singular = sy < 1e-6  # Verificar si sy es singular
        if not singular:
            x = math.atan2(R[2, 1], R[2, 2])  # Calcular x
            y = math.atan2(-R[2, 0], sy)  # Calcular y
            z = math.atan2(R[1, 0], R[0, 0])  # Calcular z
        else:
            x = math.atan2(-R[1, 2], R[1, 1])  # Calcular x en caso de singularidad
            y = math.atan2(-R[2, 0], sy)  # Calcular y en caso de singularidad
            z = 0  # Establecer z en 0 en caso de singularidad
        return np.array([x, y, z])  # Devolver ángulos de Euler como un array

    marker_size = 100  # Tamaño del marcador ArUco
    camera_matrix = np.array([[4.949065755680331904e+02,0.000000000000000000e+00,3.219298146850781563e+02],
                              [0.000000000000000000e+00,4.928480549415890550e+02,2.346512865763718310e+02],
                              [0.000000000000000000e+00,0.000000000000000000e+00,1.000000000000000000e+00]]) 
    camera_distortion = np.array([[1.099028777366317100e-01,
                                   -5.404175609526782331e-01,
                                   1.212558112305444757e-03,
                                   1.456590138562988785e-03,
                                   .735066521572598663e-01]])  
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_50)  # Definir diccionario de marcadores ArUco
    cap = cv2.VideoCapture(0)  # Inicializar captura de vídeo desde la dirección
    cap.set(3, 640)  # Establecer el ancho del fotograma de la cámara
    cap.set(4, 480)  # Establecer el alto del fotograma de la cámara
    while True:  # Bucle infinito para capturar y procesar los fotogramas
        cap.open(0)  # Abrir la captura de vídeo desde la dirección
        ret, frame = cap.read()  # Leer un fotograma del vídeo
        if not ret:  # Verificar si la lectura del fotograma fue exitosa
            break  # Salir del bucle si la lectura no fue exitosa

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convertir el fotograma a escala de grises
        corners, ids, rejected = cv2.aruco.detectMarkers(gray_frame, aruco_dict, camera_matrix, camera_distortion)  # Detectar marcadores ArUco

        # Verificar si se detectaron marcadores y si el ID objetivo está en la lista de IDs
        if ids is not None and ID_Objetivo in ids:
            # Obtener el índice del marcador con el ID objetivo
            indice = np.where(ids == ID_Objetivo)[0][0]
            # Filtrar los marcadores y los IDs para mantener solo la información del marcador objetivo
            corners = [corners[indice]]
            ids = [ID_Objetivo]

            # Dibujar los marcadores detectados en el fotograma
            cv2.aruco.drawDetectedMarkers(frame, corners)
            # Estimar la pose del marcador objetivo
            rvec_list_all, tvec_list_all, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, camera_distortion)
            rvec = rvec_list_all[0][0]
            tvec = tvec_list_all[0][0]
            # Dibujar ejes de coordenadas en el marcador objetivo
            cv2.drawFrameAxes(frame, camera_matrix, camera_distortion, rvec, tvec, 100)
            rvec_flipped = rvec * -1
            tvec_flipped = tvec * -1
            rotation_matrix, jacobian = cv2.Rodrigues(rvec_flipped)
            realworld_tvec = np.dot(rotation_matrix, tvec_flipped)
            pitch, roll, yaw = rotationMatrixToEulerAngles(rotation_matrix)
            #Agregar las coordenadas y el ángulo a la lista
            x = round(realworld_tvec[0],3)
            y = round(realworld_tvec[1],3)
            z = round(realworld_tvec[2],3)
            theta = round(math.degrees(roll),3)
           # Imprimir las coordenadas formateadas
            coordenadas = [x, y, z, theta] #guardamos en coordanadas los datos en una lista
            
            pid = PIDController(0.01, 0.01, 0.1 , 200, 0)
            inicio = False
            if inicio == False:
                pid.Conectar_Blu_Auto() #ejecutamos la funcion para conectar el bluetooth

            #Extraemos las velocidades, ingresando las distancias en Z, X y angulo
            velocidad_Z = pid.compute_Z(int(coordenadas[2]))
            velocidad_X = pid.compute_X(int(coordenadas[0]))
            angulo = pid.compute_Angulo(int(coordenadas[3]))
            print("Datos sensados: ",velocidad_X, velocidad_Z, angulo) #Bandera para verificacion de datos computados

            pid.Matriz_transformacion_Motores(velocidad_X, velocidad_Z,angulo) #Envio para transformar las velocidades delantera, frontal y angular a la velocidad para cada rueda

            tvec_str = "P x=%2.0f y=%2.0f  z=%2.0f O =%2.0f" % (realworld_tvec[0], realworld_tvec[1],realworld_tvec[2], math.degrees(roll))
            cv2.putText(frame, tvec_str, (20, 460), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2, cv2.LINE_AA)
        # Crear una ventana con el nombre 'DETECCION DE ARUCO'
        cv2.namedWindow('DETECCION DE ARUCO')

        # Especificar las coordenadas (x, y) de la esquina superior izquierda de la ventana
        posicion_x = 400  # Cambia esto según la posición deseada en el eje x
        posicion_y = 100  # Cambia esto según la posición deseada en el eje y

        # Mover la ventana a la posición especificada
        cv2.moveWindow('DETECCION DE ARUCO', posicion_x, posicion_y)

        # Mostrar el fotograma con los marcadores
        cv2.imshow('DETECCION DE ARUCO', frame)

        key = cv2.waitKey(3) & 0xFF  # Esperar 1 milisegundo para la entrada del teclado
        
        ###### Regla para que salga de la funcion cuando se cumpla que la distancia es Z es menor a 200 y en X menor a 10 
        if coordenadas[2] <= 200 and abs(coordenadas[0]) <= 10:
            print("Entro en el if")
            pid.Matriz_transformacion_Motores(0,0,0) #Envio de velocidades en 0 para que se detenga el robot
            time.sleep(1) #Tiempo para la escritura
            cap.release()  # Liberar la captura de vídeo
            cv2.destroyAllWindows()  # Cerrar todas las ventanas
            bandera_FIN_PID = 1 # Envio 1 en fin bandera para saber que se termino este proceso y publicar en thingsboard
            return bandera_FIN_PID
    cap.release()  # Liberar la captura de vídeo
    cv2.destroyAllWindows()  # Cerrar todas las ventanas


class PIDController:
    def __init__(self, kp , ki , kd , setpoint_Z, setpoint_X ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint_Z = setpoint_Z
        self.setpoint_X = setpoint_X
        self.prev_error_Z = self.prev_error_X = 0
        self.integral_Z = self.integral_X = 0


        self.mqtt_broker = "192.168.0.86"  # Cambiar a la dirección IP del servidor de thingsboard
        self.mqtt_port = 1883 #puerto de envio de datos para Mqtt
        self.mqtt_topic = "v1/devices/me/telemetry"  


    #Funcion para detemerinar la velocidad del angulo en funcion de que tan lejos esta del angulo que buscamos (PID Rustico)
    def compute_Angulo(self, Angulo):
        print("Esto es angulo: ", Angulo )

        if Angulo > 0:
            if Angulo > 50:
                return 10
            elif Angulo > 20:
                return 6
            elif Angulo > 2:
                return 4
            else :
                return 0
        if Angulo <= 0:
            Angulo = abs(Angulo)
            if Angulo > 50:
                return -10
            elif Angulo > 20:
                return -6
            elif Angulo > 2:
                return -4
            else :
                return 0

    ##Funcion para detemerinar la velocidad frontal en funcion de que tan lejos esta del aruco en Z (PID Rustico)
    def compute_Z(self, DisranciaZ):
        print("Esto es distancia z: ", DisranciaZ )

        if DisranciaZ > 1500:
            return 1.5
        elif DisranciaZ > 600:
            return 1
        elif DisranciaZ > 200:
            return 0.5
        else :
            return 0

    ##Funcion para detemerinar la velocidad Lateral en funcion de que tan lejos esta del aruco en X (PID Rustico)
    def compute_X(self, DistanciaX):

        print("Esto es distancia x: ", DistanciaX )

        if DistanciaX >0:
            if DistanciaX > 1000:
                return 1.5
            elif DistanciaX > 400:
                return 1
            elif DistanciaX >10:
                return 0.5
            else:
                return 0
            
        elif DistanciaX <= 0:

            DistanciaX = abs(DistanciaX)
            if DistanciaX > 1000:
                return -1.5
            elif DistanciaX > 400:
                return -1
            elif DistanciaX >10:
                return -0.5
            else:
                return 0


    #Funcion para determinar la velocidad de cada rueda usando la ecuacion cinametica del ROBOT mecanum de 4 ruedas (Esta ecuacion toma la velocidad: Frontal, lateral y angular)
    def Matriz_transformacion_Motores(self, velocidad_X, velocidad_Z, angulo):
        # Definir las matrices
        matriz1 = np.array([[1, -1, -0.33], #el valor de -0.33 corresponde a una constante la cual es la suma de la distancia entre los ejes de la rueda y la distancia entre la mitad de la rueda y la mitad del robot
                            [1, 1, 0.33],
                            [1, 1, -0.33],
                            [1, -1, 0.33]])

        matriz2 = np.array([[velocidad_Z],
                            [velocidad_X],
                            [angulo]])

        # Multiplicación de matrices
        resultado = np.dot(matriz1, matriz2)
        resultado_multiplicado = resultado * (1/ 0.05) #el 0.05 corresponde al radio de la rueda mecanum
       
        self.W1 = max(min(resultado_multiplicado[0][0], 255), -255) #Limitamos la salida a 255 y -255
        self.W2 = max(min(resultado_multiplicado[1][0], 255), -255)
        self.W3 = max(min(resultado_multiplicado[2][0], 255), -255)
        self.W4 = max(min(resultado_multiplicado[3][0], 255), -255)


        # Imprimir los valores de las variables individuales para ver que sale xd
        print("Valor de W1:", self.W1)
        print("Valor de W2:", self.W2)
        print("Valor de W3:", self.W3)
        print("Valor de W4:", self.W4)

        self.Enviar_arduino_blu() #funcion para envio de datos por bluetooth

    #Funcion de envio de datos mediante bluetooth
    def Enviar_arduino_blu(self):
        #data corresponde a un diccionario
        data = {
            "Modo" : "Auto",
            "m1_vel": self.W1,
            "m2_vel": self.W2,
            "m3_vel": self.W3,
            "m4_vel": self.W4,
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        time.sleep(0.5)
        pass
    
    #Funcion para concetar bluetooth mediante el puerto bluetooth de mi pc
    def Conectar_Blu_Auto(self):
        self.serialArduino = serial.Serial("COM12", 115200)  # Reemplaza 'COM1' por el puerto serie correspondiente
        inicio = True
        return inicio
        pass
