<<<<<<< HEAD
=======
import os
<<<<<<< HEAD
=======
import time

from link2doc import Link2Doc
from relationextractor import RelationExtractor
from tfidfmodelmanager import TFIDFModelManager
>>>>>>> link collector

>>>>>>> link collector
import config
import os
from link2doc import Link2Doc
from relationextractor import RelationExtractor

MODELS_DIRECTORY = config.get('resources', 'models')

<<<<<<< HEAD
class Links2Tfidf(object):
	def __init__(self, filename):
		self.filename = os.path.join(MODELS_DIRECTORY, filename)
		self.rex = RelationExtractor()

	def createModel(self):
		l2d = Link2Doc()

		with open(self.filename) as f:
=======

class Links2TFIDF(object):
	"""
	Links2Tfidf class. Expects a filename containing links
	that are collected by the CategoryLinksCollector. Requests the
	links and creates a TF-IDF model based on the contents of these
	documents
	"""

	def __init__(self, category):
		"""
		Class constructor

		:param category: The category of the document containing the links
		"""
		self.category = category
		self.rex = RelationExtractor()
		self.tmm = TFIDFModelManager(category)

	def createModel(self):
		"""
		Creates a TF-IDF model with the file supplied in the constructor

		:return: A TF-IDF model built up using the vocabulary
		collected from the supplied links
		"""
		l2d = Link2Doc()

		with open(os.path.join(CATEGORY_LINKS_DIRECTORY,
							   self.category + '.txt')) as f:
>>>>>>> link collector
			for line in f:
				print('********************')
				print(line)
				print('********************')
				doc = l2d.get_doc(line)
<<<<<<< HEAD
				rex.extend_dictionary(doc)

			self.rex.init_tfidf_model()
			self.rex.save(self.filename)
=======
				start = time.time()
				self.tmm.extend_dictionary(doc)
				print("TIME TO EXTEND DICT + CORPUS:")
				end = time.time()
				print(end - start)

			# self.rex.init_tfidf_model()
			# self.rex.tfidf_model.save(os.path.join(MODELS_DIRECTORY,
			# 									   self.category + '.mm'))
			self.tmm.init_model()
			self.tmm.save()
>>>>>>> link collector
