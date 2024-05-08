
import cv2
import time


def Aruco(Buscar):
    marker_size = 100
    # Obtener el diccionario de marcadores ArUco y los parámetros del detector
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_50)
    aruco_params = cv2.aruco.DetectorParameters()

    cap = cv2.VideoCapture(0)  # Iniciar captura desde la cámara (cambiar el número si tienes varias cámaras)

    Ideslista =[]

    detected_ids = set()  # Usamos un conjunto para evitar duplicados de IDs detectados

    while True:
        ret, frame = cap.read()  # Leer un fotograma de la cámara

        if not ret:
            break

        # Convertir el fotograma a escala de grises
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar los marcadores ArUco en el fotograma
        marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(gray_frame, aruco_dict, parameters=aruco_params)
        


        # Verificar si se detectaron marcadores
        if marker_ids is not None:
            # Añadir los IDs de los marcadores detectados a la lista
            for id in marker_ids.flatten():
                if id not in detected_ids:
                    detected_ids.add(id)
                    print(f"Se añadió el número {id} a la lista.")
                    if Buscar != id:
                        Girar()
                    if Buscar == id:
                        Objetivo_encontrado = id
                        Inicio_Pid()


            # Dibujar los marcadores en el fotograma
            cv2.aruco.drawDetectedMarkers(frame, marker_corners, marker_ids)

        # Mostrar el fotograma con los marcadores detectados
        cv2.imshow("Detected ArUco Markers", frame)
        EnvioProcesos(frame, Objetivo_encontrado)
        # Salir del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar la captura y cerrar todas las ventanas
    cap.release()
    cv2.destroyAllWindows()

    #return list(detected_ids)


def Girar():
    print("Girando en proceso..........")

    pass

def Inicio_Pid():
    print("Eniciamos el PID")
    time.sleep(2)
    pass

def EnvioProcesos():
    
    pass
