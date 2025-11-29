def filter_even(arr):
    out = []
    for x in arr:
        if x % 2 == 0:
            out.append(x)
    return out

print(filter_even([1,2,3,4,5,6]))

