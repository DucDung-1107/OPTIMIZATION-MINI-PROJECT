import sys

_global_max_scheduled_count = 0
_global_best_assignments = []
_N_classes_val = 0 
_M_rooms_val = 0  
_classes_data_list = []
_room_capacities_data_list = []
_teacher_busy_schedule_matrix = [] 
_room_busy_schedule_matrix = []   

def _is_valid_placement(class_obj_idx, start_slot_1_indexed, room_idx_0_indexed):

    class_obj = _classes_data_list[class_obj_idx]
    num_periods = class_obj['t']
    teacher_id = class_obj['g'] 
    num_students = class_obj['s']

    if num_students > _room_capacities_data_list[room_idx_0_indexed]:
        return False

    start_slot_0_indexed = start_slot_1_indexed - 1
    end_slot_0_indexed = start_slot_0_indexed + num_periods - 1

    if end_slot_0_indexed >= 60: 
        return False
    
    if (start_slot_0_indexed // 6) != (end_slot_0_indexed // 6):
        return False

    teacher_id_0_indexed = teacher_id - 1 
    for k_slot_0_indexed in range(start_slot_0_indexed, end_slot_0_indexed + 1):
        if _teacher_busy_schedule_matrix[teacher_id_0_indexed][k_slot_0_indexed]:
            return False 
        if _room_busy_schedule_matrix[room_idx_0_indexed][k_slot_0_indexed]:
            return False
    return True

def _backtrack_scheduler(class_k_idx, current_assignments_list):
    """Hàm đệ quy lui để thử xếp lịch."""
    global _global_max_scheduled_count, _global_best_assignments 

    if class_k_idx == _N_classes_val:
        if len(current_assignments_list) > _global_max_scheduled_count:
            _global_max_scheduled_count = len(current_assignments_list)
            _global_best_assignments = list(current_assignments_list) 
        return
    #PRUNING
    if len(current_assignments_list) + (_N_classes_val - class_k_idx) < _global_max_scheduled_count:
        return

    _backtrack_scheduler(class_k_idx + 1, current_assignments_list)

    current_class_obj = _classes_data_list[class_k_idx]
    num_periods = current_class_obj['t']
    teacher_id = current_class_obj['g'] 
    
    for r_idx_0 in range(_M_rooms_val): 

        for s_slot_1 in range(1, 60 - num_periods + 2): 
            if _is_valid_placement(class_k_idx, s_slot_1, r_idx_0):

                
                teacher_id_0_indexed = teacher_id - 1
                start_slot_0_indexed = s_slot_1 - 1
                
                slots_occupied_this_assignment = []
                for i in range(num_periods):
                    slot_idx_to_occupy = start_slot_0_indexed + i
                    slots_occupied_this_assignment.append(slot_idx_to_occupy)
                    _teacher_busy_schedule_matrix[teacher_id_0_indexed][slot_idx_to_occupy] = True
                    _room_busy_schedule_matrix[r_idx_0][slot_idx_to_occupy] = True
                
                current_assignments_list.append({
                    'id': current_class_obj['id'], 
                    'slot': s_slot_1, 
                    'room': r_idx_0 + 1
                })
                
                _backtrack_scheduler(class_k_idx + 1, current_assignments_list)
                
                current_assignments_list.pop()
                for slot_idx_to_free in slots_occupied_this_assignment:
                    _teacher_busy_schedule_matrix[teacher_id_0_indexed][slot_idx_to_free] = False
                    _room_busy_schedule_matrix[r_idx_0][slot_idx_to_free] = False

def solve_timetable_problem():
    """Hàm chính đọc input, chạy thuật toán và in output."""
    global _N_classes_val, _M_rooms_val, _classes_data_list, _room_capacities_data_list
    global _teacher_busy_schedule_matrix, _room_busy_schedule_matrix
    global _global_max_scheduled_count, _global_best_assignments

    _N_classes_val, _M_rooms_val = map(int, sys.stdin.readline().split())
    
    _classes_data_list = []
    max_observed_teacher_id = 0
    for i in range(_N_classes_val):
        t, g, s_count = map(int, sys.stdin.readline().split()) 
        _classes_data_list.append({'id': i + 1, 't': t, 'g': g, 's': s_count})
        if g > max_observed_teacher_id:
            max_observed_teacher_id = g
            
    _room_capacities_data_list = list(map(int, sys.stdin.readline().split()))

    num_teachers_for_array = 100 
    _teacher_busy_schedule_matrix = [[False for _ in range(60)] for _ in range(num_teachers_for_array)] 
    _room_busy_schedule_matrix = [[False for _ in range(60)] for _ in range(_M_rooms_val)]

    _global_max_scheduled_count = 0
    _global_best_assignments = []
    
    _backtrack_scheduler(0, [])

    print(_global_max_scheduled_count)
    for assignment in _global_best_assignments:
        print(f"{assignment['id']} {assignment['slot']} {assignment['room']}")

# Chạy giải thuật
solve_timetable_problem()