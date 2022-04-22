from black import re
from z3 import *

def internal_consistency(grid, n, k):
    # this num_grid is flattened to be of only a particular move
    # 0 for vertical car, 1 for horizontal car, 2 for mine, 3 is red car, 4 is empty
    constraints = []
    for i in range(n):
        for j in range(n):
            for move in range(k+1):
                if j == n-1 :
                    # for red or horizontal car, j != n-1
                    constraints.append(Not(grid[i][j][move][1]))
                    constraints.append(Not(grid[i][j][move][3]))
                else :
                    # num_grid[i][j+1] should be 4 if num_grid[i][j] == 1 or num_grid[i][j] == 3
                    constraints.append(Implies(grid[i][j][move][1], grid[i][j+1][move][4]))
                    constraints.append(Implies(grid[i][j][move][3], grid[i][j+1][move][4]))
                if i == n-1 :
                    # for vertical car, i != n-1
                    constraints.append(Not(grid[i][j][move][0]))
                else :
                    # num_grid[i+1][j] should be 4 if num_grid[i][j] == 0
                    constraints.append(Implies(grid[i][j][move][0], grid[i+1][j][move][4]))
                if i > 0 and j > 0 :
                    constraints.append(Not(And(grid[i][j][move][4], grid[i-1][j][move][0], Or(grid[i][j-1][move][1], grid[i][j-1][move][3]))))
    #print('internal consistency')
    return And(constraints)

def goal_clauses(grid, n, k, red_car_row):
    #print('goal clauses')
    return Or([ grid[red_car_row][n-2][move][3] for move in range(k+1)])

# def sum_to_one(p):
#     # p is list
#     n = len(p)
#     constraints = []
#     constraints.append(Or(p))
#     s = [Bool("s_" + str(i)) for i in range(n-1)]
#     constraints.append(Implies(p[0], s[0]))
#     for i in range(1, n-1):
#         constraints.append(Implies(Or(p[i], s[i-1]), s[i]))
#         constraints.append(Implies(s[i-1], Not(p[i])))
#     constraints.append(Implies(s[n-2],Not(p[n-1])))
#     return And(constraints)

def sum_to_one( ls ):
    return PbEq(tuple([(i,1) for i in ls]), 1)

# def valid_cell(grid, i, j, k, n):

def everything_same_except(grid, i, j, k, n, orientation):
    constraints = []
    if orientation == "down":
        for row in range(n):
            for col in range(n):
                if (row, col) != (i,j) and (row,col) != (i+1, j):
                    for id in range(5):
                        constraints.append(grid[row][col][k][id] == grid[row][col][k+1][id])
    elif orientation == "up":
        for row in range(n):
            for col in range(n):
                if (row, col) != (i,j) and (row,col) != (i-1, j):
                    for id in range(5):
                        constraints.append(grid[row][col][k][id] == grid[row][col][k+1][id])
    elif orientation == "left":
        for row in range(n):
            for col in range(n):
                if (row, col) != (i,j) and (row,col) != (i, j-1):
                    for id in range(5):
                        constraints.append(grid[row][col][k][id] == grid[row][col][k+1][id])
    elif orientation == "right":
        for row in range(n):
            for col in range(n):
                if (row, col) != (i,j) and (row,col) != (i, j+1):
                    for id in range(5):
                        constraints.append(grid[row][col][k][id] == grid[row][col][k+1][id])
    return And(constraints)


