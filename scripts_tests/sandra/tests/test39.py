def check_int(x):
    try:
        int(x)
        return True
    except:
        return False

print(check_int("123"))
print(check_int("xx"))
