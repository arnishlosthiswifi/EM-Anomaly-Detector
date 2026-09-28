import serial
import matplotlib.pyplot as plt
from collections import deque

PORT = "COM7"
BAUD = 115200
SAMPLES = 500

ser = serial.Serial(PORT, BAUD, timeout=1)

data = deque([1875] * SAMPLES, maxlen=SAMPLES)

plt.ion()

fig, ax = plt.subplots()
line, = ax.plot(data)

ax.set_title("ESP32 Coil Signal")
ax.set_xlabel("Sample")
ax.set_ylabel("ADC Value")
ax.set_ylim(1000, 2750)
ax.grid(True)

BASELINE = 1875
GAIN = 20

while True:
    try:
        value = int(ser.readline().decode().strip())

        # Amplify only the deviation from the baseline
        display_value = BASELINE + (value - BASELINE) * GAIN

        data.append(display_value)

        line.set_ydata(data)
        line.set_xdata(range(len(data)))

        ax.set_xlim(0, SAMPLES)

        plt.pause(0.001)

    except ValueError:
        pass

    except KeyboardInterrupt:
        break

ser.close()
plt.close()