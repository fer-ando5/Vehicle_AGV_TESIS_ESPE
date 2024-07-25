import os
import paho.mqtt.client as mqtt

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
            # Suscribir a los tópicos necesarios
            self.client.subscribe("/sensores/presencia1")
            self.client.subscribe("/sensores/presencia2")
            self.client.subscribe("/sensores/presencia3")
            self.client.subscribe("/Caja/presencia1")
        else:
            print(f"Error al conectar: {rc}")

    def on_message(self, client, userdata, msg):
        print(f'Recibido mensaje en tópico: {msg.topic} | Estado: {msg.payload.decode()}')
        self.last_message[msg.topic] = msg.payload.decode()

    def get_status(self, topic):
        return self.last_message.get(topic, "Sin datos")

    def publish_message(self, topic, message):
        result = self.client.publish(topic, message, qos=1)
        status = result.rc
        if status == 0:
            print(f"Mensaje `{message}` enviado a tópico `{topic}`")
        else:
            print(f"Error al enviar mensaje a tópico `{topic}`: {status}")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def start_monitoring(self):
        self.client.connect(self.mqtt_server, self.mqtt_port, 60)
        self.client.loop_start()

        try:
            while True:
                self.clear_screen()

                estado_sensor1 = self.get_status("/sensores/presencia1")
                estado_sensor2 = self.get_status("/sensores/presencia2")
                estado_sensor3 = self.get_status("/sensores/presencia3")
                estado_caja1 = self.get_status("/Caja/presencia1")

                print(f"Estado sensor 1: {estado_sensor1}")
                print(f"Estado sensor 2: {estado_sensor2}")
                print(f"Estado sensor 3: {estado_sensor3}")
                print(f"Estado caja 1: {estado_caja1}")

                # Esperar entrada del usuario para el mensaje
                mensaje = input("Introduce el mensaje para publicar y presiona Enter: ")

                # Publicar datos ingresados por el usuario
                self.publish_message("/robot/estado", mensaje)

        except KeyboardInterrupt:
            print("\nSaliendo...")

        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    # Configuración del servidor MQTT
    mqtt_server = "192.168.11.34"
    mqtt_port = 1883

    # Iniciar el monitoreo de sensores
    monitor = Funciones_Complementarias(mqtt_server, mqtt_port)
    monitor.start_monitoring()
