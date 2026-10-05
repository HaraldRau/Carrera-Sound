# motor_v8.py

import numpy as np
import sounddevice as sd

# ------------------------------------------------------------
# Einstellungen
# ------------------------------------------------------------

SAMPLE_RATE = 44100

RPM = 750

# 4 Zündereignisse pro Kurbelwellenumdrehung
IGNITIONS_PER_REV = 4

# 750 RPM -> 50 Zündimpulse/s
IGNITION_FREQUENCY = RPM / 60.0 * IGNITIONS_PER_REV

DURATION = 3.0

VOLUME = 0.45


# ------------------------------------------------------------
# V8-Zündimpuls
# ------------------------------------------------------------

def create_v8_sound():

    sample_count = int(SAMPLE_RATE * DURATION)

    t = np.arange(sample_count) / SAMPLE_RATE

    # --------------------------------------------------------
    # Phase des einzelnen Zündereignisses
    #
    # 0 ... 1 entspricht einem kompletten Zündabstand
    # --------------------------------------------------------

    phase = (t * IGNITION_FREQUENCY) % 1.0

    # --------------------------------------------------------
    # Zündimpuls
    #
    # Sehr kurzer kräftiger Impuls, danach schnelles Abklingen
    # --------------------------------------------------------

    impulse = np.exp(-phase * 18.0)

    # Etwas weichere Form des Impulses
    impulse *= 0.7 + 0.3 * np.cos(2 * np.pi * phase)

    # --------------------------------------------------------
    # Tiefer Motor-Grundton
    # --------------------------------------------------------

    bass = 0.35 * np.sin(
        2 * np.pi * IGNITION_FREQUENCY * t
    )

    # --------------------------------------------------------
    # Kleine Sägezahn-Komponente
    #
    # Gibt dem Klang etwas Rauheit.
    # --------------------------------------------------------

    saw = 2.0 * phase - 1.0

    # --------------------------------------------------------
    # Zündimpuls bekommt etwas Obertonstruktur
    # --------------------------------------------------------

    sound = (
        1.00 * impulse
        + 0.25 * bass
        + 0.12 * saw
    )

    # --------------------------------------------------------
    # Leichte Sättigung
    #
    # Verhindert einen zu sauberen synthetischen Klang.
    # --------------------------------------------------------

    sound = np.tanh(sound * 1.8)

    # Lautstärke
    sound *= VOLUME

    return sound.astype(np.float32)


# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------

def main():

    print("V8 Standgas-Test")
    print("----------------")
    print(f"Drehzahl:      {RPM} RPM")
    print(f"Zündfrequenz:  {IGNITION_FREQUENCY:.1f} Hz")
    print()
    print("q beendet das Programm.")

    sound = create_v8_sound()

    while True:

        eingabe = input("Enter = Motor laufen lassen, q = Ende: ")

        if eingabe.lower() == "q":
            break

        sd.play(sound, SAMPLE_RATE)
        sd.wait()


if __name__ == "__main__":
    main()
