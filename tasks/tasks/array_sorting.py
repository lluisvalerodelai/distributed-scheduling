from random import randint


def sort_array(n):
    array = [randint(-32767, 32767) for _ in range(n)]
    array.sort()
    print("sorted array")
    return array
