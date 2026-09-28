import serial
import numpy as np
import matplotlib.pyplot as plt
import time
import json
import os

# ============================================================
# SETTINGS
# ============================================================

PORT = "COM7"
BAUD = 115200

SAMPLE_RATE = 20000
FFT_SIZE = 1024

TEST_DURATION = 4.0

FREQUENCY_TOLERANCE = 300
3
BASELINE_FILE = "baseline.json"

# ============================================================
# SERIAL
# ============================================================

ser = serial.Serial(
    PORT,
    BAUD,
    timeout=1
)

time.sleep(2)

ser.reset_input_buffer()

print("ESP32 connected.")


# ============================================================
# READ SAMPLES
# ============================================================

def get_samples():

    samples = []

    start = time.time()

    while len(samples) < FFT_SIZE:

        if time.time() - start > 2:

            return None

        line = ser.readline()

        if not line:
            continue

        try:

            value = int(
                line.decode().strip()
            )

            samples.append(value)

        except ValueError:

            continue

    return np.array(
        samples,
        dtype=float
    )


# ============================================================
# FFT
# ============================================================

def analyze(samples):

    samples = samples - np.mean(samples)

    window = np.hanning(
        len(samples)
    )

    spectrum = np.abs(
        np.fft.rfft(
            samples * window
        )
    )

    frequencies = np.fft.rfftfreq(
        len(samples),
        1 / SAMPLE_RATE
    )

    spectrum[0] = 0

    peak = np.argmax(
        spectrum
    )

    peak_frequency = frequencies[peak]

    return (
        peak_frequency,
        spectrum[peak],
        frequencies,
        spectrum
    )


# ============================================================
# COLLECT FOR 4 SECONDS
# ============================================================

def collect_measurements():

    frequencies = []
    amplitudes = []

    last_freq_axis = None
    last_spectrum = None

    start = time.time()

    while time.time() - start < TEST_DURATION:

        samples = get_samples()

        if samples is None:
            continue

        freq, amplitude, freq_axis, spectrum = \
            analyze(samples)

        frequencies.append(freq)

        amplitudes.append(amplitude)

        last_freq_axis = freq_axis
        last_spectrum = spectrum

    return (
        np.array(frequencies),
        np.array(amplitudes),
        last_freq_axis,
        last_spectrum
    )


# ============================================================
# CALIBRATION
# ============================================================

def calibrate():

    print()
    print("================================")
    print("       CALIBRATION MODE")
    print("================================")
    print()

    input(
        "Place known-good source and "
        "press ENTER..."
    )

    ser.reset_input_buffer()

    print()
    print("Measuring for 4 seconds...")
    print()

    frequencies, amplitudes, freq_axis, spectrum = \
        collect_measurements()

    if len(frequencies) == 0:

        print("ERROR: No samples received.")

        return

    # Median protects against random spikes
    baseline = np.median(
        frequencies
    )

    variation = np.median(
        np.abs(
            frequencies - baseline
        )
    )

    data = {
        "frequency": float(baseline),
        "variation": float(variation)
    }

    with open(
        BASELINE_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

    print()
    print("================================")
    print("       CALIBRATION DONE")
    print("================================")
    print()

    print(
        f"Reference frequency: "
        f"{baseline:.1f} Hz"
    )

    print(
        f"Typical variation: "
        f"{variation:.1f} Hz"
    )

    show_graph(
        freq_axis,
        spectrum,
        baseline,
        "VERIFIED NORMAL"
    )


# ============================================================
# TEST
# ============================================================

def test_device():

    if not os.path.exists(
        BASELINE_FILE
    ):

        print(
            "Calibrate first!"
        )

        return

    with open(
        BASELINE_FILE,
        "r"
    ) as f:

        baseline_data = json.load(f)

    reference = baseline_data[
        "frequency"
    ]

    print()
    print("================================")
    print("          TEST MODE")
    print("================================")
    print()

    print(
        f"Reference frequency: "
        f"{reference:.1f} Hz"
    )

    input(
        "Place device and "
        "press ENTER..."
    )

    ser.reset_input_buffer()

    print()
    print("Testing for 4 seconds...")
    print()

    frequencies, amplitudes, freq_axis, spectrum = \
        collect_measurements()

    if len(frequencies) == 0:

        print(
            "ERROR: No data received."
        )

        return

    # Median frequency
    measured = np.median(
        frequencies
    )

    # How many FFT windows agree?
    differences = np.abs(
        frequencies - reference
    )

    matching = (
        differences <=
        FREQUENCY_TOLERANCE
    )

    consistency = np.mean(
        matching
    )

    deviation = (
        measured - reference
    )

    # --------------------------------
    # DECISION
    # --------------------------------

    if consistency >= 0.60:

        status = "DEVICE OKAY"

    else:

        status = "ANOMALY"

    print()
    print("================================")
    print("             RESULT")
    print("================================")
    print()

    print(
        f"STATUS      : {status}"
    )

    print(
        f"REFERENCE   : "
        f"{reference:.1f} Hz"
    )

    print(
        f"DETECTED    : "
        f"{measured:.1f} Hz"
    )

    print(
        f"DEVIATION   : "
        f"{deviation:+.1f} Hz"
    )

    print(
        f"CONSISTENCY : "
        f"{consistency * 100:.1f}%"
    )

    print(
        f"WINDOWS     : "
        f"{len(frequencies)}"
    )

    print()

    show_graph(
        freq_axis,
        spectrum,
        reference,
        status
    )


# ============================================================
# GRAPH
# ============================================================

def show_graph(
    freq_axis,
    spectrum,
    reference,
    title
):

    plt.figure(
        figsize=(11, 6)
    )

    plt.plot(
        freq_axis,
        spectrum
    )

    plt.axvline(
        reference,
        linestyle="--",
        label=
        f"Reference: {reference:.1f} Hz"
    )

    plt.axvspan(
        reference -
        FREQUENCY_TOLERANCE,

        reference +
        FREQUENCY_TOLERANCE,

        alpha=0.15,

        label="Allowed range"
    )

    plt.xlabel(
        "Frequency (Hz)"
    )

    plt.ylabel(
        "Magnitude"
    )

    plt.title(
        title
    )

    plt.xlim(
        0,
        SAMPLE_RATE / 2
    )

    plt.grid()

    plt.legend()

    plt.tight_layout()

    plt.show()


# ============================================================
# MENU
# ============================================================

while True:

    print()
    print("================================")
    print("       EM DIAGNOSTIC SYSTEM")
    print("================================")
    print()
    print("1. Calibrate")
    print("2. Test device")
    print("3. Exit")
    print()

    choice = input(
        "Select: "
    )

    if choice == "1":

        calibrate()

    elif choice == "2":

        test_device()

    elif choice == "3":

        break

    else:

        print(
            "Invalid option."
        )