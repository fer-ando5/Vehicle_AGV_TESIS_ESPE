import cv2 as cv
import os

CHESS_BOARD_DIM = (9, 6) # Define la dimensión del tablero de ajedrez como una tupla de dos valores

n = 0  #Variable declarada para almacenar la cantidad de imagenes

dir = "Calibracion" #Establece la ruta del directorio donde se guardarán las imágenes.

CHECK_DIR = os.path.isdir(dir) # Comprueba si el directorio de imágenes ya existe.

if not CHECK_DIR: #Verifica si el directorio de imágenes no existe.
    os.makedirs(dir) #Si el directorio no existe, lo crea.
    print(f'"{dir}" Directory is created')
else:
    print(f'"{dir}" Directory already Exists.')

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001) #Establece los criterios de terminación para el algoritmo de búsqueda de esquinas del tablero


def detect_checker_board(image, grayImage, criteria, boardDimension): #Define una función para detectar el tablero de ajedrez en una imagen dada
    ret, corners = cv.findChessboardCorners(grayImage, boardDimension)
    if ret == True:
        corners1 = cv.cornerSubPix(grayImage, corners, (3, 3), (-1, -1), criteria)
        image = cv.drawChessboardCorners(image, boardDimension, corners1, ret)

    return image, ret

cap = cv.VideoCapture(1)

if __name__ == "__main__":
    while True: #Inicia un bucle infinito para capturar continuamente imágenes de la cámara.
        cap.open(1)
        _, frame = cap.read() #Captura un fotograma de la cámara y lo almacena en frame
        copyFrame = frame.copy() # Realiza una copia del fotograma capturado.
        #frame = cv.rotate(frame,cv.ROTATE_90_CLOCKWISE)
        #copyFrame = cv.rotate(copyFrame,cv.ROTATE_90_CLOCKWISE)
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) #Convierte el fotograma a escala de grises

        image, board_detected = detect_checker_board(frame, gray, criteria, CHESS_BOARD_DIM) #Utiliza la función detect_checker_board para detectar el tablero de ajedrez en la imagen
        # print(ret)
        #Agrega un texto al fotograma mostrando el número de imagen guarda
        cv.putText(frame,f"saved_img : {n}",(30, 40),cv.FONT_HERSHEY_PLAIN,1.4,(255,0, 0),2,cv.LINE_AA,)
        cv.imshow("frame", frame)  #Muestra el fotograma en una ventana con el nombre "frame".
        cv.imshow("copyframe", copyFrame)  #Muestra la copia del fotograma en otra ventana con el nombre "copyFrame".

        key = cv.waitKey(5) #Espera la entrada del teclado durante 1 milisegundo.
        if key == ord("q"):
            break
        if key == ord("s") and board_detected == True: #Si se presiona la tecla 's' y se detecta un tablero de ajedrez en la imagen, guarda la imagen.
           cv.imwrite(f"{dir}/image{n}.png", copyFrame) #Guarda la imagen en el directorio de imágenes
           print(f"imagen {n}")
           n += 1  # Incrementa el contador de imágenes guardadas.
        
    cap.release()#Libera los recursos de la cámara.
    cv.destroyAllWindows() #Cierra todas las ventanas abiertas por OpenCV.

print("Images guardadas:", n) #Imprime el número total de imágenes guardadas


