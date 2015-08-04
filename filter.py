import pymongo
import datetime
import time

stopwords = open("stopwords.txt", 'r').read().splitlines()

def getDb():
	return pymongo.MongoClient().classifier

def filterData():
	db = getDb()
	all_top = db.hot_submissions.find()
	all_new = db.new_submissions.find()