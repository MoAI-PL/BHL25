def selection_sort(arr):
    result = []
    a = arr[:]
    while a:
        m = a[0]
        for x in a:
            if x < m:
                m = x
        a.remove(m)
        result.append(m)
    return result

print(selection_sort([5,4,3,2,1]))
