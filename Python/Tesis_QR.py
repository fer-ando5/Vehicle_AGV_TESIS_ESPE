import time
import tkinter as tk
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt
import requests
from io import BytesIO
import cv2
from pyzbar.pyzbar import decode
import numpy as np

diccionarioCiudades={"AM": "Ambato","QU": "Quito","GU": "Guayaquil"}
diccionarioNombres={"JT": "Jairo Torres","DP":"Diego Pinta","AM":"Angie Macias"}
diccionariocedulas={"0354":"1803645447","5045":"1150574517","0092":"2200189278"}


class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        # URL de la cámara IP
        # self.video_source = 'http://192.168.0.85/640x480.jpg'
        self.video_source = 'http://192.168.11.85/640x480.jpg'

        # Tamaño deseado del lienzo
        self.canvas_width = 800
        self.canvas_height = 600

        # Crear un lienzo (canvas) en la ventana para mostrar el video
        self.canvas = tk.Canvas(window, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        # Configuración de MQTT para ThingsBoard
        self.mqtt_broker = "192.168.0.86"  # Cambiar a la dirección IP de la laptop Lenovo
        self.mqtt_port = 1883
        self.mqtt_topic = "v1/devices/me/telemetry"  
        self.access_token = "6uWlyUoDW6IdKS7alLYG" 

        # Crear un atributo para almacenar la imagen del lienzo
        self.photo = None

        # Frecuencia de actualización del lienzo (en milisegundos)
        self.delay = 10

        # Iniciar la función de actualización continua del lienzo
        self.update()

        # Mantener la ventana abierta
        self.window.mainloop()

    # Función para actualizar el lienzo con el video y la detección de códigos QR
    def update(self):
        try:
            # Obtener el flujo de video desde la cámara IP
            response = requests.get(self.video_source, stream=True)
            bytes_data = BytesIO(response.content)
            byte_frame = bytes_data.getvalue()

            # Convertir los bytes a una imagen de OpenCV
            nparr = np.frombuffer(byte_frame, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Convertir el cuadro de BGR a RGB y crear una imagen de tkinter
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img.thumbnail((self.canvas_width, self.canvas_height))  # Ajustar tamaño de imagen al lienzo
            self.photo = ImageTk.PhotoImage(image=img)

            # Mostrar la imagen en el lienzo
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

            # Detección de códigos QR
            self.read_qr_code(frame)

        except Exception as e:
            print("Error:", e)

        # Llamar a la función de actualización nuevamente después de un breve retraso
        self.window.after(self.delay, self.update)

    def separacion(self, qr_data):
        verciudad= qr_data[:2]
        vermotor = qr_data[2:4]
        verrpm=qr_data[5:8]
        verinicialn= qr_data[8]+ qr_data[11]
        print(qr_data[8])
        vercedula=str(qr_data[9:11])+str(qr_data[12:14])
        print("Ciudad",verciudad,"Motor",vermotor,"RPM",verrpm,"Iniciales",verinicialn,"Cedula",vercedula)
        self.send_to_thingsboard(qr_data,verciudad,vermotor,verrpm,verinicialn,vercedula)  # Enviar el texto del código QR a ThingsBoard

    # Función para leer el código QR
    def read_qr_code(self, frame):
        # Detección de códigos QR en el cuadro
        decoded_objects = decode(frame)
        if decoded_objects:
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                validarQR=len(qr_data)
                print(validarQR)
                if validarQR==14:
                    print("Código QR detectado:", qr_data)
                    self.separacion(qr_data)
                else :
                    print ("no es un codigo valido")
   
   
    # Función para enviar datos a ThingsBoard
    def send_to_thingsboard(self, data,verciudad,vermotor,verrpm,verinicialn,vercedula):
        try:
            client = mqtt.Client()
            print(client)
            client.username_pw_set(self.access_token)
            client.connect(self.mqtt_broker, self.mqtt_port, 60)
            payload = '{"Codigo": "' + data + '", "Ciudad": "' + diccionarioCiudades[verciudad] + '", "Motor (V)": "' + vermotor + '", "RPM": "' + verrpm + '", "Cliente": "' + diccionarioNombres[verinicialn] + '", "Cedula": "' + diccionariocedulas[vercedula] + '"}'
            print(payload)
            client.publish(self.mqtt_topic, payload, qos=1)
            time.sleep(1)  # Agrega un retraso de 1 segundo antes de desconectar el cliente
            client.disconnect()
            print("Datos enviados a ThingsBoard correctamente.")
        except Exception as e:
            print("Error al enviar datos a ThingsBoard:", e)

# Crear una instancia de la aplicación con una ventana de tkinter
App(tk.Tk(), "Interfaz de Cámara IP y Detección de Códigos QR")
