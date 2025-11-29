import time
import random
import math

# I. Celowo duża baza kodu (długie definicje, które nie robią wiele)
def initialize_system_module_1():
    """Moduł inicjalizacyjny 1 - Długie ciało funkcji dla rozmiaru pliku."""
    for i in range(100):
        a = i * 2 + 3
        b = a / 7
        c = b * math.sqrt(a)

def initialize_system_module_2():
    """Moduł inicjalizacyjny 2."""
    for i in range(100):
        x = math.cos(i)
        y = math.sin(i)
        z = x + y

def complex_data_processor_1(data):
    """Przetwarzanie danych 1."""
    return [item ** 2 for item in data]

# Powtarzaj te definicje (np. 10-20 razy), aby sztucznie zwiększyć rozmiar pliku
# (W prawdziwym kodzie byłby to zbiór wielu różnych, złożonych funkcji)
def complex_data_processor_2(data):
    return [item / 2.0 for item in data]

def complex_data_processor_3(data):
    return [item + 100 for item in data]

# ... dodaj więcej podobnych, dużych, ale prostych funkcji dla większego rozmiaru pliku ...

# II. CELOWO NIE EFEKTYWNE BLOKI KODU (Wąskie Gardła)

def sort_large_data_inefficiently(data_size=2000):
    """
    CEL: Generuje dużą listę i sortuje ją. 
    Sortowanie to operacja O(n log n), która jest często widoczna w profilowaniu.
    """
    print("-> Uruchamiam nieefektywne sortowanie dużej listy...")
    data = [random.randint(1, 10000) for _ in range(data_size)]
    data.sort()
    return len(data)

def highly_redundant_calculation(iterations=5000000):
    """
    CEL: Duża, prosta pętla - typowy przykład zużycia CPU.
    """
    print("-> Uruchamiam wysoko redundantne obliczenia...")
    result = 0
    for i in range(iterations):
        result += math.sin(i * 0.001) ** 2
    return result

def nested_loop_slowdown(size=500):
    """
    CEL: Pętla zagnieżdżona O(n^2) - klasyczne wąskie gardło.
    """
    print("-> Uruchamiam spowolnienie pętli zagnieżdżonej O(n^2)...")
    matrix_sum = 0
    for i in range(size):
        for j in range(size):
            # Celowo dodajemy operację, która zajmuje czas
            matrix_sum += math.sqrt(i * j + 1)
    return matrix_sum

def main():
    start_time = time.time()
    
    # 1. Wywołujemy funkcje, które stanowią wąskie gardła
    sort_large_data_inefficiently(data_size=10000)
    
    # 2. Wywołujemy funkcję zużywającą CPU
    highly_redundant_calculation(iterations=1000000) 
    
    # 3. Wywołujemy klasyczny problem O(n^2)
    nested_loop_slowdown(size=1000)
    
    # Wywołanie reszty (mniej istotnych) modułów dla uwiarygodnienia rozmiaru kodu
    data_list = list(range(1000))
    processed_1 = complex_data_processor_1(data_list)
    processed_2 = complex_data_processor_2(processed_1)
    initialize_system_module_1()
    initialize_system_module_2()

    end_time = time.time()
    print(f"\nCałkowity czas wykonania: {end_time - start_time:.2f} sekundy")

if __name__ == "__main__":
    # Aby plik był duży, możesz powtórzyć powyższe definicje lub 
    # po prostu dodać duży blok komentarzy/tekstu, aby zwiększyć jego wagę w systemie plików.
    # Wystarczy, że wywołasz go profilerem.
    main()