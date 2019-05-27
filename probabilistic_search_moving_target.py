import numpy as np
import random
import queue
import math
import copy
from tkinter import *
from statistics import mean

dim = 50
iter = 10

def create_map(dim):
	map = np.zeros(dim*dim)

	for i in range(dim*dim):
			
			a = np.random.randint(1,10)
			if a == 1 or a == 2:
				map[i] = 0
			elif a == 3 or a == 4 or a == 5:
				map[i] = 1
			elif a == 6 or a == 7 or a == 8:
				map[i] = 2
			else:
				map[i] = 3
	target = np.random.randint(0,(dim*dim)-1)
	#print(map)
	return map,target

def create_belief_map(dim):
	belief_map = np.zeros(dim*dim)
	belief_map += (1/(dim * dim))
	return belief_map

def distancefromtarget(cell,target_cell,dim):
    row_target = int(target_cell / dim)
    column_target = target_cell % dim
    row = int(cell / dim)
    column = cell % dim
    # Find the Manhattan distance
    distance = abs(row_target - row) + abs(column_target - column)

    return distance

def select_cell(map,belief_map,Rule):
    # Select the next cell with highest containing probability
    if Rule == 1:
        max=0
        max_cells=[]
        for i in range(len(belief_map)):
            if belief_map[i] > max:
                max = belief_map[i]
                del max_cells[:]
                max_cells.append(i)
            elif belief_map[i] == max:
                max_cells.append(i)

        if len(max_cells) == 1:
            cell = max_cells[0]
        else:
            cell = max_cells[np.random.randint(0,(len(max_cells)-1))]
    else:
        # Select the next cell with highest finding probability
        max=0
        max_cells=[]
        for i in range(len(belief_map)):
            finding_prob = get_finding_probability(map[i])
            if belief_map[i] * finding_prob > max:
                max = belief_map[i] * finding_prob
                del max_cells[:]
                max_cells.append(i)
            elif belief_map[i] * finding_prob == max:
                max_cells.append(i)

        if len(max_cells) == 1:
            cell = max_cells[0]
        else:
            cell = max_cells[np.random.randint(0,(len(max_cells)-1))]

    return cell

def select_cell_with_distance(map,belief_map,Rule,Prev_cell):
    # Select the next cell with highest containing probability
    if Rule == 1:
        if Prev_cell == -1:
            cell = np.random.randint(0,(dim*dim)-1)
            distance_covered = 1
        else:
            max=0
            max_cells=[]
            for i in range(len(belief_map)):
                if i != Prev_cell:
                    distance = distancefromtarget(Prev_cell,i,dim)
                    distance /= (dim*dim)
                    if (belief_map[i] / distance) > max:
                        max = belief_map[i] / distance
                        del max_cells[:]
                        max_cells.append(i)
                    elif (belief_map[i] / distance) == max:
                        max_cells.append(i)

            if len(max_cells) == 1:
                cell = max_cells[0]
            else:
                cell = max_cells[np.random.randint(0,(len(max_cells)-1))]
            distance_covered = distancefromtarget(Prev_cell,cell,dim)
    else:
        # Select the next cell with highest finding probability
        if Prev_cell == -1:
            cell = np.random.randint(0,(dim*dim)-1)
            distance_covered = 1
        else:
            max=0
            max_cells=[]
            for i in range(len(belief_map)):
                if i != Prev_cell:
                    finding_prob = get_finding_probability(map[i])
                    distance = distancefromtarget(Prev_cell,i,dim)
                    distance /= (dim*dim)
                    if (belief_map[i] * finding_prob / distance) > max:
                        max = belief_map[i] * finding_prob / distance
                        del max_cells[:]
                        max_cells.append(i)
                    elif (belief_map[i] * finding_prob / distance) == max:
                        max_cells.append(i)

            if len(max_cells) == 1:
                cell = max_cells[0]
            else:
                cell = max_cells[np.random.randint(0,(len(max_cells)-1))]
            distance_covered = distancefromtarget(Prev_cell,cell,dim)

    return cell,distance_covered

def find_P_target_not_found(terrain):
    if terrain == 0:                    # flat
        P_target_not_found = 0.1
    elif terrain == 1:                  # Hilly
        P_target_not_found = 0.3
    elif terrain == 2:                  # Forested
        P_target_not_found = 0.7
    elif terrain == 3:                  # Caves
        P_target_not_found = 0.9
    else:
        print("not valid terrain")
        assert(0)
    return P_target_not_found

def get_finding_probability(terrain):
    if terrain == 0:                    # flat
        P_finding = 0.9
    elif terrain == 1:                  # Hilly
        P_finding = 0.7
    elif terrain == 2:                  # Forested
        P_finding = 0.3
    elif terrain == 3:                  # Caves
        P_finding = 0.1
    else:
        print("not valid terrain")
        assert(0)
    return P_finding

def IsTargethunted(cell,target,terrain,Rule):
    if cell == target:
        probability = get_finding_probability(terrain)
        num = probability * 10
        a = np.random.randint(1,10)
        if a <= num:
            return True
        else:
            return False
    else:
        return False

