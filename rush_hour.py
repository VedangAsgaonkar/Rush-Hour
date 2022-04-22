from z3 import *
import sys
from constraints import *
import time


# def show_var (i,j,move,id,model):
#     var = "p_" + str(i) + "_" + str(j) + "_" + str(move) + "_" + str(id)
#     var1 = Bool(var)
    
# def create_list (move, m, n):
#     bool_var = []
#     for i in range(n):
#         for j in range(n):
#             for id in range(5):
#                 var = Bool("p_" + str(i) + "_" + str(j) + "_" + str(move) + "_" + str(id))
#                 if m[var]:
#                     bool_var.append((var, True))
#                 else:
#                     bool_var.append((var, False))
#     return bool_var

def compare_moves (move, m, n): #move <= k - 1
    retval = []
    for i in range(n):
        for j in range(n):
            for id in range(5):
                s1 = "p_" + str(i) + "_" + str(j) + "_" + str(move) + "_" + str(id)
                s2 = "p_" + str(i) + "_" + str(j) + "_" + str(move+1) + "_" + str(id)
                var1 = Bool(s1)
                var2 = Bool(s2)
                if bool(m[var1]) != bool(m[var2]):
                    retval.append(str(i) + "," + str(j))
    # print("Move number " + str(move) + ": ", retval[0][:-4] + ") -> " + retval[2][:-4] + ")")
    ###print('----------------------\n', move)
    if len(retval) != 0:
        print(retval[2])



if __name__ == "__main__" :
    input_file = open(sys.argv[1], 'r')
    line_num = 0
    assigned = []
    constraints = []        
    #print("HI1")
    while True:
        line = input_file.readline()
        if not line:
            break
        line = line.strip().split(',')
        if line_num == 0 :
            n = int(line[0])
            k = int(line[1])
            # grid is row x column x move_no x identity
            grid = [ [ [ [ Bool('p_'+str(row) + '_' + str(col) + '_' + str(move_no) + '_' + str(id)) for id in range(5)] for move_no in range(k+1) ] for col in range(n) ] for row in range(n)]
        elif line_num == 1:
            i = int(line[0])
            j = int(line[1])
            constraints.append(grid[i][j][0][3])
            red_car_row = i
            red_car_col = j
            assigned.append((i,j))
        else :
            car_type = int(line[0])
            # 0 for vertical car, 1 for horizontal car, 2 for mine, 3 is red car, 4 is empty
            i = int(line[1])
            j = int(line[2]) 
            constraints.append(grid[i][j][0][car_type])
            assigned.append((i,j))
        line_num += 1
    #print("HI2")
    for i in range(n):
        for j in range(n):
            if (i,j) not in assigned:
                constraints.append(grid[i][j][0][4])
    T0 = time.time()
    min_moves = (n-2)-red_car_col
    for it in range(min_moves,k+1):
            # Add constraints
        #print(it)
        constraints1 = []        
        constraints1.append(check_id(grid, n, it))
        constraints1.append(internal_consistency(grid, n, it))
        constraints1.append(goal_clauses(grid, n, it, red_car_row))
        t0 = time.time()
        constraints1.append(move_consistency2(grid, n, it))
        t1 = time.time()
        ###print('constraints created')
        #print("HI3")
        s = Solver()
        s.add(And(And(constraints), And(constraints1)))
        if s.check() == sat:
            t2 = time.time()
            m = s.model()
            for move in range(it+1):
                #print("HI4", it)
                if move != it:
                    #print("HI5")
                    compare_moves(move,m,n)
                # for i in range(n):
                #     for j in range(n):
                #         for id in range(5):
                #             if m[grid[i][j][move][id]] :
                #                 if id != 4:
                #                     print(id, end=" ")
                #                 else :
                #                     print("_", end=" ")
                #     print('\n')
                # print('---------')
            break
        else:
            t2 = time.time()
            ##print(t1-t0, t2-t0)
    else:
        print('UNSAT')
    #T1 = time.time()
    ###print(T1-T0)
    




    # ##print(constraints)

    # Add SAT solver




    # ##print('solver initialized')
    # # If it is SAT, ##print solution
    # if s.check() == sat:
    #     ###print(s.model())
    #     m = s.model()
    #     ###print(create_list(0, m, n))
    #     for iter in range(k):
    #         compare_moves(iter,m,n)
    #     ##print('SAT')
    #     t2 = time.time()
    # else:
    #     ##print('UNSAT')
    #     ##print(s.statistics()) 
    #     ##print(s.unsat_core())
    #     t2 = time.time()


    
    
