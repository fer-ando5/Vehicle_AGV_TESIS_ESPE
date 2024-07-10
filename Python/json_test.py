import serial
import json
import time

# Configura el puerto y la velocidad de baudios (ajusta según sea necesario)
bluetooth_port = '/dev/cu.HC-05'  # Ejemplo para Linux; en Windows podría ser 'COM3'
baud_rate = 115200

# Datos que se enviarán en formato JSON
data = {
    "Modo": "Manual",
    "Dato_movimiento": "Derecha",
    "Dato_velocidad": 5
}

# Crear una cadena JSON
json_data = json.dumps(data) + '\n'  # Agrega un terminador de línea

try:
    # Configura la conexión serial
    bluetooth_serial = serial.Serial(bluetooth_port, baud_rate)

    # Enviar datos en un bucle
    while True:
        print(f"Enviando: {json_data}")
        bluetooth_serial.write(json_data.encode('utf-8'))  # Enviar los datos como bytes
        time.sleep(5)  # Espera 5 segundos antes de enviar el siguiente mensaje

except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")

except KeyboardInterrupt:
    print("Interrumpido por el usuario")

finally:
    if 'bluetooth_serial' in locals() and bluetooth_serial.is_open:
        bluetooth_serial.close()
        print("Puerto serial cerrado")