def move_consistency(grid, n, k):
    constraints = []
    for move in range(k):
        move_constraints = []
        for i in range(n):
            for j in range(n):
                # move horizontal car from (i, j) to (i, j+1)
                if j < n-1 :
                    move_constraints.append(And(grid[i][j][move][1], grid[i][j+1][move][4], grid[i][j][move+1][4], grid[i][j+1][move+1][1], everything_same_except(grid, i, j, move, n, "right")))
                # move horizontal car from (i, j) to (i, j-1)
                if j > 0:
                    move_constraints.append(And(grid[i][j][move][1], grid[i][j-1][move][4], grid[i][j][move+1][4], grid[i][j-1][move+1][1], everything_same_except(grid, i, j, move, n, "left")))
                # move vertical car from (i,j) to (i+1, j)
                if i < n-1:
                    move_constraints.append(And(grid[i][j][move][0], grid[i+1][j][move][4], grid[i][j][move+1][4], grid[i+1][j][move+1][0], everything_same_except(grid, i, j, move, n, "down")))
                # move vertical car from (i,j) to (i-1, j)
                if i > 0:
                    move_constraints.append(And(grid[i][j][move][0], grid[i-1][j][move][4], grid[i][j][move+1][4], grid[i-1][j][move+1][0], everything_same_except(grid, i, j, move, n, "up")))
                # move red car from (i, j) to (i, j+1)
                if j < n-1 :
                    move_constraints.append(And(grid[i][j][move][3], grid[i][j+1][move][4], grid[i][j][move+1][4], grid[i][j+1][move+1][3], everything_same_except(grid, i, j, move, n, "right")))
                # move red car from (i, j) to (i, j-1)
                if j > 0:
                    move_constraints.append(And(grid[i][j][move][3], grid[i][j-1][move][4], grid[i][j][move+1][4], grid[i][j-1][move+1][3], everything_same_except(grid, i, j, move, n, "left")))                
        # constraints.append(sum_to_one(move_constraints))
        constraints.append(Or(move_constraints))
    #print('move consistency')
    return And(constraints)

def check_id(grid, n, k):
    #print('check id')
    constraints = [ sum_to_one([ grid[i][j][move][id] for id in range(5)]) for move in range(k+1)  for j in range(n) for i in range(n) ]
    # #print(constraints)
    return And(constraints)

#this is for sum=2,not <=2
def sum_to_two(p):
    n=len(p)
    s=[[Bool('u_'+str(id)+'_'+str(val)) for val in range(2) ] for id in range(n) ]
    constraints=[]
    constraints.append(p[0]==s[0][0])
    constraints.append(Not(s[0][1]))
    for i in range(1,n):
        constraints.append((Or(p[i],s[i-1][0]))==s[i][0])
        constraints.append((Or(And(p[i],s[i-1][0]),s[i-1][1]))==s[i][1])
        constraints.append(Implies(s[i-1][1],Not(p[i])))
    constraints.append(s[n-1][1])
    return And(constraints)

def move_consistency2(grid, n, k):
    constraints = []
    for move in range(k):
        move_constraints = []
        change_constraint = []
        for i in range(n):
            for j in range(n):
                change_constraint.append(Or([ Xor(grid[i][j][move][id], grid[i][j][move+1][id]) for id in range(5) ]))
                # move horizontal car from (i, j) to (i, j+1)
                if j < n-1 :
                    move_constraints.append(And(grid[i][j][move][1], grid[i][j+1][move][4], grid[i][j][move+1][4], grid[i][j+1][move+1][1]))
                # move horizontal car from (i, j) to (i, j-1)
                if j > 0:
                    move_constraints.append(And(grid[i][j][move][1], grid[i][j-1][move][4], grid[i][j][move+1][4], grid[i][j-1][move+1][1]))
                # move vertical car from (i,j) to (i+1, j)
                if i < n-1:
                    move_constraints.append(And(grid[i][j][move][0], grid[i+1][j][move][4], grid[i][j][move+1][4], grid[i+1][j][move+1][0]))
                # move vertical car from (i,j) to (i-1, j)
                if i > 0:
                    move_constraints.append(And(grid[i][j][move][0], grid[i-1][j][move][4], grid[i][j][move+1][4], grid[i-1][j][move+1][0]))
                # move red car from (i, j) to (i, j+1)
                if j < n-1 :
                    move_constraints.append(And(grid[i][j][move][3], grid[i][j+1][move][4], grid[i][j][move+1][4], grid[i][j+1][move+1][3]))
                # move red car from (i, j) to (i, j-1)
                if j > 0:
                    move_constraints.append(And(grid[i][j][move][3], grid[i][j-1][move][4], grid[i][j][move+1][4], grid[i][j-1][move+1][3]))    
        # constraints.append(sum_to_two(change_constraint)) 
        constraints.append(Or( And (PbEq( tuple([(b,1) for b in change_constraint])  ,2) , Or(move_constraints) )  , PbEq( tuple([(b,1) for b in change_constraint])  ,0) ))
    return And(constraints)         