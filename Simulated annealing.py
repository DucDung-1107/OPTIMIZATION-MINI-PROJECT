import math
import random
from collections import defaultdict
from copy import deepcopy

# --- Dữ liệu đầu vào (ví dụ) ---
# N_classes, M_rooms = 10, 2
# class_details_raw = [
#     (4, 1, 15), (4, 1, 18), (4, 1, 15), (2, 2, 18), (4, 2, 11),
#     (3, 1, 15), (2, 2, 27), (3, 2, 18), (4, 1, 13), (3, 1, 10)
# ]
# room_capacities_raw = [20, 20]

# MAX_SLOTS = 60 # 5 days * 12 slots/day
# SLOTS_PER_BLOCK = 6 # morning or afternoon block

# --- Chuyển đổi và Chuẩn bị ---
# classes = [{'id': i, 't': d[0], 'g': d[1], 's': d[2]} for i, d in enumerate(class_details_raw)]
# rooms = [{'id': i, 'c': cap} for i, cap in enumerate(room_capacities_raw)]

# --- Helper: Lấy các slot bắt đầu hợp lệ cho một thời lượng ---
def get_valid_start_slots_for_duration(duration, max_slots=60, slots_per_block=6):
    valid_starts = []
    if duration > slots_per_block: # Lớp quá dài cho một buổi
        return []
    for block_start_slot in range(1, max_slots + 1, slots_per_block):
        for offset in range(slots_per_block - duration + 1):
            start_slot = block_start_slot + offset
            if start_slot + duration -1 <= block_start_slot + slots_per_block -1: # Ensure it ends within the block
                 valid_starts.append(start_slot)
    return sorted(list(set(valid_starts))) # unique and sorted

# precompute_valid_starts = {
#    dur: get_valid_start_slots_for_duration(dur) for dur in range(1, SLOTS_PER_BLOCK + 1)
# }

