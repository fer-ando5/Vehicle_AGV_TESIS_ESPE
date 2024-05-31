## Version 3 
#OBJETIVO: Se realizara una interfaz simple, en modo automatico, solo tendra 3 botones y cada que se inicie un proceso de se mostrara
#en una ventana diferente y solo por ese tiempo luego se cerrara para continuar
# NOTA 
# 
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import time

import Tesis_Funciones_Version
import IdentificadorIdAruco


import cv2
import Aruco_Medicion_Distancia

import serial
import json

##########################################  Variables #########################################
valoranteriorcajamesa1 = 3
cajavalormesa1 = 4
errorescajamesa1=1

########################################################## MODO AUTOMATICO ################################################################################


class VentanaAutomatico:
    def __init__(self, master):
        self.master = master
        master.title("Ventana de Modo Automaticó Iniciada")
        self.master.geometry("600x150")
        # Obtener el ancho y alto de la pantalla
        ancho_pantalla = master.winfo_screenwidth()
        alto_pantalla = master.winfo_screenheight()
        # Crear la instancia de Tk
        
        # self.serialArduino = serial.Serial("COM12", 115200)  # Reemplaza 'COM1' por el puerto serie correspondiente
        self.serialArduino = serial.Serial("/dev/tty.HC-05", 115200)  # Reemplaza 'COM1' por el puerto serie correspondiente
        
        self.velocidad = 30

        # Crear la instancia de la clase VentanaAutomatico y pasarle la instancia de Tk
        # Iniciar el bucle de eventos de Tkinter
        
        # Calcular las coordenadas para centrar la ventana en la parte superior
        x = (ancho_pantalla - 600) // 2  # 600 es el ancho de la ventana
        y = 0  # La ventana estará en la parte superior
        
        # Establecer la posición de la ventana
        master.geometry(f"600x150+{x}+{y}")
        Titulo=tk.Label(master,text="Modo Automaticó", font=("Arial", 20))
        Titulo.pack()

        self.Area_botonesAuto = tk.Frame(master)  # Crear un frame para contener los botones
        self.Area_botonesAuto.pack(pady=10) 

        self.botonInicioA = tk.Button(self.Area_botonesAuto, text ="Inicio",command=self.Validaciones_Inicio, width=15, height=2)
        self.botonInicioA.pack(side=tk.LEFT, padx=10)

        self.boton_reiniciarA = tk.Button(self.Area_botonesAuto, text="Reiniciar", width=15, height=2)  # Crear un botón con texto y comando asociado
        self.boton_reiniciarA.pack(side=tk.LEFT, padx=10)  # Empaquetar el botón en el frame, alineado a la izquierda con un espacio horizontal de 10 píxeles

        self.boton_regresar = tk.Button(self.Area_botonesAuto, text="Regresar", command=abrir_ventana_principal_auto ,width=15, height=2)  # Crear un botón con texto y comando asociado
        self.boton_regresar.pack(side=tk.LEFT, padx=10)  # Empaquetar el botón en el frame, alineado a la izquierda con un espacio horizontal de 10 píxeles

        self.boton_salirA = tk.Button(self.Area_botonesAuto, text="Salir", command=VenAuto.quit, width=15, height=2)  # Crear un botón con texto y comando asociado
        self.boton_salirA.pack(side=tk.LEFT, padx=10)  # Empaquetar el botón en el frame, alineado a la izquierda con un espacio horizontal de 10 píxeles

        # Crear un Label para mostrar el estado
        self.label_estado = tk.Label(master, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.label_estado.pack(side=tk.BOTTOM, fill=tk.X)

##################################### FINAL DE INTERFAZ GRAFICA ###################################################

    #Funcion al procesar el boton de inicio
    def Validaciones_Inicio(self):
        funciones_complementarias = Tesis_Funciones_Version.Funciones_Complementarias() #Inicializamos el fichero de tesis funciones version complementarias
        print("Inicia el proceso de validaciones_Inicio")
        self.Existe_caja = funciones_complementarias.Validaion_Caja_Mesa() #Funcion para la validacion de la caja
        print(self.Existe_caja)
        time.sleep(2)
        if self.Existe_caja == 0:
            message = " " * 10 + "PRECAUCIÓN\n\nROBOT EN MOVIMIENTO"
            # Mostrar el cuadro de advertencia de inicio de movimiento del robot
            messagebox.showwarning("Advertencia", message, icon="warning", parent=self.master)
            print("Detectamos caja y pasamos a enviar atributos")
            funciones_complementarias.Enviar_atributos("Robot","Inicio",True) #Enviamos los atributos a thingsboard sobre que el tema Inicio con el atributo TRUE para llevar el monitoreo en thingsboard
            self.label_estado.config(text="Iniciando proceso, tenga cuidado con el robot")  # Actualiza el texto del Label
            Objetivo_Aruco = 1 #asignamos el aruco objetivo ya que el aruco ID 1 corresponde al la mesa donde estara la caja
            Verificador_Aruco = False #Inicializamos verificacion aruco en false
            while Verificador_Aruco == False:
                print("Entro en el while para buscar el aruco")
                Verificador_Aruco , Objetivo_Aruco = self.Aruco(Objetivo_Aruco) #Llamamos a la funcion para la busqueda del aruco
            print("Salio del while para buscar el aruco")
            self.Bandera_Fin_PID = Aruco_Medicion_Distancia.Estimation(Objetivo_Aruco) #Llamamos a la funcion de estimacion para empezar con la navegacion


            funciones_complementarias.Enviar_atributos("Robot","Inicio",False) #Al final del proceso enviamos False para el monitoreo y decir que se finalizo el proceso de clasificacion de la caja
        elif self.Existe_caja == 1: #Si no existe la caja se ejecuta esta funcion y se muestra un mensaje de alerta
            print("No existe Caja")
            self.label_estado.config(text="NO EXISTE CAJA PARA INICIAR EL PROCESO, PONGA UNA CAJA Y LUEGO PRESIONE INICIO")  # Actualiza el texto del Label
            funciones_complementarias.Enviar_atributos("Robot","Inicio",False)
            messagebox.showwarning("Advertencia", "NO EXISTE CAJA PARA INICIAR EL PROCESO, PONGA UNA CAJA Y LUEGO PRESIONE INICIO", icon="warning", parent=self.master)
            
        
#Funcion para identificar los arucos y buscar el aruvo objetivo a ser buscado
    def Aruco(self, Buscar):
        marker_size = 100
        # Obtener el diccionario de marcadores ArUco y los parámetros del detector
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_50)
        aruco_params = cv2.aruco.DetectorParameters()
        cap = cv2.VideoCapture(0) # Iniciar captura desde la cámara (cambiar el número si tienes varias cámaras)
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
                    if id not in detected_ids: #Compara los arucos
                        detected_ids.add(id)
                        if Buscar != id: # si el aruco que se agrega no es el objetivo se ejecuta la funcion Girar la cual mantiene girando al robot hasta que encuentre el aruco objetivo
                            self.Girar() #Funcion de girar el robot
                        if Buscar == id: #Cuando el aruco objetivo es encontrado 

                            Verificador_Aruco = True #Asiganamos el valor de true para decir que si se encontro el aruco objetivo
                            data = {
                                "Modo" : str("Quieto"), #Detenemos al robot
                                }
                            # Convertir el diccionario a una cadena JSON
                            json_data = json.dumps(data)
                            # Enviar la cadena JSON a Arduino a través del puerto serie
                            self.serialArduino.write(json_data.encode())
                            time.sleep(1)
                            self.serialArduino.close() # Cerramos el envio de datos bluetooth
                            time.sleep(0.5)
                            cap.release() 
                            cv2.destroyAllWindows()
                            return Verificador_Aruco , id 
                # Dibujar los marcadores en el fotograma
                cv2.aruco.drawDetectedMarkers(frame, marker_corners, marker_ids)
            
            # Crear una ventana con el nombre 'DETECCION DE ARUCO'
            cv2.namedWindow('DETECCION DE ARUCO')

            # Especificar las coordenadas (x, y) de la esquina superior izquierda de la ventana
            posicion_x = 20  # Cambia esto según la posición deseada en el eje x
            posicion_y = 200  # Cambia esto según la posición deseada en el eje y

            # Mover la ventana a la posición especificada
            cv2.moveWindow('DETECCION DE ARUCO', posicion_x, posicion_y)

            # Mostrar el fotograma con los marcadores
            cv2.imshow('DETECCION DE ARUCO', frame)

            # Salir del bucle si se presiona la tecla 'q'
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def Girar(self):
        print("Girando........")
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Giro_Antihorario",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

