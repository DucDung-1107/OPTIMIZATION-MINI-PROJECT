import random
import math
from collections import defaultdict

class ClassSchedulingACO:
    def __init__(self, n_classes, n_rooms, durations, teachers, students, room_capacities):
        self.n_classes = n_classes
        self.n_rooms = n_rooms
        self.durations = durations
        self.teachers = teachers
        self.students = students
        self.room_capacities = room_capacities
        
        self.total_slots = 60
        self.slots_per_session = 6  
        
        # Tham số ACO
        self.n_ants = 50
        self.n_iterations = 100
        self.alpha = 1.0  
        self.beta = 2.0   
        self.rho = 0.1    
        self.q0 = 0.9     
        
        self.init_pheromone_matrix()
        
        self.feasible_assignments = self.generate_feasible_assignments()
        
    def init_pheromone_matrix(self):
        """Khởi tạo ma trận pheromone"""
        self.pheromone = {}
        tau0 = 1.0
        
        for class_id in range(self.n_classes):
            for slot in range(self.total_slots):
                for room in range(self.n_rooms):
                    self.pheromone[(class_id, slot, room)] = tau0
    
    def generate_feasible_assignments(self):
        """Tạo danh sách các assignment khả thi cho mỗi lớp"""
        feasible = [[] for _ in range(self.n_classes)]
        
        for class_id in range(self.n_classes):
            duration = self.durations[class_id]
            students = self.students[class_id]
            
            # constraint
            for start_slot in range(self.total_slots):
                end_slot = start_slot + duration - 1
                
                # 
                if end_slot >= self.total_slots:
                    break
                
                #
                start_session = start_slot // self.slots_per_session
                end_session = end_slot // self.slots_per_session
                
                if start_session == end_session:
                    #
                    for room in range(self.n_rooms):
                        if students <= self.room_capacities[room]:
                            feasible[class_id].append((start_slot, room))
        
        return feasible
    
    def calculate_heuristic(self, class_id, slot, room):
        """Tính giá trị heuristic cho assignment"""
        #
        slot_preference = 1.0 / (slot + 1)
        capacity_fit = 1.0 / (self.room_capacities[room] - self.students[class_id] + 1)
        return slot_preference * capacity_fit
    
    def is_valid_assignment(self, schedule, class_id, slot, room):
        """Kiểm tra assignment có hợp lệ không"""
        duration = self.durations[class_id]
        teacher = self.teachers[class_id]
        
        # constraint checking
        for s in range(slot, slot + duration):
      
            for other_class, other_slot, other_room in schedule:
                if other_class == class_id:
                    continue
                    
                other_duration = self.durations[other_class]
                other_teacher = self.teachers[other_class]
                
                if teacher == other_teacher:
                    if other_slot <= s < other_slot + other_duration:
                        return False
                
                if room == other_room:
                    if other_slot <= s < other_slot + other_duration:
                        return False
        
        return True
    
    def construct_solution(self):
        """Một con kiến xây dựng một giải pháp"""
        schedule = []
        scheduled_classes = set()
        
        classes_order = list(range(self.n_classes))
        random.shuffle(classes_order)
        
        for class_id in classes_order:
            if class_id in scheduled_classes:
                continue
                
            best_assignment = None
            best_prob = -1
            
            for slot, room in self.feasible_assignments[class_id]:
                if not self.is_valid_assignment(schedule, class_id, slot, room):
                    continue
                
                pheromone_val = self.pheromone.get((class_id, slot, room), 1.0)
                heuristic_val = self.calculate_heuristic(class_id, slot, room)
                
                prob = (pheromone_val ** self.alpha) * (heuristic_val ** self.beta)
                
                if random.random() < self.q0:
                 
                    if prob > best_prob:
                        best_prob = prob
                        best_assignment = (slot, room)
                else:
                    if random.random() < prob / (prob + 1):
                        best_assignment = (slot, room)
            
            if best_assignment:
                schedule.append((class_id, best_assignment[0], best_assignment[1]))
                scheduled_classes.add(class_id)
        
        return schedule
    
    def evaluate_solution(self, schedule):
        """Đánh giá chất lượng giải pháp"""
        return len(schedule)  
    
    def update_pheromone(self, solutions_fitness):
     
        for key in self.pheromone:
            self.pheromone[key] *= (1 - self.rho)
        
        for schedule, fitness in solutions_fitness:
            delta_tau = fitness / self.n_classes
            for class_id, slot, room in schedule:
                key = (class_id, slot, room)
                if key in self.pheromone:
                    self.pheromone[key] += delta_tau
    
    def solve(self):
        """Giải bài toán bằng ACO"""
        best_solution = []
        best_fitness = 0
        
        for iteration in range(self.n_iterations):
            solutions_fitness = []
            
            for ant in range(self.n_ants):
                solution = self.construct_solution()
                fitness = self.evaluate_solution(solution)
                solutions_fitness.append((solution, fitness))
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_solution = solution.copy()
            
            self.update_pheromone(solutions_fitness)
            

        
        return best_solution, best_fitness

def solve_schedule_aco():
    # input
    n, m = map(int, input().split())
    
    durations = []
    teachers = []
    students = []
    
    for i in range(n):
        t, g, s = map(int, input().split())
        durations.append(t)
        teachers.append(g - 1) 
        students.append(s)
    
    room_capacities = list(map(int, input().split()))
    
    aco = ClassSchedulingACO(n, m, durations, teachers, students, room_capacities)
    best_solution, best_fitness = aco.solve()
    
    print(best_fitness)
    
    best_solution.sort(key=lambda x: x[0])
    
    for class_id, slot, room in best_solution:
        print(f"{class_id + 1} {slot + 1} {room + 1}")

if __name__ == '__main__':
    import time
    t1 = time.time()
    solve_schedule_aco()
    t2 = time.time()
    print(t2-t1)