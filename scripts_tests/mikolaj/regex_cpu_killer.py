import re
import time

# Celowo duża lista tekstu do przetworzenia
large_text = "a" * 5000 + "!" 

def simple_redundant_function_1():
    # Funkcja tylko po to, by zająć miejsce
    pass
# Powtórz 10-krotnie proste funkcje, aby sztucznie zwiększyć rozmiar pliku...

def catastrophic_regex_matching(text):
    """
    CEL: Użycie nieefektywnego wyrażenia regularnego, które powoduje
    "catastrophic backtracking" (wzór: (a+)*b).
    """
    print("-> Uruchamiam wyrażenie regularne powodujące Catastrophic Backtracking...")
    # Wzór (a+)+ jest szczególnie problematyczny, gdy brakuje 'b' na końcu, 
    # ale działa i jest widoczny w profilowaniu.
    pattern = re.compile(r"((a*)*)!")
    try:
        start_time = time.time()
        match = pattern.search(text)
        end_time = time.time()
        print(f"Regex zakończone w {end_time - start_time:.4f} s.")
        return match is not None
    except Exception as e:
        print(f"Błąd regex: {e}")
        return False

def main():
    catastrophic_regex_matching(large_text)
    
    # Dodatkowe, proste funkcje dla rozmiaru kodu
    simple_redundant_function_1()
    # ... i inne wywołania


if __name__ == "__main_":
    main()