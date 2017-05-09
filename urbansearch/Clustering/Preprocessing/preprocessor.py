#Tokenizes, Stems, removes stop words and counts

import re

from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from collections import Counter

class PreProcessor:
    def __init__(self, lang='dutch'):
        self.lang = lang
        self.stemmer = SnowballStemmer(self.lang)

    def preProcess(self, text):
        text = self.stripPunctuations(text) #expects string
        text = self.tokenize(text) #transfers to array
        text = self.stem(text) #Do this before stripping ('Het' is not removed, 'het' is)
        text = self.stripWords(text) #expects array
        text = self.count(text)
        return text

    def stem(self, text):
        list = []
        for w in text:
            w = self.stemmer.stem(w)
            list.append(w)
        return list

    def stripWords(self, text):
        return [word for word in text if (word not in stopwords.words(self.lang))]

    def stripPunctuations(self, text):
        return re.sub('[^\w\s]|_/g', '', text)

    def tokenize(self, text):
        return word_tokenize(text)

    def count(self, text):
        return Counter(w.title() for w in text)
