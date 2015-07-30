import praw
import pymongo
import datetime
import time

def getDb():
	return pymongo.MongoClient().classifier

def scanNewQuestions():
	reddit = praw.Reddit("AskReddit Naive Bayes Classifier")
	submissions = reddit.get_subreddit('askreddit').get_new(limit=500)
	newSubmissions = []
	db = getDb()
	for submission in submissions:
		subObj = {
			'title' : submission.title,
			'created': datetime.datetime.utcfromtimestamp(submission.created_utc),
			'url': submission.url,
			'upvotes': submission.ups,
			'reddit_id': submission.id
		}
		#newSubmissions.append(subObj)
		#{"$in": [subObj['reddit_id'] for subObj in newSubmissions]}}
		db.new_submissions.update({'reddit_id': subObj['reddit_id']}, subObj, upsert=True)

def scanFrontPage():
	reddit = praw.Reddit("AskReddit Naive Bayes Classifier")
	submissions = reddit.get_subreddit('askreddit').get_hot(limit=25)
	hotSubmissions = []
	db = getDb()
	for submission in submissions:
		subObj = {
			'title' : submission.title,
			'created': datetime.datetime.utcfromtimestamp(submission.created_utc),
			'url': submission.url,
			'upvotes': submission.ups,
			'reddit_id': submission.id
		}
		#hotSubmissions.append(subObj)
		db.hot_submissions.update({'reddit_id': subObj['reddit_id']}, subObj, upsert=True)

def periodicFPScan(pauseTimeInSeconds):
	while True:
		scanFrontPage()
		time.sleep(pauseTimeInSeconds)

def periodicNewScan(pauseTimeInSeconds):
	while True:
		scanNewQuestions()
		time.sleep(pauseTimeInSeconds)
