# Electromagnetic Anomaly Detection System

An ESP32-based system that detects abnormal operating conditions in electronic and electromechanical devices by analyzing their electromagnetic signatures.

## How It Works

When a device such as a DC motor operates, it produces electromagnetic radiation. A sensing coil placed near the device detects this electromagnetic activity and generates a small induced electrical signal.

The signal is sampled by the **ESP32's ADC**, which converts it into digital samples. These samples are then processed by a Python program running on a computer.

```text
Device
  ↓
Electromagnetic Field
  ↓
Sensing Coil
  ↓
ESP32 ADC
  ↓
Digital Samples
  ↓
Python Analysis
  ↓
Frequency Comparison
  ↓
Normal / Anomaly
```

## Software

The Python program is menu-driven:

```text
1. Calibrate Device
2. Test Device
3. Exit
```

### Calibration

A known-good device is used to create a baseline.

For our prototype, a properly functioning **DC motor powered by 9V** was used. Its electromagnetic frequency response is measured and stored in a JSON file.

```text
Good Device → ESP32 → Frequency → Save Baseline
```

### Testing

When a device is tested, its current frequency response is measured and compared with the stored baseline.

The frequency difference is calculated as:

```text
Frequency Shift = |Test Frequency - Baseline Frequency|
```

A tolerance threshold is used to prevent small variations caused by noise, distance, or positioning from being incorrectly classified as faults.

```text
If Shift ≤ Threshold → NORMAL

If Shift > Threshold → ANOMALY
```

## Prototype Demonstration

During testing, the DC motor was first calibrated using a **9V supply**.

The same motor was then operated using a **3.7V battery**, producing a significantly different electromagnetic frequency response.

The measured frequency shift exceeded the configured threshold, and the system correctly classified the device as:

```text
ANOMALY DETECTED
```

## Components

- ESP32
- Electromagnetic sensing coil
- DC motor / device under test
- Computer
- Python
- JSON for storing calibration data

## Future Scope

The system can be improved using better signal conditioning, FFT-based spectral analysis, multiple sensing coils, real-time visualization, and machine-learning-based anomaly classification.
