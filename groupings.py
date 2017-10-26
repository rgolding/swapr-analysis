#####################################
####        Imports              ####
#####################################
import analysis
import random
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#####################################
####        Global Vars          ####
#####################################
numOfRuns = 100
minSizeGroup = 3
maxSizeGroup = 10



#####################################
####        Database             ####
#####################################
database = 'db.sqlite'
db = sqlite3.connect(database)	

"""
Analysis steps:
1. Make groupings of students from size 0 to n (x times of each)

For each practice 2 assignment:	
2. Get each student's offset and bibi from weights for each item index
3. Get practice video ratings from practice video 2
4. do the math
5. comparing expert
6. find squares

"""

def steps(start, end, lab, videoLabel):
	print("lab", lab)
	print(videoLabel)


	all_students = get_all_students(lab, videoLabel)

	ret_val = []

	for j in range(start, end + 1):

		differences = []

		for i in range(numOfRuns):
		

			#1. Make a group
			try:
				g = groups(j, all_students)
			except:
				print("lab", lab)
				print("all_students:", all_students)

			#2. Get weights
			w = weights(g, lab)
			# print (w)

			#3 Get practice video2 for that lab
			prac_ratings = practice_video_x(g,lab, videoLabel)
			# print (prac_ratings)

			#4 do the math
			student_score = math(g, prac_ratings, w)
			if not student_score:
				continue
			# print(student_score)

			#5. comparing to expert

			expert_scores = get_expert_scores(lab, videoLabel)
			# print(expert_scores)

			# p(student_score, expert_scores)

			#6. perform sum squared
			try:
				diff = [(student_score[i] - expert_scores[i])**(2) for i in range(len(expert_scores))]
			except:
				print(i)
			# print(diff)

			differences.append(diff)



		#for all differences, make an average

		average_differences = []
		for i in range(len(diff)):
			total_item_index = 0

			for j in range(len(differences)):
				total_item_index += differences[j][i]

			average_differences.append(total_item_index/len(differences))
			total_item_index = 0

		# print (average_differences)

		ret_val.append(average_differences)

	return ret_val


"""
Calls steps() for a certain lab and practice video
"""	

def handler():
	#########################
	# Basically Global vars #
	#########################
	labs = ["1", "2", "3", "4"]
	videoLabel = ["Practice 2"]
	

	###############
	#  Run Steps  #
	###############
	allLists = []
	for l in labs:
		for v in videoLabel:
			d = steps(minSizeGroup, maxSizeGroup, l, v)
			allLists.append(d)
			# print(d)



	# print(allLists)

	# Every group of size n is every lab at index n - minSizeGroup

	points = []


	for i in range(maxSizeGroup - minSizeGroup):

		#find average for every i (i --> group of size n)
		total = 0

		for j in range(len(allLists)):

			total += (sum(allLists[j][i])) ** (1/2)

		y_point = total / (5 * j)

		x_point = minSizeGroup + i

		points.append((x_point, y_point))

	x = []; y=[]
	for point in points:
		x.append(point[0])
		y.append(point[1])
	plt.scatter(x,y, color='red')
	plt.show()


	print (points)



"""
prints nicely
"""
def p(a, b):
	for i in range(len(a)):
		print('i:', i, round(a[i], 1), b[i])


"""
Retrieves expert ratings
"""
def get_expert_scores(lab, videoLabel):
	# q = "select itemIndex, score from expertEvaluations where labNumber in ({}) and videoLabel = 'Practice 2' ".format(labs)
	# q = "select itemIndex, score from expertEvaluations where labNumber = 1 and videoLabel = 'Practice 2' "
	q = "select itemIndex, score from expertEvaluations where labNumber = {} and videoLabel = '{}' ".format(lab, videoLabel)   



	evals = query(db, q)

	expert_scores = [None, None, None, None, None,]

	for e in evals:
		itemIndex = e[0] - 1
		score = e[1]
		expert_scores[itemIndex] = score

	return expert_scores




