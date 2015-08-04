import pymongo
import datetime
import time
import gatherQuestions


class NaiveBayes(object):
	
	def __init__(self):
		self.db = self.getDb()
		self.unique_words = self.db.unique_words.find()
		self.dimensionality = len(self.unique_words)
		self.document_count = self.db.trainingSetPostives.count() + self.db.trainingSetNegatives.count()

	def getDb(self):
		return gatherQuestions.getDb()#pymongo.MongoClient().classifier

	def getUniqueWords(self):
		return list(set([obj['word'] for obj in getDb().unique_words.find()]))

	def 