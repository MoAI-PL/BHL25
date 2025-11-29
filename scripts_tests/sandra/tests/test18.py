def matrix_sum(a, b):
    result = []
    for i in range(len(a)):
        row = []
        for j in range(len(a[0])):
            row.append(a[i][j] + b[i][j])
        result.append(row)
    return result

print(matrix_sum([[1,2],[3,4]], [[5,6],[7,8]]))