########################################################## MODO MANUAL ################################################################################

class VentanaManual:
    def __init__(self, master):
        self.master = master
        master.title("Ventana de Modo Manual Iniciada")
        self.master.geometry("900x700")
        # Aquí colocas el código para la ventana de modo manual
        # self.serialArduino = serial.Serial("COM12", 115200)  # Reemplaza 'COM1' por el puerto serie correspondiente
        self.serialArduino = serial.Serial("/dev/tty.HC-05", 115200)  # Reemplaza 'COM1' por el puerto serie correspondiente
        master.title("Ventana de Modo Manual Iniciada")
        #Titulo=tk.Label(VenManual,text="Modo Manual")
        #Titulo.pack()
        
        # Obtener el ancho y alto de la pantalla
        ancho_pantalla = master.winfo_screenwidth()
        alto_pantalla = master.winfo_screenheight()

        # Calcular las coordenadas para centrar la ventana
        x = (ancho_pantalla - 900) // 2  # 900 es el ancho de la ventana
        y = (alto_pantalla - 750) // 2   # 700 es el alto de la ventana

        # Establecer la posición de la ventana
        master.geometry(f"900x700+{x}+{y}")
        
        self.velocidad = 50

        # Crear el título que abarca toda la parte superior
        titulo = tk.Label(master, text="MODO MANUAL", font=("Arial", 16))
        titulo.pack(fill=tk.X)  # Se extiende horizontalmente

        # Crear el frame izquierdo para contener los botones
        self.area_izquierda = tk.Frame(master)
        self.area_izquierda.pack(side=tk.LEFT, padx=10, pady=10)  # Se adhiere a la izquierda, con espacio exterior
        Valto = 1
        Vancho = 5
        # Botones en el área izquierda
        self.boton1 = tk.Button(self.area_izquierda, text="↖",font=("Arial", 20),width=Vancho, height=Valto)
        self.boton1.grid(row=0, column=0, padx=5, pady=5)  # Colocar en la fila 0, columna 0, con espacio exterior
        self.boton1.bind("<Button-1>", self.Diagonal_Superior_IZQ)
        self.boton1.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton2 = tk.Button(self.area_izquierda, text="↑",font=("Arial", 20),width=Vancho, height=Valto)
        self.boton2.grid(row=0, column=1, padx=5, pady=5)  # Colocar en la fila 0, columna 1, con espacio exterior
        self.boton2.bind("<Button-1>", self.Adelante)
        self.boton2.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton3 = tk.Button(self.area_izquierda, text="↗", font=("Arial", 20),width=Vancho, height=Valto)
        self.boton3.grid(row=0, column=2, padx=5, pady=5)  # Colocar en la fila 0, columna 2, con espacio exterior
        self.boton3.bind("<Button-1>", self.Diagonal_Superior_DER)
        self.boton3.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton4 = tk.Button(self.area_izquierda, text="←", font=("Arial", 20),width=Vancho, height=Valto)
        self.boton4.grid(row=1, column=0, padx=5, pady=5)  # Colocar en la fila 1, columna 0, con espacio exterior
        self.boton4.bind("<Button-1>", self.Izquierda)
        self.boton4.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton5 = tk.Button(self.area_izquierda, text="HOME",width=12, height=3)
        self.boton5.grid(row=1, column=1, padx=5, pady=5)  # Colocar en la fila 1, columna 1, con espacio exterior

        self.boton5.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton6 = tk.Button(self.area_izquierda, text="→", font=("Arial", 20),width=Vancho, height=Valto)
        self.boton6.grid(row=1, column=2, padx=5, pady=5)  # Colocar en la fila 1, columna 2, con espacio exterior
        self.boton6.bind("<Button-1>", self.Derecha)
        self.boton6.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton7 = tk.Button(self.area_izquierda, text="↙", font=("Arial", 20),width=Vancho, height=Valto)
        self.boton7.grid(row=2, column=0, padx=5, pady=5)  # Colocar en la fila 2, columna 0, con espacio exterior
        self.boton7.bind("<Button-1>", self.Diagonal_Inferior_IZQ)
        self.boton7.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton8 = tk.Button(self.area_izquierda, text="↓", font=("Arial", 20),width=Vancho, height=Valto)
        self.boton8.grid(row=2, column=1, padx=5, pady=5)  # Colocar en la fila 2, columna 1, con espacio exterior
        self.boton8.bind("<Button-1>", self.Atras)
        self.boton8.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton9 = tk.Button(self.area_izquierda, text="↘", font=("Arial", 20),width=Vancho, height=Valto)
        self.boton9.grid(row=2, column=2, padx=5, pady=5)  # Colocar en la fila 2, columna 2, con espacio exterior
        self.boton9.bind("<Button-1>", self.Diagonal_Inferior_DER)
        self.boton9.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton10 = tk.Button(self.area_izquierda, text="↺", font=("Arial", 20),width=Vancho, height=Valto)
        self.boton10.grid(row=3, column=0, padx=5, pady=5)  # Colocar en la fila 3, columna 0, con espacio exterior
        self.boton10.bind("<Button-1>", self.Giro_Antihorario)
        self.boton10.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton11 = tk.Button(self.area_izquierda, text="↻", font=("Arial", 20),width=Vancho, height=Valto)
        self.boton11.grid(row=3, column=2, padx=5, pady=5)  # Colocar en la fila 3, columna 1, con espacio exterior
        self.boton11.bind("<Button-1>", self.Giro_Horario)
        self.boton11.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton12 = tk.Button(self.area_izquierda, text="Regresar",command=abrir_ventana_principal_manual, width=12, height=2)
        self.boton12.grid(row=5, column=0, padx=5, pady=5)  # Colocar en la fila 4, columna 0, con espacio exterior
        self.boton12.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton13 = tk.Button(self.area_izquierda, text="Salir", command=VenManual.quit, width=12, height=2)
        self.boton13.grid(row=5, column=2, padx=5, pady=5)  # Colocar en la fila 4, columna 1, con espacio exterior
        self.boton13.bind("<ButtonRelease-1>", self.soltar_boton1)

