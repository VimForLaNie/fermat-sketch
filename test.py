from itertools import product

def brute_force_k2(k):
    length = k * k   # number of elements in the vector
    print(length)
    for combo in product(range(k), repeat=length):
        print(combo)
        yield combo   

# for a in brute_force_k2(3):
# 	print(a)