class TimetableState:
    def __init__(self, N, M, classes_info, rooms_info, precomputed_valid_starts, max_slots=60):
        self.N = N
        self.M = M
        self.classes_info = classes_info # list of dicts {'id': original_idx, 't': duration, 'g': teacher, 's': students}
        self.rooms_info = rooms_info   # list of dicts {'id': original_idx, 'c': capacity}
        self.assignments = {}  # class_original_idx -> (start_slot, room_original_idx)
        
        self.teacher_busy_slots = defaultdict(set) # teacher_id -> set of busy slots
        self.room_busy_slots = defaultdict(set)    # room_original_idx -> set of busy slots
        
        self.precomputed_valid_starts = precomputed_valid_starts
        self.max_slots = max_slots

    def calculate_energy(self):
        return -len(self.assignments) # We want to maximize scheduled classes

    def _is_assignment_possible(self, class_original_idx, start_slot, room_original_idx):
        cls = next(c for c in self.classes_info if c['id'] == class_original_idx)
        room = next(r for r in self.rooms_info if r['id'] == room_original_idx)

        # 1. Check room capacity
        if cls['s'] > room['c']:
            return False

        # 2. Check if start_slot is valid for this class duration
        if start_slot not in self.precomputed_valid_starts.get(cls['t'], []):
            return False

        # 3. Check teacher and room availability for all slots
        for i in range(cls['t']):
            current_slot = start_slot + i
            if current_slot in self.teacher_busy_slots[cls['g']]:
                return False
            if current_slot in self.room_busy_slots[room['id']]:
                return False
        return True

    def _add_assignment(self, class_original_idx, start_slot, room_original_idx):
        if class_original_idx in self.assignments: # Should not happen if logic is correct
            print(f"Warning: Class {class_original_idx} already assigned. Overwriting.")
            self._remove_assignment(class_original_idx) # Remove old one first

        cls = next(c for c in self.classes_info if c['id'] == class_original_idx)
        room = next(r for r in self.rooms_info if r['id'] == room_original_idx)
        
        self.assignments[class_original_idx] = (start_slot, room_original_idx)
        for i in range(cls['t']):
            current_slot = start_slot + i
            self.teacher_busy_slots[cls['g']].add(current_slot)
            self.room_busy_slots[room['id']].add(current_slot)
            
    def _remove_assignment(self, class_original_idx):
        if class_original_idx not in self.assignments:
            return # Nothing to remove

        cls = next(c for c in self.classes_info if c['id'] == class_original_idx)
        start_slot, room_original_idx = self.assignments.pop(class_original_idx)
        room = next(r for r in self.rooms_info if r['id'] == room_original_idx)

        for i in range(cls['t']):
            current_slot = start_slot + i
            if current_slot in self.teacher_busy_slots[cls['g']]:
                 self.teacher_busy_slots[cls['g']].remove(current_slot)
            if current_slot in self.room_busy_slots[room['id']]:
                 self.room_busy_slots[room['id']].remove(current_slot)

    def get_neighbor(self):
        new_state = self.copy()
        
        # Determine available actions
        scheduled_class_indices = list(new_state.assignments.keys())
        all_class_indices = [c['id'] for c in new_state.classes_info]
        unscheduled_class_indices = [idx for idx in all_class_indices if idx not in scheduled_class_indices]
        
        possible_actions = []
        if unscheduled_class_indices:
            possible_actions.append("ADD")
        if scheduled_class_indices:
            possible_actions.append("REMOVE")
            possible_actions.append("MOVE") # MOVE is REMOVE then ADD

        if not possible_actions:
            return None # No possible move

        action = random.choice(possible_actions)

        if action == "ADD":
            class_to_add_idx = random.choice(unscheduled_class_indices)
            cls_obj = next(c for c in new_state.classes_info if c['id'] == class_to_add_idx)
            
            potential_slots = list(new_state.precomputed_valid_starts.get(cls_obj['t'], []))
            random.shuffle(potential_slots)
            potential_rooms = [r['id'] for r in new_state.rooms_info]
            random.shuffle(potential_rooms)

            for slot in potential_slots:
                for room_idx in potential_rooms:
                    if new_state._is_assignment_possible(class_to_add_idx, slot, room_idx):
                        new_state._add_assignment(class_to_add_idx, slot, room_idx)
                        return new_state
            return None # Could not add

        elif action == "REMOVE":
            class_to_remove_idx = random.choice(scheduled_class_indices)
            new_state._remove_assignment(class_to_remove_idx)
            return new_state

        elif action == "MOVE":
            class_to_move_idx = random.choice(scheduled_class_indices)
            # Temporarily store old assignment details
            old_slot, old_room_idx = new_state.assignments[class_to_move_idx]
            
            new_state._remove_assignment(class_to_move_idx) # Remove it first

            cls_obj = next(c for c in new_state.classes_info if c['id'] == class_to_move_idx)
            potential_slots = list(new_state.precomputed_valid_starts.get(cls_obj['t'], []))
            random.shuffle(potential_slots)
            potential_rooms = [r['id'] for r in new_state.rooms_info]
            random.shuffle(potential_rooms)

            for slot in potential_slots:
                for room_idx in potential_rooms:
                    # Ensure it's a *new* position or allow same position if it's the only option
                    # For simplicity, we'll just try to find any valid spot.
                    # A stricter "move" would ensure slot != old_slot or room_idx != old_room_idx
                    if new_state._is_assignment_possible(class_to_move_idx, slot, room_idx):
                        new_state._add_assignment(class_to_move_idx, slot, room_idx)
                        return new_state
            
            # If move failed to find a new spot, the class remains unassigned in new_state
            # This is fine, as it's equivalent to a "REMOVE" if no new spot is found.
            return new_state
            
        return None # Should not reach here if logic is correct

    def copy(self):
        new_copy = TimetableState(self.N, self.M, self.classes_info, self.rooms_info, self.precomputed_valid_starts, self.max_slots)
        new_copy.assignments = deepcopy(self.assignments)
        new_copy.teacher_busy_slots = deepcopy(self.teacher_busy_slots)
        new_copy.room_busy_slots = deepcopy(self.room_busy_slots)
        return new_copy

    # Method to generate an initial greedy solution
    def generate_initial_solution_greedy(self):
        # Attempt to schedule all classes greedily
        all_class_indices = [c['id'] for c in self.classes_info]
        random.shuffle(all_class_indices) # Process in random order

        for class_idx_to_schedule in all_class_indices:
            cls_obj = next(c for c in self.classes_info if c['id'] == class_idx_to_schedule)
            potential_slots = list(self.precomputed_valid_starts.get(cls_obj['t'], []))
            random.shuffle(potential_slots) # Try slots in random order
            potential_rooms = [r['id'] for r in self.rooms_info]
            random.shuffle(potential_rooms) # Try rooms in random order

            found_spot = False
            for slot in potential_slots:
                for room_idx in potential_rooms:
                    if self._is_assignment_possible(class_idx_to_schedule, slot, room_idx):
                        self._add_assignment(class_idx_to_schedule, slot, room_idx)
                        found_spot = True
                        break
                if found_spot:
                    break
        # Initial solution is now in self.assignments


