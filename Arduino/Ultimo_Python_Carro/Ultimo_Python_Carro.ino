#include <ArduinoJson.h>

StaticJsonDocument<200> doc;

//SoftwareSerial BTSerial(19, 18);

int M1_Dir = 53;
int M1_Vel = 2;

int M2_Dir = 51;
int M2_Vel = 3;

int M3_Dir = 49;
int M3_Vel = 4;

int M4_Dir = 47;
int M4_Vel = 5;

String mensaje, m1_vel, m2_vel, m3_vel, m4_vel;
String Dato_movimiento, Dato_velocidad;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  //BTSerial.begin(115200);

  pinMode(M1_Dir, OUTPUT);
  pinMode(M1_Vel, OUTPUT);

  pinMode(M2_Dir, OUTPUT);
  pinMode(M2_Vel, OUTPUT);

  pinMode(M3_Dir, OUTPUT);
  pinMode(M3_Vel, OUTPUT);

  pinMode(M4_Dir, OUTPUT);
  pinMode(M4_Vel, OUTPUT);

} 

void loop() {

  if (Serial.available()) { // Si hay datos disponibles en el puerto serie del Arduino IDE
    //mensaje = Serial.readString();  // Leer la velocidad de giro enviada desde Python
   // Serial.println(mensaje);

    deserializeJson(doc, Serial);

    String Modo = doc["Modo"];
    
    /*
    int pos = mensaje.indexOf(',');
    int pos1 = mensaje.indexOf(',', pos + 1); // Buscar la segunda coma
    int pos2 = mensaje.indexOf(',', pos1 + 1); // Buscar la tercera coma
    int pos3 = mensaje.indexOf(',', pos2 + 1); // Buscar la cuarta coma
    int pos4 = mensaje.indexOf(',', pos3 + 1); // Buscar la quinta coma

    m1_vel = mensaje.substring(0, pos);
    m2_vel = mensaje.substring(pos + 1, pos1); // Extraer la subcadena entre la primera y segunda coma
    m3_vel = mensaje.substring(pos1 + 1, pos2); // Extraer la subcadena entre la segunda y tercera coma
    m4_vel = mensaje.substring(pos2 + 1, pos3); // Extraer la subcadena entre la tercera y cuarta coma
    Dato_movimiento = mensaje.substring(pos3 + 1, pos4); // Extraer la subcadena entre la cuarta y quinta coma
    Dato_velocidad = mensaje.substring(pos4 + 1); // La subcadena restante es para la velocidad

    int vel_m1 = m1_vel.toInt();
    int vel_m2 = m2_vel.toInt();
    int vel_m3 = m3_vel.toInt();
    int vel_m4 = m4_vel.toInt();
    int Valor_velocidad = Dato_velocidad.toInt();
    */

    if (Modo == "Auto"){

      int vel_m1 = doc["m1_vel"];
      int vel_m2 = doc["m2_vel"];
      int vel_m3 = doc["m3_vel"];
      int vel_m4 = doc["m4_vel"];

    // Controlar la velocidad del motor utilizando la señal PWM
      if (vel_m1 > 0) {
        Serial.println("Positivo M1");
        digitalWrite(M1_Dir, LOW);
        analogWrite(M1_Vel, vel_m1);
      }
      
      if (vel_m1 <= 0) {
        int Nvel_m1 = abs(vel_m1);
        Serial.println("Negativo M1");
        digitalWrite(M1_Dir, HIGH);
        analogWrite(M1_Vel, Nvel_m1);
      }

      if (vel_m2 > 0) {
        Serial.println("Positivo M2");
        digitalWrite(M2_Dir, LOW);
        analogWrite(M2_Vel, vel_m2);
      }
      
      if (vel_m2 <= 0) {
        int Nvel_m2 = abs(vel_m2);
        Serial.println("Negativo M2");
        digitalWrite(M2_Dir, HIGH);
        analogWrite(M2_Vel, Nvel_m2);
      }

      if (vel_m3 > 0) {
        Serial.println("Positivo M3");
        digitalWrite(M3_Dir, LOW);
        analogWrite(M3_Vel, vel_m3);
      }
      
      if (vel_m3 <= 0) {
        int Nvel_m3 = abs(vel_m3);
        Serial.println("Negativo M3");
        digitalWrite(M3_Dir, HIGH);
        analogWrite(M3_Vel, Nvel_m3);
      }

      if (vel_m4 > 0) {
        Serial.println("Positivo M4");
        digitalWrite(M4_Dir, LOW);
        analogWrite(M4_Vel, vel_m4);
      }
      
      if (vel_m4 <= 0) {
        int Nvel_m4 = abs(vel_m4);
        Serial.println("Negativo M4");
        digitalWrite(M4_Dir, HIGH);
        analogWrite(M4_Vel, Nvel_m4);
      }
    }

    if (Modo == "Manual"){

      String Dato_movimiento = doc["Dato_movimiento"];
      int Valor_velocidad = doc["Dato_velocidad"];

      //nuevo giro horario
      if (Dato_movimiento == "Giro_Horario"){
        digitalWrite(M1_Dir, LOW);
        analogWrite(M1_Vel, Valor_velocidad);

        digitalWrite(M2_Dir, LOW);
        analogWrite(M2_Vel, Valor_velocidad);
        
        digitalWrite(M3_Dir, LOW);
        analogWrite(M3_Vel, Valor_velocidad);
        
        digitalWrite(M4_Dir, LOW);
        analogWrite(M4_Vel, Valor_velocidad);
      }

      //nuevo giro antihorario
      if (Dato_movimiento == "Giro_Antihorario"){
        digitalWrite(M1_Dir, HIGH);
        analogWrite(M1_Vel, Valor_velocidad);

        digitalWrite(M2_Dir, HIGH);
        analogWrite(M2_Vel, Valor_velocidad);
        
        digitalWrite(M3_Dir, HIGH);
        analogWrite(M3_Vel, Valor_velocidad);
        
        digitalWrite(M4_Dir, HIGH);
        analogWrite(M4_Vel, Valor_velocidad);
      }

      //Nuevoo movimiento hacia adelante
      if (Dato_movimiento == "Adelante"){
        digitalWrite(M1_Dir, LOW);
        analogWrite(M1_Vel, Valor_velocidad);

        digitalWrite(M2_Dir, HIGH);
        analogWrite(M2_Vel, Valor_velocidad);
        
        digitalWrite(M3_Dir, LOW);
        analogWrite(M3_Vel, Valor_velocidad);
        
        digitalWrite(M4_Dir, HIGH);
        analogWrite(M4_Vel, Valor_velocidad);
      }

      //Nuevo movimiento hacia atras
      if (Dato_movimiento == "Atras"){
        digitalWrite(M1_Dir, HIGH);
        analogWrite(M1_Vel, Valor_velocidad);

        digitalWrite(M2_Dir, LOW);
        analogWrite(M2_Vel, Valor_velocidad);
        
        digitalWrite(M3_Dir, HIGH);
        analogWrite(M3_Vel, Valor_velocidad);
        
        digitalWrite(M4_Dir, LOW);
        analogWrite(M4_Vel, Valor_velocidad);
      }

      //Nuevo movimiento hacia la derecha
      if (Dato_movimiento == "Derecha"){
        digitalWrite(M1_Dir, LOW);
        analogWrite(M1_Vel, Valor_velocidad);

        digitalWrite(M2_Dir, LOW);
        analogWrite(M2_Vel, Valor_velocidad);
        
        digitalWrite(M3_Dir, HIGH);
        analogWrite(M3_Vel, Valor_velocidad);
        
        digitalWrite(M4_Dir, HIGH);
        analogWrite(M4_Vel, Valor_velocidad);

      }

      //Nuevo movimiento hacia la izquierda
      if (Dato_movimiento == "Izquierda"){
        digitalWrite(M1_Dir, HIGH);
        analogWrite(M1_Vel, Valor_velocidad);

        digitalWrite(M2_Dir, HIGH);
        analogWrite(M2_Vel, Valor_velocidad);
        
        digitalWrite(M3_Dir, LOW);
        analogWrite(M3_Vel, Valor_velocidad);
        
        digitalWrite(M4_Dir, LOW);
        analogWrite(M4_Vel, Valor_velocidad);

      }

      //Nuevo movimiento diagonal inferior derecha
      if (Dato_movimiento == "Diagonal_Superior_IZQ"){
        digitalWrite(M1_Dir, HIGH);
        analogWrite(M1_Vel, 0);

        digitalWrite(M2_Dir, HIGH);
        analogWrite(M2_Vel, Valor_velocidad);
        
        digitalWrite(M3_Dir, LOW);
        analogWrite(M3_Vel, Valor_velocidad);
        
        digitalWrite(M4_Dir, LOW);
        analogWrite(M4_Vel, 0);
      }

      //Nuevo movimiento diagonal superior derecha
      if (Dato_movimiento == "Diagonal_Superior_DER"){
        digitalWrite(M1_Dir, LOW);
        analogWrite(M1_Vel, Valor_velocidad);

        digitalWrite(M2_Dir, LOW);
        analogWrite(M2_Vel, 0);
        
        digitalWrite(M3_Dir, HIGH);
        analogWrite(M3_Vel, 0);
        
        digitalWrite(M4_Dir, HIGH);
        analogWrite(M4_Vel, Valor_velocidad);
      }

      //Nuevo movimiento diagonal inferior derecha
      if (Dato_movimiento == "Diagonal_Inferior_IZQ"){
        digitalWrite(M1_Dir, HIGH);
        analogWrite(M1_Vel, Valor_velocidad);

        digitalWrite(M2_Dir, HIGH);
        analogWrite(M2_Vel, 0);
        
        digitalWrite(M3_Dir, LOW);
        analogWrite(M3_Vel, 0);
        
        digitalWrite(M4_Dir, LOW);
        analogWrite(M4_Vel, Valor_velocidad);
      }

      //Nuevo movimiento diagonal superior izquierda
      if (Dato_movimiento == "Diagonal_Inferior_DER"){
        digitalWrite(M1_Dir, LOW);
        analogWrite(M1_Vel, 0);

        digitalWrite(M2_Dir, LOW);
        analogWrite(M2_Vel, Valor_velocidad);
        
        digitalWrite(M3_Dir, HIGH);
        analogWrite(M3_Vel, Valor_velocidad);
        
        digitalWrite(M4_Dir, HIGH);
        analogWrite(M4_Vel, 0);
      }
    }

    if (Modo == "Quieto"){
      digitalWrite(M1_Dir, LOW);
      analogWrite(M1_Vel, 0);

      digitalWrite(M2_Dir, LOW);
      analogWrite(M2_Vel, 0);
      
      digitalWrite(M3_Dir, HIGH);
      analogWrite(M3_Vel, 0);
      
      digitalWrite(M4_Dir, HIGH);
      analogWrite(M4_Vel, 0);

    }

  }

}