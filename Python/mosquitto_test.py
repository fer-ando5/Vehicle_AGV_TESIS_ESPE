import paho.mqtt.client as mqtt
import time

# Función de callback que se ejecuta cuando se recibe un mensaje
def on_message(client, userdata, msg):
    print(f'Recibido mensaje en tópico: {msg.topic} | Estado: {msg.payload.decode()}')

# Función para obtener el estado actual de un sensor específico desde el broker MQTT
def get_status(client, topic):
    # Solicitar el estado actual del sensor al broker
    client.subscribe(topic, qos=1)  # Suscripción con QoS 1 para asegurar la entrega1
    time.sleep(1)  # Esperar un momento para recibir el mensaje (puedes ajustar este tiempo)

# Configuración del cliente MQTT
mqtt_server = "192.168.65.34"
mqtt_port = 1883

client = mqtt.Client()
client.on_message = on_message

# Conectar al broker MQTT
client.connect(mqtt_server, mqtt_port, 60)

# Iniciar el bucle de recepción
client.loop_start()

try:
    while True:
        # Capturar entrada del usuario desde el teclado
        sensor_num = input()
        
        if sensor_num == 'q':
            break
        
        if sensor_num in ['1', '2', '3']:
            sensor_topic = f"/sensores/presencia{sensor_num}"
            get_status(client, sensor_topic)
        else:
            print("Entrada inválida. Por favor, presiona 1, 2, o 3.")

except KeyboardInterrupt:
    print("\nSaliendo...")

# Detener el bucle y desconectar
client.loop_stop()
client.disconnect()
