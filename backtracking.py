import sys

N = 1005
M = 105
n = 0  # number of classes
m = 0  # number of rooms
t = [0] * N  # duration of each class
g = [0] * N  # teacher ID for each class
s = [0] * N  # number of students in each class
c = [0] * M  # capacity of each room
l = [0] * N  # starting period for each class
bestl = [0] * N  # best starting period found for each class
r = [0] * N  # room assigned to each class
bestr = [0] * N  # best room assignment found for each class
bestClass = 0  # maximum number of classes scheduled
countClass = 0  # current number of classes scheduled

def input_data():
    global n, m
    n, m = map(int, input().split())
    
    for i in range(1, n + 1):
        t[i], g[i], s[i] = map(int, input().split())
    
    c_input = list(map(int, input().split()))
    for i in range(1, m + 1):
        c[i] = c_input[i - 1]
    
    print("Input done")

def solution():
    global bestClass, bestl, bestr
    bestClass = countClass
    for i in range(1, n + 1):
        bestl[i] = l[i]
        bestr[i] = r[i]

def try_assign(i):
    global countClass
    
    k = 1
    while k <= 60 - t[i] + 1:
        # Check if class fits within a single session (morning/afternoon)
        if (k - 1) // 6 == (k + t[i] - 2) // 6:
            for j in range(1, m + 1):
                # Check if room capacity is sufficient
                if c[j] >= s[i]:
                    check_valid = True
                    
                    # Check for conflicts with previously scheduled classes
                    for p in range(1, i):
                        if l[p] > 0:
                            # Check if periods overlap
                            if not (l[p] + t[p] - 1 < k or k + t[i] - 1 < l[p]):
                                # Same teacher or same room
                                if g[p] == g[i] or r[p] == j:
                                    check_valid = False
                                    break
                    if check_valid:
                        l[i] = k
                        r[i] = j
                        countClass += 1
                        
                        if i == n:
                            if countClass > bestClass:
                                solution()
                        else:
                            try_assign(i + 1)
                        
                        # Backtrack
                        countClass -= 1
                        l[i] = 0
                        r[i] = 0
        else:
            # Skip to next session if current session is insufficient
            k = ((k + t[i] - 1) // 6) * 6
        k += 1

    # Try not scheduling this class (always do it now regardless of bound)
    if i == n:
        if countClass > bestClass:
            solution()
    else:
        try_assign(i + 1)

def main():
    input_data()
    try_assign(1)
    
    print(bestClass)
    for i in range(1, n + 1):
        if bestl[i] != 0:
            print(f"{i} {bestl[i]} {bestr[i]}")

if __name__ == "__main__":
    main()
