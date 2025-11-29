import time

# Zestaw dużych funkcji dla rozmiaru kodu (powtórz wiele razy)
def module_initialization_a():
    pass
def module_initialization_b():
    pass
# ...

def deep_recursive_call(depth):
    """
    CEL: Głębokie wywołanie rekurencyjne, obciążające stos.
    """
    if depth > 0:
        return deep_recursive_call(depth - 1)
    return 1

def quad_nested_loops(n=200):
    """
    CEL: Pętla O(n^4) - ekstremalnie wolne obliczenia, 
    które dominują w profilowaniu.
    """
    print(f"-> Uruchamiam pętlę O(n^4) dla n={n}...")
    total = 0
    # O(n^4)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for l in range(n):
                    total += i + j + k + l
    return total

def main():
    # Wąskie gardło O(n^4)
    # n=200 może zająć chwilę, możesz zmniejszyć do n=50 dla szybszych testów
    quad_nested_loops(n=100) 
    
    # Obciążenie stosu
    deep_recursive_call(1000)
    
    # Wywołania innych funkcji dla zwiększenia rozmiaru...
    module_initialization_a()


if __name__ == "__main__":
    main()