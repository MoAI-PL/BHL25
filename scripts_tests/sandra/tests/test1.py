# test1.py

def slow_function():
    numbers = []
    for i in range(10000):
        numbers.append(i * i)
    return numbers


def inefficient_io():
    # Zbyt wiele operacji I/O w pętli
    for i in range(300):
        with open("log.txt", "a") as f:
            f.write(f"Line {i}\n")


def redundant_calculations(n):
    # Wykonujemy wielokrotnie to samo obliczenie
    result = 0
    for i in range(n):
        x = (i ** 3) - (i ** 2) + (i * 5)
        result += x
    return result


def main():
    slow_function()
    inefficient_io()
    redundant_calculations(5000)


if __name__ == "__main__":
    main()
