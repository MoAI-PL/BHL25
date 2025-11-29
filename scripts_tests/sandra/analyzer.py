import csv
import glob
import os
from eco_code_analyzer import analyze_code, get_eco_score, get_improvement_suggestions

OUTPUT_CSV = "eco_analysis_results.csv"

def analyze_file(path):
    """Wczytuje plik, analizuje kod i zwraca (score, suggestions)."""
    with open(path, "r") as f:
        code = f.read()

    result = analyze_code(code)
    score = get_eco_score(result)
    # suggestions = get_improvement_suggestions(result)

    # zamień listę słowników na jeden string
    #suggestions_text = "\n".join([str(s) for s in suggestions])

    return score


def main():
    # znajdź wszystkie pliki test*.py
    files = sorted(glob.glob("tests/*"))

    if not files:
        print("Brak plików  w katalogu!")
        return

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "eco_score"])

        for file in files:
            print(f"Analiza {file}...")
            score = analyze_file(file)
            writer.writerow([os.path.basename(file), score])

    print(f"\nWyniki zapisane w pliku: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
