#include <SabertoothSimplified.h>
#include <SoftwareSerial.h>
#include <Servo.h>

Servo myservo;
SabertoothSimplified ST;
SoftwareSerial mySerial(10, 11); // RX, TX

String tmp_line;

int delIdx; // delimiter position

int motorSpeed;
int steering;

const int maxSpeed=40;

                                        
void setup()
{
  mySerial.begin(9600);
  SabertoothTXPinSerial.begin(9600);
  
  motorSpeed = 0;
  steering = 0;
  
  myservo.attach(9);
}


void setMotorSpeed(int mspeed1, int mspeed2){
  mySerial.println("setting motor speed");
  ST.motor(2, mspeed2);
  ST.motor(1, mspeed1);
  mySerial.println(mspeed1*10);
}

/*void setSteering(int steering){
  mySerial.println("setting steering");
  myservo.write(90 +(steering*20));
  mySerial.println(90 +(steering*20));
}
*/

void processLine(String tmp){
  delIdx = tmp_line.indexOf(',');
    mySerial.println("splitting");
    if(delIdx != -1){
      motorSpeed = tmp_line.substring(0,delIdx).toInt();
      mySerial.println(tmp_line.substring(0,delIdx));
      steering = tmp_line.substring(delIdx+1,tmp_line.length()).toInt();
      
      motorSpeed *= -1;
      setMotorSpeed((maxSpeed*motorSpeed)-(8*steering), (maxSpeed*motorSpeed)+(8*steering));
      // neg to the right
      // pos to the left
      
      mySerial.println("set motor speed");
    }
}

void loop()
{
  if (mySerial.available()){
    //char c = mySerial.read();
    tmp_line = mySerial.readStringUntil('\n');
    processLine(tmp_line);
    mySerial.println("processed line");
  }
}
