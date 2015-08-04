import praw
import pymongo
import datetime
import time
from pyquery import PyQuery
import requests
import threading

def getDb():
	return pymongo.MongoClient().classifier

stopwords = open("stopwords.txt", 'r').read().splitlines()

def scanNewQuestions():
	reddit = praw.Reddit("AskReddit Naive Bayes Classifier")
	submissions = reddit.get_subreddit('askreddit').get_new(limit=50)
	newSubmissions = []
	db = getDb()
	for submission in submissions:
		foundText = " ".join(''.join(ch for ch in word if ch.isalnum()) for word in submission.title.lower().split() if ''.join(ch for ch in word if ch.isalnum()) not in stopwords)
		subObj = {
			'title' : foundText,
			'created': datetime.datetime.utcfromtimestamp(submission.created_utc),
			'url': submission.url,
			'upvotes': submission.ups,
			'reddit_id': submission.id,
			'num_comments': submission.num_comments
		}
		# for word in foundText.split():
		# 	db.unique_words.update({'word' : word}, {'word' : word}, upsert=True)
		# 	db.unique_words.update({'word' : word}, {"$inc" : {"doc_freq" : 1}})
		#newSubmissions.append(subObj)
		#{"$in": [subObj['reddit_id'] for subObj in newSubmissions]}}
		db.new_submissions.update({'reddit_id': subObj['reddit_id']}, subObj, upsert=True)

def trainingSet():
	reddit = praw.Reddit("AskReddit Naive Bayes Classifier")
	submissions = reddit.get_subreddit('askreddit').get_top_from_hour(limit=50)
	hotSubmissions = []
	db = getDb()
	for submission in submissions:
		foundText = " ".join(''.join(ch for ch in word if ch.isalnum()) for word in submission.title.lower().split() if ''.join(ch for ch in word if ch.isalnum()) not in stopwords)
		subObj = {
			'title' : foundText,
			'created': datetime.datetime.utcfromtimestamp(submission.created_utc),
			'url': submission.url,
			'upvotes': submission.ups,
			'reddit_id': submission.id
		}
		equalSubmission = db.new_submissions.find_one({'reddit_id': subObj['reddit_id']})
		if equalSubmission != None:
			subObj['upvotes_after_one_hour'] = equalSubmission['upvotes']
			subObj['num_comments_after_one_hour'] = equalSubmission['num_comments']
		for word in foundText.split():
			db.unique_words.update({'word' : word}, {'word' : word}, upsert=True)
			db.unique_words.update({'word' : word}, {"$inc" : {"doc_freq" : 1}})
		#hotSubmissions.append(subObj)
		db.trainingSet.update({'reddit_id': subObj['reddit_id']}, subObj, upsert=True)

def scanFrontPage():
	reddit = praw.Reddit("AskReddit Naive Bayes Classifier")
	submissions = reddit.get_subreddit('askreddit').get_hot(limit=25)
	hotSubmissions = []
	db = getDb()
	for submission in submissions:
		foundText = " ".join(''.join(ch for ch in word if ch.isalnum()) for word in submission.title.lower().split() if ''.join(ch for ch in word if ch.isalnum()) not in stopwords)
		subObj = {
			'title' : foundText,
			'created': datetime.datetime.utcfromtimestamp(submission.created_utc),
			'url': submission.url,
			'upvotes': submission.ups,
			'reddit_id': submission.id
		}
		equalSubmission = db.new_submissions.find_one({'reddit_id': subObj['reddit_id']})
		if equalSubmission != None:
			subObj['upvotes_after_one_hour'] = equalSubmission['upvotes']
			subObj['num_comments_after_one_hour'] = equalSubmission['num_comments']
		# for word in foundText.split():
		# 	db.unique_words.update({'word' : word}, {'word' : word}, upsert=True)
		# 	db.unique_words.update({'word' : word}, {"$inc" : {"doc_freq" : 1}})
		#hotSubmissions.append(subObj)
		db.frontPage.update({'reddit_id': subObj['reddit_id']}, subObj, upsert=True)

def syncTraining():
	db = getDb()
	fpIds = [obj['reddit_id'] for obj in db.frontPage.find()]
	db.trainingSet.update({"reddit_id" : {"$in" : fpIds}}, {"$set" : {"hitFrontPage" : True}}, multi=True)


def monitorAndBuild():

	def scanNew():
		trainingSet()
		time.sleep(60)

	def scanFP():
		scanFrontPage()
		time.sleep(300)

	def sync():
		syncTraining()
		time.sleep(1000)

	t = threading.Thread(target=scanNew)
	#t.daemon = True
	t.start()

	s = threading.Thread(target=scanFP)
	#s.daemon = True
	s.start()

	u = threading.Thread(target=sync)
	#u.daemon = True
	u.start()

if __name__ == "__main__":
	monitorAndBuild()




