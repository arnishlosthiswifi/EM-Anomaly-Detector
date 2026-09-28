#define TX_PIN 25
#define RX_PIN 34

#define TX_FREQ 7000
#define SAMPLE_RATE 20000

void setup() {
  Serial.begin(115200);

  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  // 5 kHz transmitter
  ledcAttach(TX_PIN, TX_FREQ, 8);
  ledcWrite(TX_PIN, 128);
}

void loop() {
  static unsigned long nextSample = 0;

  if ((long)(micros() - nextSample) >= 0) {

    nextSample += 1000000UL / SAMPLE_RATE;

    int signal = analogRead(RX_PIN);

    Serial.println(signal);
  }
}