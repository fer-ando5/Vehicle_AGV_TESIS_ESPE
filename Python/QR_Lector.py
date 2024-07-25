import requests
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from io import BytesIO
import paho.mqtt.client as mqtt
import json
import time

# Diccionarios para almacenar datos
diccionarioCiudades = {"AM": "Ambato", "QU": "Quito", "GU": "Guayaquil"}
diccionarioNombres = {"JT": "Jairo Torres", "DP": "Diego Pinta", "AM": "Angie Macias"}
diccionariocedulas = {"0354": "1803645447", "5045": "1150574517", "0092": "2200189278"}

class QRLector:
    def __init__(self):
        # URL de la cámara IP
        self.video_source = 'http://192.168.192.80/640x480.jpg'
        
        # Configuración MQTT
        mqtt_server_ip = "192.168.192.34"
        self.mqtt_server_ip = mqtt_server_ip
        self.client = mqtt.Client()
        self.client.connect(self.mqtt_server_ip)
        self.client.loop_start()  # Iniciar el bucle de red para manejar las publicaciones

    def procesar_codigo_qr(self):
        print("Iniciando el procesamiento de código QR...")
        while True:
            try:
                # Obtener el flujo de video desde la cámara IP
                response = requests.get(self.video_source, stream=True)
                response.raise_for_status()  # Verificar si la solicitud fue exitosa
                bytes_data = BytesIO(response.content)
                byte_frame = bytes_data.getvalue()

                # Convertir los bytes a una imagen de OpenCV
                nparr = np.frombuffer(byte_frame, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is None:
                    print("No se pudo decodificar el frame")
                    continue

                # Mostrar la imagen en una ventana de OpenCV
                cv2.imshow('Cámara en Vivo', frame)

                # Detección de códigos QR en el cuadro
                decoded_objects = decode(frame)
                if decoded_objects:
                    for obj in decoded_objects:
                        qr_data = obj.data.decode('utf-8')
                        if len(qr_data) == 14:
                            print("Código QR detectado:", qr_data)
                            datos = self.separacion(qr_data)
                            self.publicar_datos(datos)  # Publicar los datos en MQTT
                            time.sleep(5)
                            cv2.destroyAllWindows()  # Cerrar la ventana cuando se detecta un código QR válido
                            return datos  # Retornar los datos y detener la función

                # Pausa para permitir la actualización de la ventana
                cv2.waitKey(100)

            except requests.RequestException as req_err:
                print(f"Error en la solicitud HTTP: {req_err}")
            except cv2.error as cv_err:
                print(f"Error en OpenCV: {cv_err}")
            except Exception as e:
                print(f"Error inesperado: {e}")

    cv2.destroyAllWindows()  # Asegurarse de cerrar la ventana en caso de error o salida

    def separacion(self, qr_data):
        verciudad = qr_data[:2]
        vermotor = qr_data[2:4]
        verrpm = qr_data[4:8]
        verinicialn = qr_data[8:10]
        vercedula = qr_data[10:14]

        ciudad = diccionarioCiudades.get(verciudad, "Desconocida")
        nombre = diccionarioNombres.get(verinicialn, "Desconocido")
        cedula = diccionariocedulas.get(vercedula, "Cédula desconocida")

        datos = {
            "Ciudad": ciudad,
            "Motor": vermotor,
            "RPM": verrpm,
            "Nombre": nombre,
            "Cédula": cedula
        }
        time.sleep(0.1)
        print("DATOS:", datos)
        return datos

    def publicar_datos(self, datos):
        for clave, valor in datos.items():
            topic = f"InformacionBox/{clave}"
            mensaje_json = json.dumps({"valor": valor})
            try:
                self.client.publish(topic, mensaje_json)
                print(f"Publicado en {topic}: {mensaje_json}")
            except Exception as e:
                print(f"Error al publicar en {topic}: {e}")
            time.sleep(0.1)  # Añadir una pequeña pausa para evitar problemas de publicación



# Crear instancia de QRLector con la IP del servidor MQTT y procesar códigos QR

# lector = QRLector()
# lector.procesar_codigo_qr()
