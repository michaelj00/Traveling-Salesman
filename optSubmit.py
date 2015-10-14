#!/usr/bin/python

#	
#	Jackie Lamb, Suzanne Thrasher, Michael Jones 
#	CS352  Group 11
#	Project 5
#
# 	11/29/2014
# 	Confirmed distance matrix and calc_path_distance work. 
#   Need to confirm that nearest neighbor works properly
#
#  	11/30/2014
#	Running need quadrants
#
#	11/30/2014	
#	Running. implemented quadrant assignment
#	Needs localized_pairwise_exchange complete
#	Lots of comments added
#
#	11/30/2014
#	Working rather quickly. 
#	Implemented quadrants and breaks if current distance is greater
#	than lowest distance
#
#	11/30/2014
#	added stop cases in pairwise_exchange
#	Got 252 nearest neighbors for 279 with a low of 2937
#
#	12/1/2014
#	Added more comments. 
#	Implemented a 3-opt solution. 3-opt solution is really only
#	valid for test cases < 300
#	Does however give slightly closer results than both 2-opt
#	and localized 2-opt when 3-opt run first and 2-opt after
#
#	12/2/2014
#	Corrected issue of not finding unique nearest path.
#
#	Sources:
#	http://web.stanford.edu/class/cs238/lect_notes/lecture12-13-05.pdf
#	http://isd.ktu.lt/it2011/material/Proceedings/1_AI_5.pdf
#	http://users.eecs.northwestern.edu/~haizhou/357/lec2.pdf
#	https://www.zib.de/borndoerfer/Homepage/Documents/WS11/WS11-CIP-TU-12.pdf
#	http://www.lsi.upc.edu/~mjserna/docencia/algofib/P07/dynprog.pdf
#	http://en.wikipedia.org/wiki/Travelling_salesman_problem
#	https://www.youtube.com/watch?v=-cLsEHP0qt0
#	http://www.seas.gwu.edu/~simhaweb/champalg/tsp/tsp.html



'''
		implementation with watch is 
		
		python watch.py python <program_name> <input file>
		
		python watch.py python opttest.py tsp_example_2.txt
'''


import time
import fileinput
import sys
import copy
import math
import signal
import atexit
import random
import itertools
import operator
from operator import itemgetter

shortest = 100000000
'''
#	The signal handler. On receiving sigterm, it writes
#	the latest result to the file.
#	Provided by instructor. 
#
#	change shortest path to whatever variable you need. 
#'''
def sig_term(num, frame):
	global lowest_distance
	global shortest
	global new_path

	ofile = fileinput.filename() + '.tour'
	with open(ofile, 'w') as f:
		f.write("%s\n" % lowest_distance)
		for i in range (0, len(new_path)):
			f.write("%s\n" % new_path[i])
	print "shortest tour = %s" % lowest_distance



'''#
#	distance_two_points
#	
#	args:   two points to find euclidean distance between
#	returns: rounded integer distance 
'''
def distance_two_points(pointa,pointb):
	return int(round(math.sqrt(  (pointa[1] - pointb[1])**2 + (pointa[2] - pointb[2])**2)))
         
	
'''#
#	Create a 2d list of distances where the i and j are points
#	and the relation between the two is the distance
#	
#		 1   2  3  4  i
# 	1	['', 4, 7, 8]
#	2	[4, '', 3, 4]
#	3	[7, 3, '', 1]
#	4	[8, 4, 1, '']
#	j
#
#	args:   	a list of points 
#	returns:	a populated 2D table of distances between points. 
	'''
def distance_table(original_points_listing):
	dist_table = [[0 for i in range(len(original_points_listing))] for j in range(len(original_points_listing))]
 
	for j in range(0, len(original_points_listing)):
		for i in range(len(original_points_listing)):
			if i == j:
				dist_table[i][j] = float("inf")
				break
			else:
				dist = distance_two_points(original_points_listing[i], original_points_listing[j])	
				dist_table[i][j] = dist
				dist_table[j][i] = dist
	return dist_table
	
'''
	Remove_First will remove the "city name" from the listing. 

	This will return a new list with only (x,y) coordinates. 
		
	********	NOT USED NOT USED  	****************

	'''
def remove_first(listing):
	xylisting = [[0 for i in range(len(listing))] for j in range(len(listing))]
	xylisting = copy.deepcopy(listing)
	for i in range(len(listing)):
		xylisting[i].pop(0)
	return xylisting


