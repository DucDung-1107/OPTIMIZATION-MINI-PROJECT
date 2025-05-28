import time

class Class:
    def __init__(self):
        self.nSlot = 0
        self.teacher = 0
        self.nStudents = 0
        self.choosenSlot = 0
        self.choosenRoom = 0
    
    def input(self, values):
        self.nSlot, self.teacher, self.nStudents = map(int, values)

def Assignment(M, nTeacher, sorted_class, sorted_rooms):
    usingTeacher = [[False] * 61 for _ in range(nTeacher + 1)]  # Changed to 61 to handle index 60
    usingRoom = [[False] * 61 for _ in range(M)]  # Changed to 61 to handle index 60
    
    # Xác định ngày, tiết và phòng cho mỗi lớp
    for chooseRoom in sorted_rooms:
        for idClass in sorted_class[:]:  # Create a copy to safely modify during iteration
            for startSlot in range(1, 61):
                if capacity[chooseRoom] < classList[idClass].nStudents:
                    continue
                
                endSlot = startSlot + classList[idClass].nSlot - 1
                if endSlot > 60:  # Check if endSlot exceeds limit
                    continue
                if (startSlot - 1) // 6 != (endSlot - 1) // 6:
                    continue
                
                checkValidArrangement = True
                for j in range(startSlot, endSlot + 1):
                    if usingTeacher[classList[idClass].teacher][j]:
                        checkValidArrangement = False
                        break
                    
                    if usingRoom[chooseRoom][j]:
                        checkValidArrangement = False
                        break
                
                if checkValidArrangement:
                    for j in range(startSlot, endSlot + 1):
                        usingTeacher[classList[idClass].teacher][j] = True
                        usingRoom[chooseRoom][j] = True
                    
                    classList[idClass].choosenSlot = startSlot
                    classList[idClass].choosenRoom = chooseRoom + 1
                    sorted_class.remove(idClass)
                    break

# Đọc N và M từ input
N, M = map(int, input().split())

# Tạo danh sách lớp
classList = [Class() for _ in range(N)]

# Đọc thông tin lớp từ input
for i in range(N):
    values = input().split()
    classList[i].input(values)

# Đọc thông tin capacity từ input
capacity = list(map(int, input().split()))

# Số lượng giáo viên
nTeacher = max(classList, key=lambda x: x.teacher).teacher

t1 = time.time()

# Sort theo số lượng sinh viên
sorted_classes = sorted(range(N), key=lambda x: -classList[x].nStudents)

# Sort theo sức chứa
sorted_rooms = sorted(range(M), key=lambda x: -capacity[x])

Assignment(M, nTeacher, sorted_classes, sorted_rooms)

t2 = time.time()

# Đếm số lớp được xếp lịch
maximum_Classes = 0
for index, assignment in enumerate(classList):
    if classList[index].choosenRoom and classList[index].choosenSlot:
        maximum_Classes += 1

print(maximum_Classes)

# In kết quả xếp lịch
for index, assignment in enumerate(classList):
    if classList[index].choosenRoom and classList[index].choosenSlot:
        print(f"{index + 1} {classList[index].choosenSlot} {classList[index].choosenRoom}")

print(f"Time solution: {t2-t1:.10f}")