############ Funciones de modo manual

    def Giro_Horario(self, event):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Giro_Horario",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

    def Giro_Antihorario(self, event):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Giro_Antihorario",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

    def Derecha(self, event):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Derecha",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

    def Izquierda(self, event):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Izquierda",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

    def Adelante(self, event):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Adelante",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

    def Atras(self, event):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Atras",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

    def Diagonal_Superior_IZQ(self, event):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Diagonal_Superior_IZQ",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

    def Diagonal_Superior_DER(self, event):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Diagonal_Superior_DER",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

    def Diagonal_Inferior_IZQ(self, event):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Diagonal_Inferior_IZQ",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

    def Diagonal_Inferior_DER(self, event):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Diagonal_Inferior_DER",
            "Dato_velocidad": self.velocidad
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass

    def soltar_boton1(self, event):
        data = {
            "Modo" : str("Quieto"),
            }
        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data)
        # Enviar la cadena JSON a Arduino a través del puerto serie
        self.serialArduino.write(json_data.encode())
        pass


########################################################## Ventana Principal ################################################################################

def abrir_ventana_principal_auto():
    VenAuto.destroy()
    ventana.deiconify()  # Mostrar la ventana principal

def abrir_ventana_principal_manual():

    VenManual.destroy()
    ventana.deiconify()  # Mostrar la ventana principal

