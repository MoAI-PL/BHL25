def find_min(arr):
    m = arr[0]
    for x in arr:
        if x < m:
            m = x
    return m

print(find_min([9,4,6,1,8]))
