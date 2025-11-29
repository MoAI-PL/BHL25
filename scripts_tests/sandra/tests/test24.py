def find_max(arr):
    m = arr[0]
    for i in range(len(arr)):
        for j in range(i+1):
            if arr[i] > m:
                m = arr[i]
    return m

print(find_max([1,5,3,9,2]))
