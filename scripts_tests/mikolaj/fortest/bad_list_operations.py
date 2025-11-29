import time

def placeholder_function_a():
    pass
# Powtórz 5-krotnie, by zwiększyć objętość kodu...
def placeholder_function_e():
    pass

def inefficient_list_insertion(size=50000):
    """
    CEL: Wielokrotne wstawianie na początek listy (`list.insert(0, ...)`) 
    jest bardzo kosztowne, ponieważ wymaga przesunięcia wszystkich 
    istniejących elementów. 
    W sumie ma to złożoność O(n^2), gdzie n jest wielkością listy.
    """
    print("-> Uruchamiam nieefektywne wstawianie na początek listy O(n^2)...")
    slow_list = []
    for i in range(size):
        slow_list.insert(0, i) # <--- To jest kosztowne!
    return len(slow_list)

def slow_string_concatenation(num_chunks=100000):
    """
    CEL: Powolne łączenie ciągów znaków za pomocą operatora `+` w pętli. 
    Lepszym rozwiązaniem byłoby użycie `"".join(lista)`.
    """
    print("-> Uruchamiam powolne łączenie ciągów...")
    result_string = ""
    for i in range(num_chunks):
        result_string += str(i) # <--- To jest kosztowne!
    return len(result_string)

def main():
    # Wąskie gardło O(n^2)
    inefficient_list_insertion(size=20000) 
    
    # Wąskie gardło alokacji pamięci dla stringów
    slow_string_concatenation(num_chunks=50000)

if __name__ == "__main__":
    main()