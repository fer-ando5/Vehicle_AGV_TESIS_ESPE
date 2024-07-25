import os
import paho.mqtt.client as mqtt
import time

class Funciones_Complementarias:
    def __init__(self, mqtt_server, mqtt_port):
        self.mqtt_server = mqtt_server
        self.mqtt_port = mqtt_port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.last_message = {}

    def on_connect(self, client, userdata, flags, rc):
        print(f"Conectado al servidor MQTT con código de resultado: {rc}")
        if rc == 0:
            # Suscribir al tópico necesario
            self.client.subscribe("/Caja/presencia1")
            self.client.subscribe("/sensores/presencia1")
            self.client.subscribe("/sensores/presencia2")
            self.client.subscribe("/sensores/presencia3")
        else:
            print(f"Error al conectar: {rc}")

    def on_message(self, client, userdata, msg):
        print(f'Recibido mensaje en tópico: {msg.topic} | Estado: {msg.payload.decode()}')
        self.last_message[msg.topic] = msg.payload.decode()

    def get_status(self, topic):
        return self.last_message.get(topic, "Sin datos")

    def start(self):
        self.client.connect(self.mqtt_server, self.mqtt_port, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish_message(self, topic, message):
        self.client.connect(self.mqtt_server, self.mqtt_port, 60)
        self.client.publish(topic, message)
        self.client.disconnect()

    def Validacion_Caja_Mesa(self):
        self.start()
        # Esperar a que se reciba el mensaje
        try:
            while "/Caja/presencia1" not in self.last_message:
                pass  # Esperar hasta que se reciba el mensaje
        except KeyboardInterrupt:
            print("\nSaliendo...")
        finally:
            estado_caja1 = self.get_status("/Caja/presencia1")
            self.stop()
            return estado_caja1

    def Validacion_Repisas(self):
        self.start()
        estados = []
        try:
            # Esperar hasta que se reciban los mensajes de todos los sensores
            sensores = ["/sensores/presencia1", "/sensores/presencia2", "/sensores/presencia3"]
            while not all(sensor in self.last_message for sensor in sensores):
                print(f"Esperando mensajes: {self.last_message}")  # Depuración
                time.sleep(0.1)  # Esperar un corto período para evitar uso excesivo de CPU

            # Obtener el estado de cada sensor
            for sensor in sensores:
                estado = self.get_status(sensor)
                print(f"Mensaje recibido en tópico {sensor}: {estado}")  # Depuración
                # Convertir el estado a entero si es necesario
                try:
                    estado = int(estado)
                except ValueError:
                    print(f"Error al convertir el estado del sensor {sensor} a entero")
                    estado = -1  # Valor de error
                estados.append(estado)
                disponibilidad = 'Disponible' if estado == 0 else 'No disponible'
                print(f"Estado del sensor {sensor}: {disponibilidad}")
        except KeyboardInterrupt:
            print("\nSaliendo...")
        finally:
            self.stop()
            return estados


    def Validar_Casilleros_Disponibles(self):
        estados = self.Validacion_Repisas()

        # Convertir los estados a enteros, si aún no lo son
        estados = [int(estado) for estado in estados]
        
        # Imprimir los estados de los sensores
        print(f"Estados de los sensores: {estados}")

        # Verifica si hay algún casillero disponible
        casilleros_disponibles = [i + 1 for i, estado in enumerate(estados) if estado == 0]  # Estado 0 indica disponible

        print(f"Casilleros disponibles: {casilleros_disponibles}")

        if not casilleros_disponibles:
            print("ERROR SIN DISPOSICION DE CASILLEROS")
            return 0  # Retorna 0 si no hay casilleros disponibles

        # Retorna el casillero más cercano disponible
        casillero_mas_cercano = min(casilleros_disponibles)
        return casillero_mas_cercano



