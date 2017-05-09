import re

class TermFrequency:

	def tfDoc(self, path):
		wordmap = {}

		try:
			with open(path) as doc:
				for line in doc:
					for word in line.split():
						word = word.lower()
						if not wordmap.get(word):
							wordmap[word] = 0

						wordmap[word] += 1

			return wordmap

		except:
			print('Document not found')

	def tfLine(self, line):
		pass
