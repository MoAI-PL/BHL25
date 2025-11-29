# slow10.py
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):  # bezpieczniej i szybciej
        if n % i == 0:
            return False
    return True

primes = []
for i in range(2, 2_000_00):  # 200 tys — długo, ale stabilnie
    if is_prime(i):
        primes.append(i)

print("Primes:", len(primes))
