## Version 3 
#OBJETIVO: Se realizara una interfaz simple, en modo automatico, solo tendra 3 botones y cada que se inicie un proceso de se mostrara
#en una ventana diferente y solo por ese tiempo luego se cerrara para continuar
# NOTA 
# 
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from tkinter import Label
from tkinter import Scale
from tkinter import Text
from tkinter import HORIZONTAL
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import time
import os

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
        master.overrideredirect(True)
        self.master.geometry("1366x768")
        self.master.resizable(width=False, height=False)
        # self.serialArduino = serial.Serial("COM12", 115200)  # Reemplaza 'COM1' por el puerto serie correspondiente
        self.serialArduino = serial.Serial("/dev/tty.HC-05", 115200)  # Reemplaza 'COM1' por el puerto serie correspondiente
        master.title("Ventana de Modo Manual Iniciada")
        #Titulo=tk.Label(VenManual,text="Modo Manual")
        # Obtener el ancho y alto de la pantalla
        ancho_pantalla = master.winfo_screenwidth()
        alto_pantalla = master.winfo_screenheight() 

        # Calcular las coordenadas para centrar la ventana
        x = (ancho_pantalla - 1366) // 2  # 900 es el ancho de la ventana
        y = (alto_pantalla - 768) // 2   # 700 es el alto de la ventana

        # Establecer la posición de la ventana
        master.geometry(f"1366x768+{x}+{y}")
        
        self.velocidad = 50

        # Definir el tamaño deseado de la imagen
        width, height = 120, 100

        # Obtener el directorio base del archivo actual
        ruta_base = os.path.dirname(__file__)

        # Construir las rutas relativas a las imágenes
        ruta_imagen_logo_universidad = os.path.join(ruta_base, 'HMI', 'Logo_U.png')
        ruta_imagen_logo_carrera = os.path.join(ruta_base, 'HMI', 'Logo_M.png')

        # Cargar la imagen del logo de la universidad
        imagen_logo_universidad = Image.open(ruta_imagen_logo_universidad)
        imagen_logo_universidad_resized = imagen_logo_universidad.resize((width, height), Image.LANCZOS)
        imagen_logo_universidad_tk = ImageTk.PhotoImage(imagen_logo_universidad_resized)

        # Cargar la imagen del logo de la carrera
        imagen_logo_carrera = Image.open(ruta_imagen_logo_carrera)
        imagen_logo_carrera_resized = imagen_logo_carrera.resize((width, height), Image.LANCZOS)
        imagen_logo_carrera_tk = ImageTk.PhotoImage(imagen_logo_carrera_resized)

        # Crear un frame para contener las imágenes y el texto
        frame_contenedor = tk.Frame(master)
        frame_contenedor.pack(fill='x')

        # Mostrar el logo de la universidad
        label_logo_universidad = tk.Label(frame_contenedor,image=imagen_logo_universidad_tk)
        label_logo_universidad.image = imagen_logo_universidad_tk
        label_logo_universidad.pack(side=tk.LEFT, padx=(20, 0), pady=10, anchor='w')

        # Mostrar el logo de la carrera
        label_logo_carrera = tk.Label(frame_contenedor,image=imagen_logo_carrera_tk)
        label_logo_carrera.image = imagen_logo_carrera_tk
        label_logo_carrera.pack(side=tk.RIGHT, padx=(0, 20), pady=10, anchor='e')

        # Mostrar el texto
        texto = "UNIVERSIDAD DE LAS FUERZAS ARMADAS ESPE-L \n\nSISTEMA DE NAVEGACION AUTONOMA \n\nCONTROL DE MANDO: MANUAL"
        label_texto = tk.Label(frame_contenedor, text=texto, font=("Arial", 14, "bold"))
        label_texto.pack(side=tk.LEFT, expand=True, fill="both", padx=(10, 0), pady=10, anchor='center')

        ####################################################  FRAME TOTAL  #####################################################
        self.Total = tk.Frame(master)
        self.Total.pack(padx=5) 
        ####################################################  SUBFRAME CENTRAL  #####################################################

        #Crear subframe central izquierdo 
        self.centro_izquierdo = tk.Frame(self.Total)
        self.centro_izquierdo.grid(row=0,column=0,padx=20,sticky='nsew')  # Se adhiere a la izquierda, con espacio exterior
        #Crear el subframe 1
        self.Posicion1 = tk.Frame(self.centro_izquierdo)
        self.Posicion1.grid(row=0,column=0,padx=5,sticky='nsew')
        Label(self.Posicion1, text = "CONTROL DE MOVIMIENTO", font=("Arial", 12, "bold") ).grid(row=0, column=0,columnspan=3,pady=10,sticky='w')
        Valto = 1
        Vancho = 5
        #Crear botones para el control de movimiento manual 
        self.boton1 = tk.Button(self.Posicion1,text="⬉", font=("Arial",20,"bold"),width=3)
        self.boton1.grid(row=1,column=0,padx=5,pady=5,sticky='nsew')
        self.boton1.bind("<Button-1>",self.Diagonal_Superior_IZQ)
        self.boton1.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton2 = tk.Button(self.Posicion1,text="⬆",font=("Arial",20,"bold"),width=3)
        self.boton2.grid(row=1,column=1,padx=5,pady=5,sticky='nsew') 
        self.boton2.bind("<Button-1>", self.Adelante)
        self.boton2.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton3 = tk.Button(self.Posicion1,text="⬈", font=("Arial",20,"bold"),width=3)
        self.boton3.grid(row=1,column=2,padx=5,pady=5,sticky='nsew') 
        self.boton3.bind("<Button-1>", self.Diagonal_Superior_DER)
        self.boton3.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton4 = tk.Button(self.Posicion1, text="⬅", font=("Arial",20, "bold"),width=3)
        self.boton4.grid(row=2,column=0,padx=5,pady=5,sticky='nsew')
        self.boton4.bind("<Button-1>", self.Izquierda)
        self.boton4.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton6 = tk.Button(self.Posicion1, text="⮕", font=("Arial",20, "bold"),width=3)
        self.boton6.grid(row=2,column=2,padx=5,pady=5,sticky='nsew')  
        self.boton6.bind("<Button-1>", self.Derecha)
        self.boton6.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton7 = tk.Button(self.Posicion1,text="⬋",font=("Arial",20,"bold"),width=3)
        self.boton7.grid(row=3,column=0,padx=5,pady=5,sticky='nsew')
        self.boton7.bind("<Button-1>",self.Diagonal_Inferior_IZQ)
        self.boton7.bind("<ButtonRelease-1>",self.soltar_boton1)

        self.boton8 = tk.Button(self.Posicion1, text="⬇",font=("Arial",20, "bold"),width=3)
        self.boton8.grid(row=3,column=1,padx=5,pady=5,sticky='nsew') 
        self.boton8.bind("<Button-1>", self.Atras)
        self.boton8.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton9 = tk.Button(self.Posicion1, text="⬊",font=("Arial",20, "bold"),width=3)
        self.boton9.grid(row=3,column=2,padx=5,pady=5,sticky='nsew')  
        self.boton9.bind("<Button-1>",self.Diagonal_Inferior_DER)
        self.boton9.bind("<ButtonRelease-1>",self.soltar_boton1)

        self.boton10 = tk.Button(self.Posicion1, text="⟲",font=("Arial",20, "bold"),width=3)
        self.boton10.grid(row=4,column=0,padx=5,pady=5,sticky='nsew')  
        self.boton10.bind("<Button-1>", self.Giro_Antihorario)
        self.boton10.bind("<ButtonRelease-1>", self.soltar_boton1)

        self.boton11 = tk.Button(self.Posicion1, text="⟳",font=("Arial",20, "bold"),width=3)
        self.boton11.grid(row=4,column=2,padx=5,pady=5,sticky='nsew')  
        self.boton11.bind("<Button-1>", self.Giro_Horario)
        self.boton11.bind("<ButtonRelease-1>", self.soltar_boton1)
        
        #Crear el subframe 2
        self.Posicion2 = tk.Frame(self.centro_izquierdo)
        self.Posicion2.grid(row=1,column=0,padx=5,pady=10,sticky='nsew')
        Label(self.Posicion2, text = "LECTURA DE SENSORES", font=("Arial", 12, "bold") ).grid(row=0,column=0,columnspan=3,pady=10,sticky='w')

        #Crear boton para medir la distancia con los sensores ultrasonicos
        self.boton22 = tk.Button(self.Posicion2, text="MEDIR",font=("Arial", 10, "bold"), width=10,height=Valto, command=self.Leer_Datos)
        self.boton22.grid(row=1,column=0,sticky='w')

        Label(self.Posicion2, text = "ULTRASONICO 1:", font=("Arial",10, "bold")).grid(row=2,column=0,sticky='w')

        # Crear una caja de texto
        self.caja1 = Text(self.Posicion2, wrap=tk.WORD, width=7, height=1, font=("Arial", 12))
        self.caja1.grid(row=2,column=1,pady=10)

        Label(self.Posicion2,text = "ULTRASONICO 2:", font=("Arial", 10, "bold")).grid(row=3,column=0,sticky='w')

        # Crear una caja de texto
        self.caja2 = Text(self.Posicion2, wrap=tk.WORD, width=7, height=1, font=("Arial", 12))
        self.caja2.grid(row=3,column=1,pady=10)

        ############################################################################################################################################
        
        #Crear subframe central centro
        self.centro_centro = tk.Frame(self.Total)
        self.centro_centro.grid(row=0,column=1,sticky='nsew') 
        Label(self.centro_centro, text = "VIDEO EN TIEMPO REAL", font=("Arial", 12, "bold") ).grid(row=0, column=0,columnspan=3,padx=5,pady=10,sticky='w')
        
        #Crear un suframe para mostrar el video de la cámara
        self.Posicion3 = tk.Frame(self.centro_centro)
        self.Posicion3.grid(row=1,column=0,columnspan=4,padx=10,sticky='nsew')

        #Crear el label dentro del subframe donde se mostrara la camra
        self.canvas_camara = tk.Canvas(self.Posicion3,bg="white",relief="flat",width=640,height=400)
        self.canvas_camara.pack(fill="both",expand=True)

        #Crear el frame para los botones de abrir y cerrar la cámara
        self.Posicion4 = tk.Frame(self.centro_centro)
        self.Posicion4.grid(row=2,column=0,pady=10)

        #Aqui se crea el label para seleccionar la camara 
        Label(self.Posicion4, text = "CAMARA:",font=("Arial", 10, "bold") ).grid(row=0,column=0,pady=10,sticky='w')

        #Crear el menu desplegable
        self.camaras = ["NINGUNA","SUPERIOR","INFERIOR"]
        self.valor0 = tk.StringVar()
        self.valor0.set(self.camaras[0]) 
        self.drop=tk.OptionMenu(self.Posicion4,self.valor0,*self.camaras)
        self.drop.config(width=10)
        self.drop.grid(row=0,column=1)
        self.drop['font'] = ('Arial', 10, 'bold')

        # Añadir un botón para abrir y cerrar la cámara en el frame de botones
        self.boton14 = tk.Button(self.Posicion4,text="ABRIR", font=("Arial", 10, "bold"),width=10, height=1, command=self.abrir_camara)
        self.boton14.grid(row=0,column=2,padx=10,sticky='w')

        self.boton15 = tk.Button(self.Posicion4,text="CERRAR", font=("Arial", 10, "bold"),width=10, height=1,command=self.cerrar_camara)
        self.boton15.grid(row=1,column=2,padx=10,sticky='w')

        self.cap = None

        #Label para el control del microservo
        Label(self.Posicion4, text = "CONTROL DEL MICROSERVO",font=("Arial",12,"bold")).grid(row=0,column=3,columnspan=3,padx=20,pady=10,sticky='w')

        #Crear un slider para controlar la rotacion de un microservo
        self.slider = Scale(self.Posicion4,from_=0, to = 90, orient = HORIZONTAL, command = self.angle, length = 300,showvalue=True, tickinterval=10)
        self.slider.grid(row=1,column=3,columnspan=3,padx=20)
        #########################################################################################################################################################

        #Crear subframe central derecho 
        self.centro_derecho = tk.Frame(self.Total)
        self.centro_derecho.grid(row=0,column=2,sticky='nsew') 

        # Crear un frame para el control de la posicion vertical
        self.Posicion6 = tk.Frame(self.centro_derecho)
        self.Posicion6.grid(row=1,column=0,pady=10,sticky='nsew')
        Label(self.Posicion6,text = "CONTROL DE POSICION VERTICAL",font=("Arial", 12, "bold") ).grid(row=0,column=0,columnspan=2,padx=20,sticky='w')

        #Crear un frame para el menu desplegable
        self.Posicion9 = tk.Frame(self.Posicion6)
        self.Posicion9.grid(row=1,column=0,pady=10,sticky='nsew')

        #Crear un label para seleccionar el nivel al que tiene que elevarce 
        label1 = Label(self.Posicion9,text = "SELECCIONE EL NIVEL", font=("Arial",10,"bold"))
        label1.grid(row=0,column=0,columnspan=2,padx=20,sticky='w')
        self.niveles = ["NINGUNA","PISO A1","PISO A2","PISO A3"]
        self.valor = tk.StringVar()
        self.valor.set(self.niveles[0]) 
        self.drop=tk.OptionMenu(self.Posicion9,self.valor,*self.niveles)
        self.drop.config(width=10)
        self.drop.grid(row=1,column=0,columnspan=2)
        self.drop['font'] = ('Arial', 10, 'bold')

        self.Posicion10 = tk.Frame(self.Posicion6)
        self.Posicion10.grid(row=1,column=1,pady=10,sticky='nsew')

        #Crear boton para subir las tijeretas
        self.boton16 = tk.Button(self.Posicion10, text="SUBIR", font=("Arial", 10, "bold"), width=10,height=Valto, command=self.Subir_Tijereta)
        self.boton16.grid(row=0,column=0,padx=10,pady=10)
        self.canvas1= tk.Canvas(self.Posicion10,width=50,height=50) #Crear canvas para el LED 
        self.canvas1.grid(row=0,column=1)
        self.led_subir = self.canvas1.create_oval(10,10,40,40,fill="gray")

        #Crear boton para bajar las tijeretas
        self.boton17 = tk.Button(self.Posicion10, text="BAJAR", font=("Arial", 10, "bold"), width=10, height=Valto, command=self.Bajar_Tijereta)
        self.boton17.grid(row=1,column=0,padx=10,pady=10)
        self.canvas2= tk.Canvas(self.Posicion10,width=50,height=50)
        self.canvas2.grid(row=1,column=1)
        self.led_bajar = self.canvas2.create_oval(10,10,40,40,fill="gray")

        #Crear boton para detener las tijeretas
        self.boton18 = tk.Button(self.Posicion10,text="DETENER", font=("Arial", 10, "bold"), width=10, height=Valto, command=self.Detener_Tijereta)
        self.boton18.grid(row=2,column=0,padx=10,pady=10)
        self.canvas3= tk.Canvas(self.Posicion10, width=50,height=50)
        self.canvas3.grid(row=2,column=1)
        self.led_detener = self.canvas3.create_oval(10,10,40,40,fill="gray")

        #Crear frame para el movimiento lineal de la corredera
        self.Posicion7 = tk.Frame(self.centro_derecho)
        self.Posicion7.grid(row=2,column=0,pady=0,sticky='nsew')
        Label(self.Posicion7,text = "CONTROL DEL SISTEMA LINEAL", font=("Arial", 12, "bold") ).grid(row=0,column=0,columnspan=2,padx=20,sticky='w')

        #Crear boton para hacer avanzar el sistema lineal  
        self.boton19 = tk.Button(self.Posicion7, text="AVANZAR", font=("Arial", 10, "bold"), width=10, height=1, command=self.Subir_Tijereta)
        self.boton19.grid(row=1,column=0,padx=(0,10),pady=10,sticky='e')
        self.canvas4 = tk.Canvas(self.Posicion7,width=50,height=50)
        self.canvas4.grid(row=1,column=1,sticky='w')
        self.led_1 = self.canvas4.create_oval(10,10,40,40,fill="gray")
    
        #Crear boton para hacer detener el sistema lineal  
        self.boton20 = tk.Button(self.Posicion7, text="DETENER", font=("Arial", 10, "bold"), width=10,height=1,command=self.Subir_Tijereta)
        self.boton20.grid(row=3,column=0,padx=(0,10),pady=10,sticky='e')
        self.canvas5= tk.Canvas(self.Posicion7,width=50, height=50)
        self.canvas5.grid(row=3,column=1,sticky='w')
        self.led_2 = self.canvas5.create_oval(10,10,40,40,fill="gray")

        #Crear boton para hacer regresar el sistema de movimiento
        self.boton21 = tk.Button(self.Posicion7,text="REGRESAR", font=("Arial", 10, "bold"), width=10,height=1,command=self.Bajar_Tijereta)
        self.boton21.grid(row=2,column=0,padx=(0,10),pady=10,sticky='e')
        self.canvas6= tk.Canvas(self.Posicion7,width=50,height=50)
        self.canvas6.grid(row=2,column=1,sticky='w')
        self.led_3 = self.canvas6.create_oval(10,10,40,40,fill="gray")

        #Crear el Frame para el control de el electroiman 
        self.Posicion8 = tk.Frame(self.centro_derecho)
        self.Posicion8.grid(row=3,column=0,pady=10,sticky='nsew')
        Label(self.Posicion8,text = "CONTROL DEL ELECTROIMAN", font=("Arial", 12,"bold") ).grid(row=0,column=0,columnspan=2,padx=20,sticky='w')
        
        #Crear boton para encender el electroiman 
        self.boton22 = tk.Button(self.Posicion8, text="ENCENDER", font=("Arial", 10, "bold"), width=10, height=1, command=self.Bajar_Tijereta)
        self.boton22.grid(row=1,column=0,padx=(10,10),pady=10,sticky='e')

        #Crear boton para apagar el electroiman 
        self.boton23 = tk.Button(self.Posicion8, text="APAGAR", font=("Arial", 10, "bold"), width=10, height=1, command=self.Bajar_Tijereta)
        self.boton23.grid(row=2,column=0,padx=(10,10),pady=10,sticky='e')

        #Crear Canvas para el LED para encender
        self.canvas6= tk.Canvas(self.Posicion8, width=50, height=50)
        self.canvas6.grid(row=1,column=1,sticky='w')
        self.led_encender = self.canvas6.create_oval(10,10,40,40, fill="gray")

        #Crear Canvas para el LED para apagar
        self.canvas6= tk.Canvas(self.Posicion8, width=50, height=50)
        self.canvas6.grid(row=2,column=1,sticky='w')
        self.led_encender = self.canvas6.create_oval(10,10,40,40, fill="gray")

        ######################################################################################################3
        #Crear un frame para regresar y salir del modo de manod manual 
        self.Menu_Inferior  = tk.Frame(self.Total)
        self.Menu_Inferior.grid(row=1,column=0,columnspan=3,sticky='ew')

        # Configurar las columnas del Frame para que se expandan
        self.Menu_Inferior.columnconfigure(0, weight=1)
        self.Menu_Inferior.columnconfigure(1, weight=1)
        self.Menu_Inferior.columnconfigure(2, weight=1)

        self.boton12 = tk.Button(self.Menu_Inferior, text="REGRESAR",font=("Arial", 10, "bold"),width=10, height=Valto,command=abrir_ventana_principal_manual)
        self.boton12.grid(row=0,column=0,padx=20,sticky='nw')  # Colocar en la fila 4, columna 0, con espacio exterior
        self.boton12.bind("<ButtonRelease-1>",self.soltar_boton1)

        self.boton13 = tk.Button(self.Menu_Inferior, text="SALIR",font=("Arial", 10, "bold"),width=10,height=Valto,command=VenManual.quit)
        self.boton13.grid(row=0,column=2,padx=20,sticky='ne')  # Colocar en la fila 4, columna 1, con espacio exterior
        self.boton13.bind("<ButtonRelease-1>",self.soltar_boton1)

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
    ############################################################################################################
    def abrir_camara(self):
        if self.valor0.get() == self.camaras[1]:
            self.cap = cv2.VideoCapture(0) #definir el puerto de apertura de la camara superior
        elif self.valor0.get() == self.camaras[2]:
            self.cap = cv2.VideoCapture(1) #definir el puerto de apertura de la camara inferior

        if self.cap is not None and self.cap.isOpened():
            self.update_frame()

    def cerrar_camara(self):
        if self.cap:
            self.cap.release()
            self.cap = None
            self.canvas_camara.delete('all') # Eliminar todos los elementos dibujados en el Canvas

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas_camara.create_image(0,0,anchor=tk.NW,image=imgtk)
                self.canvas_camara.imgtk = imgtk
        
        self.centro_centro.after(10, self.update_frame)

    def close(self):
        self.cerrar_camara()
        self.centro_centro.destroy()
    ###################################################################################################################33
    def Subir_Tijereta(self):
        self.canvas1.itemconfig(self.led_subir, fill="#00FF00")
        self.canvas2.itemconfig(self.led_bajar, fill="gray")
        self.canvas3.itemconfig(self.led_detener, fill="gray")
        self.enviar_datos("SUBIR")

    def Detener_Tijereta(self):
        self.canvas1.itemconfig(self.led_subir, fill="gray")
        self.canvas2.itemconfig(self.led_bajar, fill="gray")
        self.canvas3.itemconfig(self.led_detener, fill="#FFFF00")
        self.enviar_datos("DETENER")

    def Bajar_Tijereta(self):
        self.canvas1.itemconfig(self.led_subir, fill="gray")
        self.canvas2.itemconfig(self.led_bajar, fill="#00FF00")
        self.canvas3.itemconfig(self.led_detener, fill="gray")
        self.enviar_datos("BAJAR")

    def enviar_datos(self, movimiento):
        piso = self.valor.get()
        if piso in self.niveles:
            data = {
                "Modo": "Manual",
                "Dato_movimiento": movimiento,
                "Nivel": piso
            }
            json_data = json.dumps(data)
            self.serialArduino.write(json_data.encode())
            print(json_data)
            pass





    def angle(self, init):
        angleData = str(self.slider.get())
        print(angleData)
        pass

    def Leer_Datos(self):
        data = {
            "Modo" : "Manual",
            "Dato_movimiento": "Leer",
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





