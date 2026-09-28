import serial
import matplotlib.pyplot as plt

PORT = "COM7"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

plt.ion()

fig, ax = plt.subplots()

x = []
y = []

line, = ax.plot([], [])

ax.set_title("ESP32 Coil Signal")
ax.set_xlabel("Sample")
ax.set_ylabel("ADC Value")
ax.set_ylim(0, 4095)
ax.set_xlim(0, 300)
ax.grid(True)

sample = 0

try:
    while True:

        raw = ser.readline().decode().strip()

        if raw:
            try:
                value = int(raw)

                x.append(sample)
                y.append(value)
                sample += 1

                # Keep only the latest 300 samples
                if len(x) > 300:
                    x.pop(0)
                    y.pop(0)

                line.set_data(x, y)

                ax.set_xlim(max(0, sample - 300), max(300, sample))

                fig.canvas.draw()
                fig.canvas.flush_events()

                plt.pause(0.01)

            except ValueError:
                pass

except KeyboardInterrupt:
    pass

finally:
    ser.close()
    plt.close()