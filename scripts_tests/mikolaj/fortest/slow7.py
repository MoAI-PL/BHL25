# slow7.py
with open("large_output.txt", "w") as f:
    for i in range(2_000_000):
        f.write("Linia numer " + str(i) + "\n")

print("complete")
