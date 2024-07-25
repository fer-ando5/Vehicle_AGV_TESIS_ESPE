from QR_Lector import QRLector
import time

def esperar_deteccion_codigo_qr():
    # Crear una instancia de la clase QRLector con la IP del servidor MQTT
    lector = QRLector()
    
    # while True:
    print("Esperando detección de código QR...")
    datos_mensaje = lector.procesar_codigo_qr()
    print("Datos del mensaje:", datos_mensaje)
        
      

# Ejecutar la función principal si se ejecuta el script
if __name__ == "__main__":
    esperar_deteccion_codigo_qr()


