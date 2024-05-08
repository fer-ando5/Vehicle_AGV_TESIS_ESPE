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

# Definición de la función principal
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
            coordenadas = [x, y, z, theta]
            #print(coordenadas)
            pid = PIDController(0.01, 0.01, 0.1 , 200, 0)
            inicio = False
            if inicio == False:
                pid.Conectar_Blu_Auto()
            velocidad_Z = pid.compute_Z(int(coordenadas[2]))
 
            velocidad_X = pid.compute_X(int(coordenadas[0]))

            angulo = pid.compute_Angulo(int(coordenadas[3]))

            print("Datos sensados: ",velocidad_X, velocidad_Z, angulo)
            pid.Matriz_transformacion_Motores(velocidad_X, velocidad_Z,angulo)

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
        if coordenadas[2] <= 200 and abs(coordenadas[0]) <= 10:
            print("Entro en el if")
            pid.Matriz_transformacion_Motores(0,0,0)
            time.sleep(1)
            cap.release()  # Liberar la captura de vídeo
            cv2.destroyAllWindows()  # Cerrar todas las ventanas
            bandera_FIN_PID = 1
            #pid.desconectar()
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


        self.mqtt_broker = "192.168.0.86"  # Cambiar a la dirección IP de la laptop Lenovo
        self.mqtt_port = 1883 #puerto de envio de datos para Mqtt
        self.mqtt_topic = "v1/devices/me/telemetry"  
        '''
        self.client = mqtt.Client() 
        token_robot= "NNz7OFhy2WnVm6eDB56x"
        token_referencia = token_robot
        self.client.username_pw_set(token_referencia)
        self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
        '''
        #self.connect_to_thingsboard()



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

        '''
        if DisranciaZ > 2000:
            velZ = 7
            print("Esto es velZ: ", velZ )
            return velZ
        elif DisranciaZ > 1500:
            velZ = 6 + (DisranciaZ - 1500) / 500  # Incremento lineal desde 6 a 7
            print("Esto es velZ: ", velZ )
            return velZ
        elif DisranciaZ > 1000:
            velZ = 5 + (DisranciaZ - 1000) / 500  # Incremento lineal desde 5 a 6
            print("Esto es velZ: ", velZ )
            return velZ
        elif DisranciaZ > 600:
            velZ = 3 + (DisranciaZ - 600) / 400    # Incremento lineal desde 4 a 5
            print("Esto es velZ: ", velZ )
            return velZ
        elif DisranciaZ > 400:
            velZ = 2 + (DisranciaZ - 400) / 200    # Incremento lineal desde 3 a 4
            print("Esto es velZ: ", velZ )
            return velZ
        elif DisranciaZ > 200:
            velZ = 2 + (DisranciaZ - 200) / 200    # Incremento lineal desde 2 a 3
            return velZ
        '''
        
        '''
        error = DisranciaZ - self.setpoint_Z
        self.integral_Z += error
        derivative = error - self.prev_error_Z
        self.prev_error_Z = error
        output = self.kp * error + self.ki * self.integral_Z + self.kd * derivative
        # Limitar la salida dentro del rango de 0 a 187
        output = max(min(output, 50), 0)
        Escalado_Z = output/50
        return Escalado_Z
        '''

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

            '''
            if DistanciaX > 2000:
                VelX = 6
                print("Esto es vel x: ", VelX )
                return VelX
            elif DistanciaX > 1000:
                VelX = round(5 + (DistanciaX - 1000) / 1000  , 2)
                return VelX
            elif DistanciaX > 400:
                VelX = round(4 + (DistanciaX - 400) / 600 , 2)

                return VelX
            elif DistanciaX > 100:
                VelX = round(3 + (DistanciaX - 100) / 300  , 2)

                return VelX
            elif DistanciaX > 50:
                VelX = round(2 + (DistanciaX - 50) / 50  , 2)
    
                return VelX
            elif DistanciaX > 10:
                VelX = round(2 + (DistanciaX - 10) / 40   , 2)
                return VelX
        
        if DistanciaX <0:
            DismodX = abs(DistanciaX)
            print("Esto es negativo distancia x", DismodX )
            if DismodX > 2000:
                VelX = 6
                print("Esto es vel x: ", VelX )
                return -VelX
            elif DismodX > 1000:
                VelX = 5 + (DistanciaX - 1000) / 1000  # Incremento lineal desde 6 a 7
                print("Esto es vel x: ", VelX )
                return -VelX
            elif DismodX > 400:
                VelX = 4 + (DistanciaX - 400) / 600    # Incremento lineal desde 5 a 6
                print("Esto es vel x: ", VelX )
                return -VelX
            elif DismodX > 100:
                VelX = 3 + (DistanciaX - 100) / 300    # Incremento lineal desde 4 a 5
                print("Esto es vel x: ", VelX )
                return -VelX
            elif DismodX > 50:
                VelX = 2 + (DistanciaX - 50) / 50      # Incremento lineal desde 3 a 4
                print("Esto es vel x: ", VelX )
                return -VelX
            elif DismodX > 10:
                VelX = 2 + (DistanciaX - 10) / 40      # Incremento lineal desde 2 a 3
                print("Esto es vel x: ", VelX )
                return -VelX
        '''
        
        '''
        error = abs(valor_X) - self.setpoint_X
        self.integral_X += error
        derivative = error - self.prev_error_X
        self.prev_error_X = error
        output = self.kp * error + self.ki * self.integral_X + self.kd * derivative
        # Limitar la salida dentro del rango de 0 a 187
        Escalado_X = output/50
        return -Escalado_X if valor_X < 0 else Escalado_X
        '''



    def Matriz_transformacion_Motores(self, velocidad_X, velocidad_Z, angulo):
        # Definir las matrices
        matriz1 = np.array([[1, -1, -0.33],
                            [1, 1, 0.33],
                            [1, 1, -0.33],
                            [1, -1, 0.33]])

        matriz2 = np.array([[velocidad_Z],
                            [velocidad_X],
                            [angulo]])

        # Multiplicación de matrices
        resultado = np.dot(matriz1, matriz2)
        resultado_multiplicado = resultado * (1/ 0.05)
        #resultado_multiplicado =(-1)*resultado_multiplicado 

        # Desempaquetar los valores de la matriz resultante en variables individuales
        #self.W1, self.W2, self.W3, self.W4 = resultado_multiplicado.flatten()
        self.W1 = max(min(resultado_multiplicado[0][0], 255), -255)
        self.W2 = max(min(resultado_multiplicado[1][0], 255), -255)
        self.W3 = max(min(resultado_multiplicado[2][0], 255), -255)
        self.W4 = max(min(resultado_multiplicado[3][0], 255), -255)


        # Imprimir los valores de las variables individuales
        print("Valor de W1:", self.W1)
        print("Valor de W2:", self.W2)
        print("Valor de W3:", self.W3)
        print("Valor de W4:", self.W4)

        self.Enviar_arduino_blu()

        
    '''
    def Envio_velocidades(self):
        try: 
            payload = '{"W1": "' + str(self.W1) + '", "W2": "' + str(self.W2) + '", "W3": "' + str(self.W3) + '", "W4": "' + str(self.W4) + '"}'
            self.client.publish(self.mqtt_topic, payload, qos=1)
            time.sleep(0.2)  # Agrega un retraso de 1 segundo antes de desconectar el cliente
            print("Datos enviados a ThingsBoard correctamente.")
        except Exception as e:
            print("Error al enviar datos a ThingsBoard:", e)      

    def __del__(self):
        # Desconectar el cliente MQTT al destruir la instancia
        self.client.disconnect()
    
    '''

    def on_connect(self, client, userdata, flags, result_code, *extra_params, tb_client):
        attributes = {"W1": self.W1}
        if result_code == 0:
            logging.info("Connected to ThingsBoard!")
            # Sending attributes
            result = tb_client.send_attributes(attributes)
            result.get()
            #time.sleep(0.1)
            logging.info("Attribute update sent: " + str(result.rc() == TBPublishInfo.TB_ERR_SUCCESS))
            #tb_client.disconnect()
        else:
            logging.error("Failed to connect to ThingsBoard with result code: %d", result_code)
        

    def connect_to_thingsboard(self):
        self.client = TBDeviceMqttClient("192.168.0.86", username="NNz7OFhy2WnVm6eDB56x")
        

    def Envio_atrbutos_2(self):
        self.client.connect(callback=self.on_connect)


    def desconectar(self):
        self.client.disconnect()


    def Enviar_arduino_blu(self):
        
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

    def Conectar_Blu_Auto(self):
        self.serialArduino = serial.Serial("COM12", 115200)  # Reemplaza 'COM1' por el puerto serie correspondiente
        inicio = True
        return inicio
        pass
