#PYTHON 
import sys
input = sys.stdin.readline

 
def greedy_schedule(n, m, duration, teacher, student, room_cap):
    roomschedule = [[False] * 60 for _ in range(m)]
    teacherschedule = [[False] * 60 for _ in range(100)]  

    res = []
    order = sorted(range(n), key=lambda i: duration[i])
#constraints
    for i in order:
        assign = False
        for start in range(0, 60 - duration[i] + 1):
            for r in range(m):
                if student[i] > room_cap[r]:
                    continue
                if all(not roomschedule[r][start + d] for d in range(duration[i])) and \
                   all(not teacherschedule[teacher[i]][start + d] for d in range(duration[i])):

                    # Assign class
                    for d in range(duration[i]):
                        roomschedule[r][start + d] = True
                        teacherschedule[teacher[i]][start + d] = True
                    res.append((i + 1, start + 1, r + 1))  
                    assign = True
                    break
            if assign:
                break

    print(len(res))
    for i in sorted(res):
        print(*i)

n, m = map(int, input().split())
clas = [list(map(int, input().split())) for _ in range(n)] 
duration=[]
teacher=[]
studentt=[]
for i in range(n):
    duration.append(clas[i][0])
    teacher.append(clas[i][1])
    studentt.append(clas[i][2])
room_cap = list(map(int, input().split()))

greedy_schedule(n,m,duration,teacher,studentt,room_cap)
