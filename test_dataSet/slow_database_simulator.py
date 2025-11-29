import pickle
import random
import time
import sys

# Klasa symulująca duży rekord bazy danych
class DbRecord:
    def __init__(self, index):
        self.id = index
        self.large_data = [random.uniform(0, 1) for _ in range(10000)]
        self.timestamp = time.time()
        
    def get_serialized_size(self):
        # Celowo używamy sys.getsizeof, by pokazać rozmiar obiektu
        return sys.getsizeof(self)

# Dodatkowe funkcje, które nic nie robią, ale zwiększają rozmiar pliku...

def simulate_slow_serialization(num_records=50):
    """
    CEL: Wielokrotna, powolna serializacja/deserializacja dużych obiektów
    (symulacja interakcji z wolnym storage'em lub siecią).
    """
    print("-> Symuluję powolną serializację dużych obiektów...")
    records = [DbRecord(i) for i in range(num_records)]
    
    serialized_data = []
    
    # Bardzo powolne serializowanie
    for record in records:
        # pickle.dumps jest operacją obciążającą CPU
        serialized_data.append(pickle.dumps(record))
        time.sleep(0.005) # Symulacja opóźnienia I/O/sieci
        
    # Bardzo powolne deserializowanie
    deserialized_records = []
    for data in serialized_data:
        # pickle.loads jest operacją obciążającą CPU i pamięć
        deserialized_records.append(pickle.loads(data))
        
    print(f"Liczba przetworzonych rekordów: {len(deserialized_records)}")

def main():
    simulate_slow_serialization(num_records=100)
    # Wywołania innych funkcji dla zwiększenia rozmiaru...

if __name__ == "__main__":
    main()