def update_belief_map(cell,terrain,belief_map,Rule):
    # Get the containing probability of the cell using the terrain
    P_target_not_found = find_P_target_not_found(terrain)
    prob_old = belief_map[cell]
    P_failure_in_cell = prob_old * P_target_not_found
    total_prob = P_failure_in_cell + (1 - prob_old)
    if Rule == 1:
        belief_map[cell] = P_failure_in_cell / total_prob
    elif Rule == 2:
        belief_map[cell] = (P_failure_in_cell / total_prob) * get_finding_probability(terrain)
    else:
        print("Invalid Rule")
        assert(0)
    assert(belief_map[cell] >= 0)
    adjust_prob = (prob_old - belief_map[cell])/(dim*dim)
    assert(adjust_prob > 0)
    for i in range(cell):
        belief_map[i]+=adjust_prob
    for i in range(cell+1,dim*dim):
        belief_map[i]+=adjust_prob
    return belief_map

def update_belief_map_moving_target(cells,belief_map,Rule,map):
	#making all cells not in type1 or type2 to 0
	for i in range(dim*dim):
		if i not in cells:
			belief_map[i]=0
	denominator = len(cells)
	old_sum = sum(belief_map)
	#equally distributing probabilities across boundary cells keeping old prob in mind
	if Rule == 1:
		for i in cells:
			belief_map[i] += (1-old_sum)/denominator
	else:
		for i in cells:
			belief_map[i] += ((1-old_sum)/denominator) * get_finding_probability(map[i])
		belief_map *= (1/sum(belief_map))
	return belief_map

def get_neighbors(map, dim, target, radius=1):

    mat = np.array(map).reshape(-1, dim)
    #print(mat)
    row = int((target - (target % dim)) / dim)
    col = (target % dim)
    rows, cols = len(mat), len(mat[0])
    out = []
    k=0

    for i in range(row - radius, row + radius+1):
        #row = []
        for j in range(col - radius, col + radius+1):
        	if 0 <= i < rows and 0 <= j < cols:
        		k=i*dim + j
        		if (k!=target):
        			out.append(k)
        		
    return out

def move_target(map,target,dim):
	neighbors = get_neighbors(map,dim,target)
	#print("neighbors are: ",neighbors)
	a = random.randint(0,len(neighbors)-1)
	#print("a is ",a)
	target = neighbors[a]
	return target

def surveillance_report(old_target,new_target,map):
	old_target_terrain,new_target_terrain = map[old_target],map[new_target]
	a = np.random.randint(1,3)
	if a == 1:
		type1=new_target_terrain
		type2=old_target_terrain
	else:
		type1=old_target_terrain
		type2=new_target_terrain
	return type1,type2

def get_possible_boundaries(type1,type2,map):
	boundaries = []
	cells = []
	for i in range(dim*dim):
		if (map[i] == type1):
			neighbors = get_neighbors(map,dim,i)
			for j in range(len(neighbors)):
				if (map[neighbors[j]]== type2):
					boundaries.append((i,neighbors[j]))
					cells.append(i)
					cells.append(neighbors[j])
	return boundaries,cells

def hunt(map,target,belief_map,Rule):
	runtime=0
	result=0
	while result == 0:
		cell = select_cell(map,belief_map,Rule)
		if IsTargethunted(cell,target,map[target],Rule):
			result = 1
		else:
			#terrain = map[cell]
			#update_belief_map(cell,terrain,belief_map,Rule)
			#move target
			old_target = target
			target = move_target(map,target,dim)
			new_target = target
			#do surveillance
			type1, type2 = surveillance_report(old_target,new_target,map)
			#search all possible boundaries
			boundaries,cells = get_possible_boundaries(type1,type2,map)
			#update belief map
			belief_map = update_belief_map_moving_target(cells,belief_map,Rule,map)

			result = 0
			runtime += 1
	return runtime

def hunt_with_distance(map,target,belief_map,Rule):
    runtime=0
    result=0
    Prev_cell = -1
    while result == 0:
        cell,distance_covered = select_cell_with_distance(map,belief_map,Rule,Prev_cell)
        if IsTargethunted(cell,target,map[target],Rule):
            result = 1
        else:
            #terrain = map[cell]
            #update_belief_map(cell,terrain,belief_map,Rule)
            old_target = target
            target = move_target(map,target,dim)
            new_target = target
            #do surveillance
            type1, type2 = surveillance_report(old_target,new_target,map)
            #search all possible boundaries
            boundaries,cells = get_possible_boundaries(type1,type2,map)
            #update belief map
            belief_map = update_belief_map_moving_target(cells,belief_map,Rule,map)

            result = 0
            runtime += distance_covered
            Prev_cell = cell
    return runtime

def huntTarget(iter,Rule):

    target_Moving_target_steps = []
    for i in range(iter):
        map, target= create_map(dim)
        belief_map = create_belief_map(dim)
        runtime = hunt(map,target,belief_map,Rule)
        print(runtime,"Moving Target")
        target_Moving_target_steps.append(runtime)

    print()
    print("Average no of steps for moving target  %f"%mean(target_Moving_target_steps))

def huntTarget_with_distance(iter,Rule):

    moving_target_with_distance = []
    for i in range(iter):
        map, target= create_map(dim)
        belief_map = create_belief_map(dim)
        runtime = hunt_with_distance(map,target,belief_map,Rule)
        print(runtime,"Moving target with distance")
        moving_target_with_distance.append(runtime)

    print()
    print("Average no of steps moving target with distance terrain %f"%mean(moving_target_with_distance))

type = 3
if type == 0:
    #Hunt the target using Rule 1 - Probablity of containing
    huntTarget(iter,1)
elif type == 1:
    # Hunt the target using Rule 2 - Probablity of finding
    huntTarget(iter,2)
elif type == 2:
    # Hunt target with shortest distance Rule 1
    huntTarget_with_distance(iter,1)
else:
    # Hunt target with shortest distance Rule 2
    huntTarget_with_distance(iter,2)