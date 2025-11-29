import os
import subprocess
from codecarbon import EmissionsTracker
import csv
from datetime import datetime

FOLDER = r"D:\MoAI\Hackatony\BHL25\BHL25\test_dataSet"
OUTPUT_CSV = "wyniki.csv"
CARBON_DIR = "carbon_logs"

# maksymalny czas wykonywania pliku .py (w sekundach)
TIME_LIMIT = 30


def main():
    os.makedirs(CARBON_DIR, exist_ok=True)

    if not os.path.isdir(FOLDER):
        print("Folder nie istnieje:", FOLDER)
        return

    py_files = [f for f in os.listdir(FOLDER) if f.endswith(".py")]

    if not py_files:
        print("Brak plików .py w folderze:", FOLDER)
        return

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["plik", "emisja_kg", "czas_startu", "czas_stopu", "timeout"])

        for filename in py_files:
            filepath = os.path.join(FOLDER, filename)

            print(f"\n===== Testuję {filename} =====")

            tracker = EmissionsTracker(
                output_dir=CARBON_DIR,
                output_file=f"carbon_{filename}.csv"
            )

            start_time = datetime.now().isoformat()
            tracker.start()

            timed_out = False

            try:
                subprocess.run(
                    ["python", filepath],
                    check=False,
                    timeout=TIME_LIMIT,  # ⏱️ limit czasu
                )
            except subprocess.TimeoutExpired:
                print(f"⚠️ Timeout po {TIME_LIMIT} sekundach, przechodzę dalej...")
                timed_out = True
            except Exception as e:
                print("Błąd podczas wykonywania:", filename, e)

            emissions = tracker.stop()
            stop_time = datetime.now().isoformat()

            writer.writerow([filename, emissions, start_time, stop_time, timed_out])

            print(f"→ Emisja: {emissions} kg (timeout: {timed_out})")

    print("\nZakończono! Wyniki zapisane w:", OUTPUT_CSV)


if __name__ == "__main__":
    main()
