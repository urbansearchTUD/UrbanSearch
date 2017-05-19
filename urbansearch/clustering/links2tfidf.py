import config
import os
from link2doc import Link2Doc
from relationextractor import RelationExtractor

CATEGORY_LINKS_DIRECTORY = config.get('resources', 'category_links')
MODELS_DIRECTORY = config.get('resources', 'models')


class Links2Tfidf(object):
	"""
	Links2Tfidf class. Expects a filename containing links
	that are collected by the CategoryLinksCollector. Requests the
	links and creates a TF-IDF model based on the contents of these
	documents
	"""

	def __init__(self, filename):
		"""
		Class constructor

		:param filename: The filename of the document containing the links associated to a category
		"""
		self.filename = os.path.join(CATEGORY_LINKS_DIRECTORY, filename)
		self.rex = RelationExtractor()

	def createModel(self):
		"""
		Creates a TF-IDF model with the file supplied in the constructor

		:return: A TF-IDF model for the supplied links
		"""
		l2d = Link2Doc()

		with open(self.filename) as f:
			for line in f:
				print('********************')
				print(line)
				print('********************')
				doc = l2d.get_doc(line)
				self.rex.extend_dictionary(doc)

			# self.rex.init_tfidf_model()
			# self.rex.tfidf_model.save(self.filename)