"""
Takes in group of students, their ratings, and weights 
to make a student score
"""
def math(g, prac_ratings, w):
	scores = []
	errors = []
	try:
		for i in range(1,6):

			denominator = 0
			numerator = 0

			for wid in prac_ratings.keys():
				offset = w[wid]['weightOffset'][i]
				bibi = w[wid]['weightBIBI'][i]
				if (bibi == 0):
					errors.append(wid)
				numerator += ((prac_ratings[wid][i] - offset) * bibi)
				denominator += bibi

			if denominator:
				score = numerator / denominator
			scores.append(score)

		return scores
	except:
		# print(errors)
		print("Failure, score or weight might be null")
		return None


"""
Return practice ratings of each student as dictionary
"""
def practice_video_x(g, lab, videoLabel):

	d = {}

	wIDs = makeWIDS(g)
	# q = "select wID, itemIndex, score from studentEvaluations where videoLabel = 'Practice 2' and labNumber in ({}) and wID in ({})".format(labs, wIDs)
	# q = "select wID, itemIndex, score from studentEvaluations where videoLabel = 'Practice 2' and labNumber = 1 and wID in ({})".format(wIDs)
	q = "select wID, itemIndex, score from studentEvaluations where videoLabel = '{}' and labNumber = {} and wID in ({})".format(videoLabel, lab, wIDs)



	all_ratings = query(db, q)

	for item in all_ratings:
		wID = item[0]
		itemIndex = item[1]

		if wID not in d:
			d[wID] = [None, None, None, None, None, None]

		d[wID][itemIndex] = item[2]
	
	return d


"""
Return Weights of each student as dictionary
"""
def weights(students, lab):
	d = {}
	wIDs = makeWIDS(students)
	
	# q = "select wID, itemIndex, weightType, weight from weights where labNumber in ({}) and wID in ({})".format(labs, wIDs)
	# q = "select wID, itemIndex, weightType, weight from weights where labNumber = 1 and wID in ({})".format(wIDs)
	q = "select wID, itemIndex, weightType, weight from weights where labNumber = {} and wID in ({})".format(lab, wIDs)



	all_weights = query(db, q)

	for item in all_weights:
		wID = item[0]
		weightType = item[2]
		itemIndex = item[1]

		if wID not in d:
			d[wID] = {'weightBIBI': [None, None, None, None, None, None], 'weightOffset':[None, None, None, None, None, None]}

		d[wID][weightType][itemIndex] = item[3]
	
	return d


"""
Returns a string of wIDS formatted for SQLite
"""
def makeWIDS(students):
	string = ""
	for s in students:
		string += "'" + s + "'" + ", "
	return string[:-2]


"""
Return a random set of size n
"""
def groups(n, set):
	if n > len(set):
		print (len(set))
	return random.sample(set, n)


"""
Return a set of all student wIDs
"""
def get_all_students(lab, videoLabel):
	# q = "select wID from submissions where labNumber = 1"

	# q = "select distinct wID from studentEvaluations where labNumber = 1 and score is not null and videoLabel = 'Practice 2'"
	q = "select distinct wID from studentEvaluations where labNumber = {} and score is not null and videoLabel = '{}' ".format(lab, videoLabel)

	# q2 = "select distinct wID from studentEvaluations where rating is null and labNumber = 1 and videoLabel = 'Practice 2' "
	q2 = "select distinct wID from studentEvaluations where rating is null and labNumber = {} and videoLabel = '{}' ".format(lab, videoLabel)
	

	ass = query(db, q)
	ass2 = query(db, q2)

	s = set()
	[s.add(student[0]) for student in ass]

	s2 = set()
	[s2.add(student[0]) for student in ass2]

	s = s - s2

	return s

"""
Query database db with query
"""
def query(db, query):
	curr = db.cursor()
	curr.execute(query)
	db.commit()
	return curr


if __name__ == '__main__':
    handler()