def ventana_automatico():
    global VenAuto
    ventana.withdraw()
    VenAuto = tk.Toplevel()
    app = VentanaAutomatico(VenAuto)

def ventana_manual():
    global VenManual
    ventana.withdraw()
    VenManual = tk.Toplevel()
    app = VentanaManual(VenManual)

# Crear la ventana principal
ventana = tk.Tk()
ventana.geometry("600x350")
ventana.title("Ventana de Inicio")

# Obtener el ancho y alto de la pantalla
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()

# Calcular las coordenadas para centrar la ventana
x = (ancho_pantalla - 600) // 2  # 600 es el ancho de la ventana
y = (alto_pantalla - 400) // 2   # 350 es el alto de la ventana

# Establecer la posición de la ventana
ventana.geometry(f"600x350+{x}+{y}")


etiqueta = tk.Label(ventana, text="Universidad de las Fuerzas Armadas ESPE Sede Latacunga", font=("Arial", 14), width=17, height=3)
etiqueta.pack(fill=tk.X, expand=True)  # Centrar verticalmente la etiqueta

etiqueta2 = tk.Label(ventana, text="Ingenieria Mecatrónica", font=("Arial", 14), width=17, height=3)
etiqueta2.pack(fill=tk.X, expand=True)  # Centrar verticalmente la etiqueta


# Crear un frame para contener los botones
Area_botones = tk.Frame(ventana)
Area_botones.pack(pady=10)

# Botón "Modo Automatico"
boton_auto = tk.Button(Area_botones, text="Modo Automatico", command=ventana_automatico, width=17, height=3)
boton_auto.pack(side=tk.TOP, pady=5)

# Botón "Modo Manual"
boton_manual = tk.Button(Area_botones, text="Modo Manual", command=ventana_manual, width=17, height=3)
boton_manual.pack(side=tk.TOP, pady=5)

# Botón "Salir"
boton_salir = tk.Button(Area_botones, text="Salir del Programa", command=ventana.quit, width=17, height=3)
boton_salir.pack(side=tk.TOP, pady=5)



ventana.mainloop()





