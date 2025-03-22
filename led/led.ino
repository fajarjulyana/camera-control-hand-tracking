const int ledPin = 13;
String inputString = "";

void setup() {
    Serial.begin(9600);
    pinMode(ledPin, OUTPUT);
}

void loop() {
    while (Serial.available()) {
        char inChar = (char)Serial.read();
        inputString += inChar;
        if (inChar == '\n') {
            if (inputString.startsWith("LED:1")) {
                digitalWrite(ledPin, HIGH);
            } else if (inputString.startsWith("LED:0")) {
                digitalWrite(ledPin, LOW);
            }
            inputString = "";
        }
    }
}
