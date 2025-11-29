def find_duplicates(arr):
    dup = []
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i != j and arr[i] == arr[j] and arr[i] not in dup:
                dup.append(arr[i])
    return dup

print(find_duplicates([1,2,3,2,1,4]))
