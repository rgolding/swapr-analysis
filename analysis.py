"""
1. Get rating for every Calibration (including Hidden) video
2. Make dictionary for each video:
{
url -> { 'instructor' -> [ratings....], 'students'-> [ratings.....] }
} 
3. Get student's score?
"""

#####################################
####        Imports              ####
#####################################
import pymysql
import sqlite3
import statistics

######################################
####        Global DB            ####
####################################
hostname = 'localhost'
username = 'USERNAME'
password = 'PASSWORD'
database = 'db.sqlite'
db = sqlite3.connect(database)	


#####################################
#### Analyze: Controls Flow      ####
#####################################
def analyze():

	print("Analyzing")

	#connect to database
	db = sqlite3.connect(database)	

	#get video url, videolabel
	videos = getCalibrationVideos(db)
	#print (videos)
	#create dictionary
	expertDict = makeExpertDictionary(videos)

	#get student averages for each calibration
	studentEvals = studentEvaluationsCalibrations()

	#mean, median, mode of student evaluations
	studentStats = studentEvalCalStats(studentEvals)

	#compare student evals to expert evals
	comps = compare(studentStats, expertDict)

	print (comps)

	db.close()

def compare(d1, d2):
	comps = {}
	#for every student video ratings
	for video in d1.keys():
		key = video
		value = {}
		
		expertEval = d2[key]

		value['meanDiff'] = expertEval - d1[video][0]
		value['medianDiff'] = expertEval - d1[video][1]

		comps[key] = value
	
	return (comps)
		


"""
Calculates averages/median/mode from dictionary of videos
Returns new dictionary
"""
def studentEvalCalStats(d):
	newD = {}

	for video in d.keys():
		newD[video] = [statistics.mean(d[video])]
		newD[video].append(statistics.median(d[video]))

	return (newD)


"""
Returns dictionary:
{
	url + str(itemIndex): [all student ratings for url]
}
"""
def studentEvaluationsCalibrations():
	videos = getStudentCalibrationRatings()
	#print(videos)
	studentVideoAll = {}

	for video in videos:
		url = video[1]
		itemIndex = video[2]
		key = url + str(itemIndex)
		
		if key not in studentVideoAll.keys():
			value = [video[3]]
			studentVideoAll[key] = value
		else:
			studentVideoAll[key].append(video[3])

	return (studentVideoAll)


def getStudentCalibrationRatings():
	q = "select videoLabel, url, itemIndex, score from studentEvaluations where (videoLabel in ('Calibration 1')) and rating IS NOT NULL"
	ass = query(db, q)
	return (ass.fetchall())

def makeExpertDictionary(videos):
	i = 'instructor'
	s = 'student'
	d = {}
	for item in videos:
		key = item[1] + str(item[2])
		value = item[3]
		d[key] = value
			
	return d

def getCalibrationVideos(db):
	q = "select videoLabel, url, itemIndex, score from expertEvaluations where (videoLabel in ('Calibration 1'))"
	#q = "select videoLabel, url, itemIndex, rating from expertEvaluations where (videoLabel in ('Calibration 1', 'Calibration 2', 'Calibration 3'))"
	ass = query(db, q)
	return (ass.fetchall())

def query(db, query):
	curr = db.cursor()
	curr.execute(query)
	db.commit()
	return curr


if __name__ == '__main__':
    analyze()