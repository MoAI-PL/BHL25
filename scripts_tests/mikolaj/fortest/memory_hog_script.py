import os
import time

# Celowo duża klasa i funkcje, aby zwiększyć rozmiar
class LargeDataContainer:
    def __init__(self, size):
        # Alokacja dużej ilości pamięci
        print("-> Alokuję dużą listę do symulacji zużycia pamięci...")
        self.data = [i * 1.5 for i in range(size)] # Lista duża
        self.metadata = "Initialized at " + time.ctime()

    def process_data(self):
        # Prosta operacja na dużej liście
        total = sum(self.data[::100])
        return total

    def __len__(self):
        return len(self.data)

def slow_file_io_operation(filename="temp_large_file.txt", lines=50000):
    """
    CEL: Powolna operacja I/O (otwieranie i zapisywanie wielu linii),
    która jest często wąskim gardłem.
    """
    print(f"-> Wykonuję powolną operację I/O: zapisuję {lines} linii...")
    with open(filename, 'w') as f:
        for i in range(lines):
            # Częste operacje zapisu obciążają system I/O
            f.write(f"Linia danych {i}: {time.time()}\n")
    # Czekamy na operację usunięcia
    time.sleep(0.1) 
    os.remove(filename)
    print("-> Operacja I/O zakończona.")


def main():
    # Wywołanie funkcji alokującej dużą pamięć (10 milionów elementów)
    container = LargeDataContainer(10000000) 
    result = container.process_data()
    print(f"Suma co setnego elementu: {result}")
    
    # Wywołanie funkcji z powolnym I/O
    slow_file_io_operation()
    
    # Dodatkowe, proste funkcje dla rozmiaru
    a = [i for i in range(1000)]
    b = [x*2 for x in a]


if __name__ == "__main__":
    main()