'''
#	Creates a random 2d list of cities with distances from 0-x
#
#	Returns listing in a (x,y) format  '''
	
def random_list(x):
	''' Generate a number of cities located on random places '''
	MAXX = 999
	MAXY = 999
	listing = [ [i, random.randrange(0, MAXX),
				random.randrange(0, MAXY)]
				for i in range(x) ]
 
	return listing


'''
	This function creates the nearest neighbor path
	
	Args:  		distance_matrix and original_points_listing
	Returns:	The new nearest neighbor path and the length of that path

'''
def find_path_nearest(distance_matrix, original_points_listing):
 
		#just a precaution to preserve original list. 
	new_list = copy.deepcopy(original_points_listing)
	global starting_point_used
	old_distance = 100000000
	total_distance = 0
	current_point = 0 
	path = []

		#	find random starting point
	current_point = random.randrange(0, len(new_list) ) 

		
		#	if starting_point_used contains all elements of the list reset
	if len(starting_point_used ) == len(new_list):
		del starting_point_used[:]
		#print "list reset!!"
	
		#	if current point has already been calculated. find new point
	while current_point in starting_point_used:
		current_point = random.randrange(0, len(new_list) )

		#	add starting point to a list of used starting points to
		#	prevent reusing same graph that was already used
	starting_point_used.append(current_point)
	print "starting point ", current_point
		#	Verified original starting point and add it to path
	path.append(current_point)

		#	find next shortest path from current_point
	for i in range(0, len(new_list) ):
		distance = 10000000
		old_distance = 10000000
		
		#	find min distance in sub list of current vertex
		#	assign that value to min_point

		for z in range(0, (len(distance_matrix)) ):
				#	distance from current point to 
			distance = distance_matrix[current_point][z]

			if (distance < old_distance) and (z not in path) and (z != current_point):
					old_distance = distance
					min_point = z
			
			#	Insert new point in the path
		if  (min_point not in path):
			path.append(min_point)
			#	Assign current point to closest point for next iteration. 
		current_point = min_point	
	
	total_distance = calc_path_distance(path, distance_matrix)
	
	return total_distance, path

'''
	find_nearest
		Just a driver function to generate nearest neighbor paths and 
		call the exchange functions. We will also store the lowest path 
		found in nearest neighbor in case that is the only instance we get.
		
	Args:		original_points_listing, distance_matrix
	Returns:	nothing
	Calls:		find_path_nearest and exchange program

'''
def find_nearest(original_points_listing, distance_matrix):
	global shortest
	global new_path 
	global lowest_distance
	test_path = []
	shortest = 100000000
	short = 100000000
	
	temp_lowest_distance, test_path = find_path_nearest(distance_matrix, original_points_listing)
	
		#	if nearest neighbor happens to be best path
	if temp_lowest_distance < lowest_distance:
		lowest_distance = temp_lowest_distance
		new_path = copy.deepcopy(test_path)
	
	pairwise_exchange_path = copy.deepcopy(test_path)
	localized_pairwise_exchange_path = copy.deepcopy(test_path)
	
	#if len(original_points_listing) < 200:
	#	print "three opt"
	#	threeopt(localized_pairwise_exchange_path, distance_matrix, original_points_listing)
	#elif len(original_points_listing) < 270:
	#	print "pairwise_exchange"
	#	localized_pairwise_exchange(pairwise_exchange_path, distance_matrix, original_points_listing)
	#else:
	threeopt(localized_pairwise_exchange_path, distance_matrix, original_points_listing)

	
