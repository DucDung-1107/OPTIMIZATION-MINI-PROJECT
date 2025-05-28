from ortools.linear_solver import pywraplp
from collections import defaultdict
import time 
def solve_schedule_mip_ortools():
    with open(filename, 'r') as f:
    lines = f.read().strip().split('\n')

    N, M = map(int, lines[0].split())

    duration = []
    class_teacher = [] 
    class_student = []

    for i in range(1, N + 1):
        t, g, s = map(int, lines[i].split())
        duration.append(t)
        class_teacher.append(g - 1)  # convert to 0-based index
        class_student.append(s)

    room_capacities_input = list(map(int, lines[N + 1].split()))

    NUM_DAYS = 5
    SLOTS_PER_SESSION = 6
    SESSIONS_PER_DAY = 2
    TOTAL_SLOTS_PER_DAY = SLOTS_PER_SESSION * SESSIONS_PER_DAY
    TOTAL_SLOTS = NUM_DAYS * TOTAL_SLOTS_PER_DAY 

    solver = pywraplp.Solver.CreateSolver('CBC_MIXED_INTEGER_PROGRAMMING')
    if not solver:
        print("CBC solver not available.")
        return

#Variasbles
    X = {}
    
    Scheduled = [solver.BoolVar(f'is_scheduled_{i}') for i in range(N)]

   
    enableassign = [[] for _ in range(N)] 

    for i in range(N):
        duration_i = duration[i]
        students_i = class_student[i]
        classscheduled = False

        if duration_i > SLOTS_PER_SESSION:
           
            solver.Add(Scheduled[i] == 0, name=f"class_{i}_too_long")
            continue 

        for s_start in range(TOTAL_SLOTS):
            s_end = s_start + duration_i - 1 

            if s_end >= TOTAL_SLOTS:
                break

            
            sessionstart = s_start // SLOTS_PER_SESSION
            sessionend = s_end // SLOTS_PER_SESSION

            if sessionstart == sessionend:
               
                for r_idx in range(M):
                    if students_i <= room_capacities_input[r_idx]:
                   
                        X[i, s_start, r_idx] = solver.BoolVar(f'X_{i}_{s_start}_{r_idx}')
                        enableassign[i].append((s_start, r_idx))
                        classscheduled = True
        
        if not classscheduled:
           
            solver.Add(Scheduled[i] == 0, name=f"class_{i}_no_valid_sr_combo")


    # Constraints

    # Constraint 1
    for i in range(N):
        current_class_X_sum = []
        for s_start, r_idx in enableassign[i]:
            current_class_X_sum.append(X[i, s_start, r_idx])
        
        if current_class_X_sum: 
            solver.Add(solver.Sum(current_class_X_sum) == Scheduled[i],
                       name=f"link_schedule_X_class_{i}")
        else:
             if duration[i] <= SLOTS_PER_SESSION:
                solver.Add(Scheduled[i] == 0, name=f"ensure_unscheduled_if_no_X_for_class_{i}")


    # Constraint 2
    teacher_to_classes = defaultdict(list)
    for i in range(N):
        teacher_to_classes[class_teacher[i]].append(i)

    for teacher_id in teacher_to_classes:
        classes_for_this_teacher = teacher_to_classes[teacher_id]
        if len(classes_for_this_teacher) < 2:
            continue

        for k_slot in range(TOTAL_SLOTS): 
            overlapping_vars_for_teacher_at_k = []
            for i_class in classes_for_this_teacher:
                duration_i = duration[i_class]

                for s_start_can in range(max(0, k_slot - duration_i + 1), k_slot + 1):
                    for r_room_can in range(M): 
                        if (i_class, s_start_can, r_room_can) in X:
                            overlapping_vars_for_teacher_at_k.append(X[i_class, s_start_can, r_room_can])
            
            if overlapping_vars_for_teacher_at_k:
                solver.Add(solver.Sum(overlapping_vars_for_teacher_at_k) <= 1,
                           name=f"teacher_{teacher_id}_conflict_at_slot_{k_slot}")

    # Constraint 3
    for r_idx in range(M):
        for k_slot in range(TOTAL_SLOTS): 
            overlap = []
            for i_class in range(N):
                duration_i = duration[i_class]
                
                for s_start_can in range(max(0, k_slot - duration_i + 1), k_slot + 1):
                    if (i_class, s_start_can, r_idx) in X:
                        overlap.append(X[i_class, s_start_can, r_idx])
            
            if overlap:
                solver.Add(solver.Sum(overlap) <= 1,
                           name=f"room_{r_idx}_conflict_at_slot_{k_slot}")
    
    # Objective
    objective_terms = [Scheduled[i] for i in range(N)]
    solver.Maximize(solver.Sum(objective_terms))

    # Solve

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        num_scheduled_count = 0
        output_lines = []
        
       

        for i in range(N):
            if Scheduled[i].solution_value() > 0: 
                num_scheduled_count +=1
                class_id_1_indexed = i + 1
                foundd = False
                for s_start, r_idx in enableassign[i]:
                    if X[i, s_start, r_idx].solution_value() > 0.5:
                        start_slot_0_indexed = s_start
                        room_id_0_indexed = r_idx
                        output_lines.append(f"{class_id_1_indexed} {start_slot_0_indexed + 1} {room_id_0_indexed + 1}")
                        foundd = True
                        break

        
        print(num_scheduled_count)
        for line in output_lines:
            print(line)
            
    elif status == pywraplp.Solver.INFEASIBLE:
        print(0)
    else:
        print(0)


if __name__ == '__main__':
    t1=time.time()
    solve_schedule_mip_ortools()
    t2=time.time()
    print(t2-t1)