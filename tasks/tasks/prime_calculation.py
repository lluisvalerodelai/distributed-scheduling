from math import ceil, sqrt


def primes_up_to(n):
    primes = 0
    for i in range(n):
        for j in range(2, ceil(sqrt(i))):
            if i % j == 0:
                break
    print("did a primes task")
    return primes
