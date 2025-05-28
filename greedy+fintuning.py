import optuna
from collections import Counter
import os

class Class:
    def __init__(self):
        self.nSlot = 0
        self.teacher = 0
        self.nStudents = 0
        self.choosenSlot = 0
        self.choosenRoom = 0
    
    def input(self, values):
        self.nSlot, self.teacher, self.nStudents = map(int, values)

def Assignment(classList, capacity, sorted_class, sorted_rooms, nTeacher):
    usingTeacher = [[False] * 61 for _ in range(nTeacher + 1)]
    usingRoom = [[False] * 61 for _ in range(len(capacity))]
    
    for chooseRoom in sorted_rooms:
        for idClass in sorted_class[:]:
            for startSlot in range(1, 61):
                cls = classList[idClass]
                if capacity[chooseRoom] < cls.nStudents:
                    continue
                endSlot = startSlot + cls.nSlot - 1
                if endSlot > 60 or (startSlot - 1) // 6 != (endSlot - 1) // 6:
                    continue
                if any(usingTeacher[cls.teacher][j] or usingRoom[chooseRoom][j] for j in range(startSlot, endSlot + 1)):
                    continue
                for j in range(startSlot, endSlot + 1):
                    usingTeacher[cls.teacher][j] = True
                    usingRoom[chooseRoom][j] = True
                cls.choosenSlot = startSlot
                cls.choosenRoom = chooseRoom + 1
                sorted_class.remove(idClass)
                break

def run_instance(input_path, output_path, alpha, beta, gamma, delta):
    with open(input_path) as f:
        N, M = map(int, f.readline().split())
        classList = [Class() for _ in range(N)]
        for i in range(N):
            classList[i].input(f.readline().split())
        capacity = list(map(int, f.readline().split()))

    nTeacher = max(cls.teacher for cls in classList)
    teacher_count = Counter(cls.teacher for cls in classList)
    room_fit_count = [sum(cap >= cls.nStudents for cap in capacity) for cls in classList]

    def compute_score(idx):
        cls = classList[idx]
        A = alpha * cls.nStudents
        B = beta * cls.nSlot
        C = gamma / teacher_count[cls.teacher] if teacher_count[cls.teacher] > 0 else 0
        D = delta / room_fit_count[idx] if room_fit_count[idx] > 0 else 0
        return A + B + C + D

    sorted_classes = sorted(range(N), key=compute_score, reverse=True)
    sorted_rooms = sorted(range(M), key=lambda x: -capacity[x])

    Assignment(classList, capacity, sorted_classes, sorted_rooms, nTeacher)

    predicted = sum(1 for cls in classList if cls.choosenSlot and cls.choosenRoom)

    with open(output_path) as f:
        expected = int(f.readline().strip())

    return abs(predicted - expected)

def objective(trial):
    alpha = trial.suggest_float("alpha", 0.1, 10.0)
    beta = trial.suggest_float("beta", 0.1, 10.0)
    gamma = trial.suggest_float("gamma", 0.1, 20.0)
    delta = trial.suggest_float("delta", 0.1, 20.0)

    total_loss = 0
    for i in range(1, 12):
        input_file = f"input{i}.txt"
        output_file = f"output{i}.txt"
        loss = run_instance(input_file, output_file, alpha, beta, gamma, delta)
        total_loss += loss
    return total_loss

study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=50)

print("Best parameters:", study.best_params)
