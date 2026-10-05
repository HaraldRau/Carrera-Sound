# motor_sim.py

import numpy as np
import sounddevice as sd
import time

# ------------------------------------------------------------
# Einstellungen
# ------------------------------------------------------------

SAMPLE_RATE = 44100       # Audio-Samplerate
MIN_VOLTAGE = 0.0
MAX_VOLTAGE = 12.0

MIN_RPM = 800             # Motor läuft bei kleiner Spannung bereits etwas
MAX_RPM = 12000

# Grundfrequenz bei 1 Umdrehung
RPM_TO_HZ = 1.0 / 60.0


# ------------------------------------------------------------
# Spannung -> Drehzahl
# ------------------------------------------------------------

def voltage_to_rpm(voltage):
    """Berechnet aus der Spannung eine virtuelle Motordrehzahl."""

    voltage = np.clip(voltage, MIN_VOLTAGE, MAX_VOLTAGE)

    # lineare Kennlinie
    fraction = voltage / MAX_VOLTAGE

    rpm = MIN_RPM + fraction * (MAX_RPM - MIN_RPM)

    # Motor steht bei 0 V
    if voltage <= 0:
        rpm = 0

    return rpm


# ------------------------------------------------------------
# Drehzahl -> Grundfrequenz
# ------------------------------------------------------------

def rpm_to_frequency(rpm):
    """Berechnet die Grundfrequenz aus der Drehzahl."""

    return rpm * RPM_TO_HZ


# ------------------------------------------------------------
# Motorsound erzeugen
# ------------------------------------------------------------

def create_motor_sound(frequency, duration, volume):
    """
    Erzeugt einen einfachen synthetischen Motorsound.

    Der Klang besteht aus Grundton + Harmonischen.
    """

    sample_count = int(SAMPLE_RATE * duration)

    t = np.arange(sample_count) / SAMPLE_RATE

    # Grundton
    signal = np.sin(2 * np.pi * frequency * t)

    # 2. Harmonische
    signal += 0.40 * np.sin(2 * np.pi * frequency * 2 * t)

    # 3. Harmonische
    signal += 0.20 * np.sin(2 * np.pi * frequency * 3 * t)

    # 4. Harmonische
    signal += 0.10 * np.sin(2 * np.pi * frequency * 4 * t)

    # Lautstärke
    signal *= volume

    # Clipping verhindern
    signal = np.clip(signal, -1.0, 1.0)

    return signal.astype(np.float32)


# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------

def main():

    print("Virtueller Rennbahnmotor")
    print("-------------------------")
    print("Spannung 0-12 V eingeben.")
    print("q beendet das Programm.\n")

    while True:

        eingabe = input("Spannung [V]: ")

        if eingabe.lower() == "q":
            break

        try:
            voltage = float(eingabe)
        except ValueError:
            print("Bitte eine Zahl eingeben.")
            continue

        # Spannung -> Drehzahl
        rpm = voltage_to_rpm(voltage)

        # Drehzahl -> Frequenz
        frequency = rpm_to_frequency(rpm)

        # Spannung -> Lautstärke
        volume = voltage / MAX_VOLTAGE

        print(
            f"  Spannung:  {voltage:.1f} V"
            f"\n  Drehzahl:   {rpm:.0f} RPM"
            f"\n  Frequenz:   {frequency:.1f} Hz"
            f"\n  Lautstärke: {volume:.2f}\n"
        )

        # Ton erzeugen
        sound = create_motor_sound(
            frequency,
            duration=1.0,
            volume=volume
        )

        # Abspielen
        sd.play(sound, SAMPLE_RATE)
        sd.wait()


if __name__ == "__main__":
    main()