'''
	This is an optional function. 
	
	It implements on iteration of three opt.
	Three opt involves switching the places of 3 cities in the list. 
	
	Once three opt has been run Localized pairwise_exchange is called
	Note three opt does involve use of neighborhoods to attempt to 
		speed up algorithm.

'''
	
	
def threeopt(localized_pairwise_exchange_path, distance_matrix, original_points_listing):
	global lowest_distance
	global new_path
	low_distance = 10000000000
	curr_distance = 1000000000
	path = copy.deepcopy(localized_pairwise_exchange_path)
	
	no_improve = 1
	opt_new_path = copy.deepcopy(new_path)
	preserve_path = copy.deepcopy(path)
	
	while no_improve > 0:
		preserve_path = copy.deepcopy(path)
		no_improve = 0
		for i in range(0, len(preserve_path) - 1):
			for j in range(i + 1, len(preserve_path)):
				for k in range(j+1, len(preserve_path)):
					if (original_points_listing[i][3] == original_points_listing[j][3])and(original_points_listing[j][3] == original_points_listing[k][3]):
					
						preserve_path = copy.deepcopy(path)
						preserve_path[i], preserve_path[j], preserve_path[k] = preserve_path[k], preserve_path[i], preserve_path[j]
						curr_distance = calc_path_distance(preserve_path, distance_matrix)
						if curr_distance < low_distance:
							print "running"
							low_distance = curr_distance
							lowest_path = copy.deepcopy(preserve_path)
							no_improve = no_improve + 1 
				if low_distance >= lowest_distance:
					break
			if low_distance >= lowest_distance:
					break
				#	keeps new found shortest_path
			path = copy.deepcopy(lowest_path)
	
	if low_distance < lowest_distance:
		lowest_distance = low_distance
		new_path = copy.deepcopy(lowest_path)
		opt_new_path = copy.deepcopy(lowest_path)  #path
	print "lowest_distance in 3-opt", lowest_distance	
	
	three_opt_path = copy.deepcopy(opt_new_path)
	if len(opt_new_path) < 275:
		pairwise_exchange(three_opt_path, distance_matrix, original_points_listing)
	elif len(opt_new_path) < 5000:
		localized_pairwise_exchange(three_opt_path, distance_matrix, original_points_listing)

'''
	localized_pairwise_exchange takes into account the point "neighbor hoods to allow selective inclusion"
		into the 2-opt switch. 
	It will continually generate paths until the path no longer improves. 
	
	Args:  localized_pairwise_exchange_path, distance_matrix, original_points_listing
	Returns: nothing

	'''
def localized_pairwise_exchange(localized_pairwise_exchange_path, distance_matrix, original_points_listing):
	global lowest_distance
	global new_path
	low_distance = 10000000000
	curr_distance = 1000000000
	path = copy.deepcopy(localized_pairwise_exchange_path)
	
	no_improve = 1
	preserve_path = copy.deepcopy(path)
	
	while no_improve > 0:
		preserve_path = copy.deepcopy(path)
		no_improve = 0
		for i in range(0, len(preserve_path) - 1):
			for j in range(i + 1, len(preserve_path)):
				if original_points_listing[i][3] == original_points_listing[j][3]:
					
					preserve_path = copy.deepcopy(path)
					preserve_path[i], preserve_path[j] = preserve_path[j], preserve_path[i]
					curr_distance = calc_path_distance(preserve_path, distance_matrix)
					if curr_distance < low_distance:
						print "running"
						low_distance = curr_distance
						lowest_path = copy.deepcopy(preserve_path)
						no_improve = no_improve + 1 
			if low_distance >= lowest_distance:
				#print "broke"
				#print "low_distance:", low_distance
				break
			#	keeps new found shortest_path
		path = copy.deepcopy(lowest_path)
	if low_distance < lowest_distance:
		lowest_distance = low_distance
		new_path = copy.deepcopy(lowest_path)#path
	print "lowest_distance in localized_pairwise_exchange", lowest_distance	
	
'''
	Pairwise_exchange
	
	This is a simple 2-opt program that changes the placment of two cites in
	the list with no regard for neighborhoods.
	
'''
	
	
def pairwise_exchange(path, distance_matrix, original_points_listing):
	global lowest_distance
	global new_path
	low_distance = 10000000000
	curr_distance = 10000000000

	no_improve = 1
		#	path is protected as the original path of reference 
	preserve_path = copy.deepcopy(path)
	
	while no_improve > 0:
			#	go back to either a fresh copy of the path or and most
			#	likely the "better" copy of the path found below
		preserve_path = copy.deepcopy(path)
			#	set to automatically stop outside loop as no improvement
		no_improve = 0
		
		for i in range(0, len(preserve_path) - 1 ):
				#	i + 1 should prevent path to itself from being evaluated
			for j in range(i + 1, len(preserve_path)):
					#	set reference path back to original for each i for eval
				preserve_path = copy.deepcopy(path)
				preserve_path[i], preserve_path[j] = preserve_path[j], preserve_path[i]
				curr_distance = calc_path_distance(preserve_path, distance_matrix)
				if curr_distance < low_distance:
					print "running"
					low_distance = curr_distance
					lowest_path = copy.deepcopy(preserve_path)
					no_improve = no_improve + 1 
			if low_distance >= lowest_distance:
				#print "broke"
				#print "low_distance:", low_distance
				break
		#	this is here to reset lowest path for return while loop
		path = copy.deepcopy(lowest_path)
	
	if low_distance < lowest_distance:
		lowest_distance = low_distance
		new_path = copy.deepcopy(lowest_path)#path
	print "lowest_distance in pairwise_exchange", lowest_distance
	
