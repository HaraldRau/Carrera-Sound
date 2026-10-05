# motor_sim.py

import numpy as np
import sounddevice as sd

# ------------------------------------------------------------
# Einstellungen
# ------------------------------------------------------------

SAMPLE_RATE = 44100       # Audio-Samplerate

MIN_VOLTAGE = 0.0
MAX_VOLTAGE = 12.0

MIN_RPM = 750              # Standgas bei 0 V
MAX_RPM = 12000

# Ein 4-Takt-V8 hat 4 Zündereignisse pro
# Kurbelwellenumdrehung.
#
# 750 RPM:
# 750 / 60 = 12,5 Umdrehungen/s
# 12,5 * 4 = 50 Zündereignisse/s
#
# Deshalb entspricht 750 RPM einem Grundton von 50 Hz.
ZÜNDUNGEN_PRO_UMDREHUNG = 4
RPM_TO_HZ = ZÜNDUNGEN_PRO_UMDREHUNG / 60.0


# ------------------------------------------------------------
# Spannung -> Drehzahl
# ------------------------------------------------------------

def voltage_to_rpm(voltage):
    """Berechnet aus der Spannung die virtuelle Motordrehzahl."""

    voltage = np.clip(voltage, MIN_VOLTAGE, MAX_VOLTAGE)

    # Lineare Kennlinie
    fraction = voltage / MAX_VOLTAGE

    rpm = MIN_RPM + fraction * (MAX_RPM - MIN_RPM)

    return rpm


# ------------------------------------------------------------
# Drehzahl -> Grundfrequenz
# ------------------------------------------------------------

def rpm_to_frequency(rpm):
    """Berechnet die V8-Grundfrequenz aus der Drehzahl."""

    return rpm * RPM_TO_HZ


# ------------------------------------------------------------
# Lautstärke
# ------------------------------------------------------------

def voltage_to_volume(voltage):
    """
    Berechnet die Lautstärke.

    Bei 0 V bleibt der Motor bereits gut hörbar.
    Die Lautstärke steigt mit der Drehzahl nur moderat an.
    """

    voltage = np.clip(voltage, MIN_VOLTAGE, MAX_VOLTAGE)

    fraction = voltage / MAX_VOLTAGE

    # Grundlautstärke im Standgas
    idle_volume = 0.22

    # Zusätzliche Lautstärke bei steigender Drehzahl
    max_additional_volume = 0.38

    # Quadratwurzel sorgt für eine flachere Kennlinie.
    volume = idle_volume + max_additional_volume * np.sqrt(fraction)

    return volume


# ------------------------------------------------------------
# Motorsound erzeugen
# ------------------------------------------------------------

def create_motor_sound(frequency, duration, volume):
    """
    Erzeugt einen einfachen synthetischen V8-Motorsound.

    Grundton + mehrere Harmonische.
    """

    sample_count = int(SAMPLE_RATE * duration)

    t = np.arange(sample_count) / SAMPLE_RATE

    # Grundton
    signal = np.sin(2 * np.pi * frequency * t)

    # 2. Harmonische
    signal += 0.45 * np.sin(2 * np.pi * frequency * 2 * t)

    # 3. Harmonische
    signal += 0.25 * np.sin(2 * np.pi * frequency * 3 * t)

    # 4. Harmonische
    signal += 0.12 * np.sin(2 * np.pi * frequency * 4 * t)

    # 5. Harmonische – etwas Charakter
    signal += 0.06 * np.sin(2 * np.pi * frequency * 5 * t)

    # Lautstärke
    signal *= volume

    # Clipping verhindern
    signal = np.clip(signal, -1.0, 1.0)

    return signal.astype(np.float32)


# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------

def main():

    print("Virtueller Porsche-V8")
    print("----------------------")
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
        volume = voltage_to_volume(voltage)

        print(
            f"  Spannung:  {voltage:.1f} V"
            f"\n  Drehzahl:  {rpm:.0f} RPM"
            f"\n  Frequenz:  {frequency:.1f} Hz"
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
```