def simulated_annealing(N, M, classes_input, rooms_input,
                        max_slots=60, slots_per_block=6,
                        T_initial=1000.0, T_final=0.1, alpha=0.99, iterations_per_temp=100):

    classes = [{'id': i, 't': d[0], 'g': d[1], 's': d[2]} for i, d in enumerate(classes_input)]
    rooms = [{'id': i, 'c': cap} for i, cap in enumerate(rooms_input)]
    
    # Precompute valid start slots for all possible durations
    max_duration = 0
    if classes:
        max_duration = max(c['t'] for c in classes) if classes else 0
    
    # Ensure durations are within reason for precomputation
    precomputed_valid_starts = {
       dur: get_valid_start_slots_for_duration(dur, max_slots, slots_per_block) 
       for dur in range(1, max(slots_per_block, max_duration) + 1)
    }

    current_state = TimetableState(N, M, classes, rooms, precomputed_valid_starts, max_slots)
    current_state.generate_initial_solution_greedy() # Generate some initial solution

    current_energy = current_state.calculate_energy()
    
    best_state = current_state.copy()
    best_energy = current_energy
    
    T = T_initial
    
    while T > T_final:
        for _ in range(iterations_per_temp):
            neighbor_state = current_state.get_neighbor()
            
            if neighbor_state is None: # Move failed
                continue
                
            neighbor_energy = neighbor_state.calculate_energy()
            delta_E = neighbor_energy - current_energy
            
            if delta_E < 0: # Better solution
                current_state = neighbor_state
                current_energy = neighbor_energy
                if current_energy < best_energy:
                    best_state = neighbor_state.copy() # Deep copy best
                    best_energy = current_energy
            else: # Potentially accept worse solution
                if random.random() < math.exp(-delta_E / T):
                    current_state = neighbor_state
                    current_energy = neighbor_energy
        T *= alpha
        # print(f"Temp: {T:.2f}, Current Scheduled: {-current_energy}, Best Scheduled: {-best_energy}")


    # Format output
    # Class IDs, slot IDs, room IDs should be 1-based in output
    output_assignments = []
    for class_original_idx, (start_slot, room_original_idx) in best_state.assignments.items():
        output_assignments.append((class_original_idx + 1, start_slot, room_original_idx + 1))
    
    # Sort by class ID for consistent output, though not strictly required by problem
    output_assignments.sort(key=lambda x: x[0]) 
    
    return len(output_assignments), output_assignments


# --- Main execution ---
if __name__ == '__main__':
    N_classes, M_rooms = map(int, input().split())
    class_details_raw = []
    for _ in range(N_classes):
        class_details_raw.append(tuple(map(int, input().split())))
    room_capacities_raw = list(map(int, input().split()))

    # SA Parameters (can be tuned)
    # iterations_per_temp = N_classes * 10  # Heuristic
    # T_initial, for -len(assignments), delta_E is usually 1 (add/remove one class)
    # So T_initial around 1.0 to 10.0 might be okay if exp(-1/T) ~ 0.3 to 0.9
    # If delta_E is small, T_initial can be smaller.
    # For energy -Q, delta_E is typically -1 (better) or +1 (worse).
    # exp(-1/T) is prob of accepting worse. If T=1, prob=e^-1~0.36. If T=5, prob=e^-0.2~0.81
    
    # A simple heuristic for T_initial: average energy change of a few random moves
    # For now, fixed values.
    sa_T_initial = 5.0 
    sa_T_final = 0.01
    sa_alpha = 0.995 # Slower cooling
    sa_iterations = N_classes * M_rooms * 2 # More iterations
    if N_classes == 0 or M_rooms == 0: # Handle edge case
        sa_iterations = 100

    Q, final_assignments = simulated_annealing(
        N_classes, M_rooms, class_details_raw, room_capacities_raw,
        max_slots=60, slots_per_block=6, # As per problem
        T_initial=sa_T_initial, T_final=sa_T_final, alpha=sa_alpha, 
        iterations_per_temp=sa_iterations
    )

    print(Q)
    for assignment in final_assignments:
        print(f"{assignment[0]} {assignment[1]} {assignment[2]}")