'''
	Given a path. This function will return the total length of 
	the path. 

'''
def calc_path_distance(path, distance_matrix):
	path_distance = 0
	for i in range(1,len(path)):
			path_distance = path_distance + distance_matrix[path[i]][path[i-1]]
		#	This is added to allow for return to start. 
	path_distance = path_distance + distance_matrix[path[0]][path[len(path)-1]]
	return path_distance


'''
	Please note quadrant numbers are added to the fourth element of a listing
		so [2, 4, 5, 1] means [city number, x, y, quadrant]
					
					y
		            |
		   2       	|     1
					|
		_____________________________x
					|
					|
		   3		|     4
					|

	This function takes the listing and goes point by point to see what
		quadrant the point should fall in. This will generate 4 distinct 
		neighborhoods of values to choose from.
'''	
	

def quadrants_creator(original_points_listing):
	xtotal = 0
	ytotal = 0
	quad_listing = []
	WestPath = []
	EastPath = []
	NorthPath = []
	SouthPath = []
	
	
		#	determine average of x & y values
	for i in range(0, len(original_points_listing)):
		xtotal = xtotal + original_points_listing[i][1]
		ytotal = ytotal + original_points_listing[i][2]
	xaverage = xtotal/len(original_points_listing)
	yaverage = ytotal/len(original_points_listing)
	
	
		#	Separate inputs into N,S,E,W 
	for i in range(0, len(original_points_listing)):
		if original_points_listing[i][1] <= xaverage:
			WestPath.append(original_points_listing[i])
		else:
			EastPath.append(original_points_listing[i])
	for j in range(0, len(original_points_listing)):
		if original_points_listing[j][2] <= yaverage:
			SouthPath.append(original_points_listing[j])
		else:
			NorthPath.append(original_points_listing[j])
	
		#	Incase you would like to see how evenly items are 
		#	distributed to paths. Uncomment. 
	#print "len(NorthPath)",len(NorthPath)
	#print "len(SouthPath)",len(SouthPath)
	#print "len(EastPath)",len(EastPath)
	#print "len(WestPath)",len(WestPath)
	
		#	Combine N,S,E,W into quadrants. 
	for k in range(0, len(original_points_listing)):
		if original_points_listing[k] in NorthPath and original_points_listing[k] in EastPath:
			original_points_listing[k].append(1)
		elif original_points_listing[k] in NorthPath and original_points_listing[k] in WestPath:
			original_points_listing[k].append(2)
		elif original_points_listing[k] in SouthPath and original_points_listing[k] in EastPath:
			original_points_listing[k].append(4)
		elif original_points_listing[k] in SouthPath and original_points_listing[k] in WestPath: 
			original_points_listing[k].append(3)
		else:
			print "Error didn't fall into path"
	
	
	
		

def main():

	global lowest_distance
	global starting_point_used
	
	starting_point_used = []
	lowest_distance = 10000000000
	''' 	Register signal handler  '''
	signal.signal(signal.SIGTERM, sig_term)
		
	''' 	parse text file and convert into [city, x, y] formatted list  '''
	original_points_listing = [[int(i) for i in line.split()] for line in fileinput.input()]	
	
	#original_points_listing = random_list(10000)

	quadrants_creator(original_points_listing)

	'''		prints the distance matrix   '''
	distance_matrix = distance_table(original_points_listing)
	
 
		#	While loop to generate constant calculations

	count = 0	#	count just gives a visual of how many paths have been evald
	while 1:
		start_time_matrix = time.time()
		find_nearest(original_points_listing, distance_matrix)
		end_time_matrix = time.time()
		timing_matrix = end_time_matrix - start_time_matrix
		print "Time for matrix= ", timing_matrix
		count = count +1 
		print count

	
if __name__ == '__main__':
    main()
    
