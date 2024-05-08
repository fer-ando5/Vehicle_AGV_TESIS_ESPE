import math
import cv2
import numpy as np
from typing import List, Tuple, Any

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
            tvec_str = "P x=%2.0f y=%2.0f  z=%2.0f O =%2.0f" % (realworld_tvec[0], realworld_tvec[1],realworld_tvec[2], math.degrees(roll))
            cv2.putText(frame, tvec_str, (20, 460), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2, cv2.LINE_AA)

        cv2.imshow('DETECCION DE ARUCO', frame)  # Mostrar el fotograma con los marcadores

        key = cv2.waitKey(1) & 0xFF  # Esperar 1 milisegundo para la entrada del teclado
        if key == ord('q'):  # Verificar si se presionó la tecla 'q'
            break  # Salir del bucle si se presionó la tecla 'q'

    cap.release()  # Liberar la captura de vídeo
    cv2.destroyAllWindows()  # Cerrar todas las ventanas

# Llamada a la función principal con el ID del marcador objetivo especificado
ID_Objetivo = 1  # Aquí debes especificar el ID del marcador que deseas detectar
Estimation(ID_Objetivo)  # Llamar a la función principal con el ID objetivo