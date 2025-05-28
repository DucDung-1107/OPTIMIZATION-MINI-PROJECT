from ortools.sat.python import cp_model

def solve_timetable():
    import sys

    # Read input from stdin
    N, M = map(int, input().split())  # number of classes, number of rooms
    t, g, s = [], [], []
    for _ in range(N):
        ti, gi, si = map(int, input().split())
        t.append(ti)
        g.append(gi - 1)  # Convert 1-based to 0-based indexing
        s.append(si)
    c = list(map(int, input().split()))  # Room capacities

    total_slots = 60  # 5 days * 12 periods

    model = cp_model.CpModel()

    # x[i][slot][room]: class i is scheduled at slot in room
    x = {}
    for i in range(N):
        for slot in range(total_slots):
            for r in range(M):
                x[i, slot, r] = model.NewBoolVar(f'x_{i}_{slot}_{r}')

    # y[i]: class i is scheduled
    y = [model.NewBoolVar(f'y_{i}') for i in range(N)]

    # Room capacity constraint
    for i in range(N):
        for slot in range(total_slots):
            for r in range(M):
                if s[i] > c[r]:
                    model.Add(x[i, slot, r] == 0)

    # Each class is scheduled contiguously for t[i] periods if it's scheduled
    for i in range(N):
        possible_starts = total_slots - t[i] + 1
        start_vars = []
        for start in range(possible_starts):
            valid = model.NewBoolVar(f'start_{i}_{start}')
            model.AddBoolAnd([x[i, start + j, r] for j in range(t[i]) for r in range(M)]).OnlyEnforceIf(valid)
            model.AddBoolOr([x[i, start + j, r].Not() for j in range(t[i]) for r in range(M)]).OnlyEnforceIf(valid.Not())

            start_vars.append(valid)
        model.AddMaxEquality(y[i], start_vars)

    # No teacher teaches two classes at the same slot
    teacher_classes = {}
    for i in range(N):
        teacher_classes.setdefault(g[i], []).append(i)

    for teacher, cls_list in teacher_classes.items():
        for slot in range(total_slots):
            model.Add(sum(x[i, slot, r] for i in cls_list for r in range(M)) <= 1)

    # No more than one class in the same room at the same time
    for slot in range(total_slots):
        for r in range(M):
            model.Add(sum(x[i, slot, r] for i in range(N)) <= 1)

    # Class cannot be in two places at the same time
    for i in range(N):
        for slot in range(total_slots):
            model.Add(sum(x[i, slot, r] for r in range(M)) <= 1)

    # Objective: maximize number of scheduled classes
    model.Maximize(sum(y))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        scheduled_classes = []
        for i in range(N):
            if solver.Value(y[i]) == 1:
                for slot in range(total_slots):
                    for r in range(M):
                        if solver.Value(x[i, slot, r]) == 1:
                            scheduled_classes.append((i + 1, slot + 1, r + 1))  # Convert to 1-based
                            break
                    else:
                        continue
                    break
        print(len(scheduled_classes))
        for entry in scheduled_classes:
            print(*entry)
    else:
        print(0)

if __name__ == '__main__':
    solve_timetable()
