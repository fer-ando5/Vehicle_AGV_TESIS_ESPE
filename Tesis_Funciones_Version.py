import logging
import time
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import paho.mqtt.client as mqtt


#Parte de codigo arucos 
import cv2 as cv
import cv2.aruco as aruco
import numpy as np
import serial
import math
from PIL import Image, ImageTk
import requests

#logeos para thingsboard
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


##borar libreria randon luego 
import random
##########################################  Variables #########################################

##########################################  Camara IP #########################################

CamaraIP = "http://192.168.0.85/640x480.jpg"

##########################################  Funciones  ########################################


class Funciones_Complementarias:
    
    def __init__(self):
        self.mqtt_broker = "10.52.172.0"  # Cambiar a la dirección IP de la laptop Lenovo
        self.mqtt_port = 1883 #puerto de envio de datos para Mqtt
        self.mqtt_topic = "v1/devices/me/telemetry"  
        ############### TOKEN DE MESA 1 (84)###############
        self.token_mesa1= "HAQDuCCiSr1dpXiTmtzX"

        ############### TOKEN ROBOT (83)###############
        self.token_robot= "NNz7OFhy2WnVm6eDB56x"

        ############### TOKEN ROBOT (82)###############
        self.token_plataforma= "NNz7OFhy2WnVm6eDB56x"
        self.valoranteriorcajamesa1 = 3
        self.cajavalormesa1 = 4
        self.errorescajamesa1=1
        self.token_referencia = None
        self.client = None
        self.contador = 1
        

    def on_attributes_change(self, result, exception=None):
        if exception is not None:
            print("Error al recibir atributos de ThingsBoard:", exception)
            self.errorescajamesa1 = 1
        
        else:
            logging.info(result)
            self.cajavalormesa1 = result.get('client', {}).get('Caja', None)
            if self.cajavalormesa1 is not None:
                print("Valor de cajavalor:", self.cajavalormesa1)
                self.errorescajamesa1 = 0
                self.contador = 1


    def Pedir_atributos_caja(self, token_referencia):
       
        client = TBDeviceMqttClient("10.52.172.0", username=token_referencia)
        client.connect()
        client.request_attributes(["Caja", "ledState"], callback=self.on_attributes_change)
        time.sleep(2)
        self.enviarcaja = self.cajavalormesa1
        if self.errorescajamesa1 == 0:
            client.disconnect()
            client.stop()



    def Validaion_Caja_Mesa(self):
        print("??????????????? INICIA Proceso ???????????????")
        while self.errorescajamesa1 == 1:
            
            time.sleep(self.contador)
            self.contador = 1 + self.contador
            print("Tiempo de pausa actual: ",self.contador)
            self.Pedir_atributos_caja(self.token_mesa1)
        print("Proceso completado.")
        self.errorescajamesa1 = self.seterror1()
        self.enviarcaja = self.cajavalormesa1
        print("??????????????? FIN Proceso ???????????????")
        return self.enviarcaja


    def seterror1(self):
        print("Seteamos el error con exito")
        self.errorescajamesa1=1

    
    def Enviar_atributos(self, token_referencia, Nombre_del_atributo, dato_atributo):
        
        try: 
            client = mqtt.Client()

            if token_referencia == "Mesa":
                token_referencia = self.token_mesa1
                
            elif token_referencia == "Robot":
                token_referencia = self.token_robot

            elif token_referencia == "Plataforma":
                token_referencia = self.token_plataforma

            client.username_pw_set(token_referencia)
            client.connect(self.mqtt_broker, self.mqtt_port, 55)
            payload = '{"' + Nombre_del_atributo + '": "' + str(dato_atributo) + '"}'
            client.publish(self.mqtt_topic, payload, qos=1)
            time.sleep(1)  # Agrega un retraso de 1 segundo antes de desconectar el cliente
            client.disconnect()
            print("Datos enviados a ThingsBoard correctamente.")
        except Exception as e:
            print("Error al enviar datos a ThingsBoard:", e)



        '''
        try:
            attributes = {Nombre_del_atributo: dato_atributo}
            print("Nombre del atributo y atributo enviado:",attributes)
            result = self.client.send_attributes(attributes)
            result.get()  # Espera a que se complete el envío de atributos

            if result.rc() == TBPublishInfo.TB_ERR_SUCCESS:
                print("Los atributos se enviaron correctamente a ThingsBoard.")
                self.client.disconnect()
            else:
                print("No se pudieron enviar los atributos a ThingsBoard.")
        except Exception as e:
            print("Error al enviar atributos a ThingsBoard:", e)
        '''