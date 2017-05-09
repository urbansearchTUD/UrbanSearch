# Tokenizes, Stems, removes stop words and counts

import re

from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from collections import Counter


class PreProcessor:
    def __init__(self, lang='dutch'):
        self.lang = lang
        self.stemmer = SnowballStemmer(self.lang)

    def pre_process(self, text):
        text = self.strip_punctuations(text)  # expects string
        text = self.tokenize(text)  # transfers to array
        text = self.stem(text)  # Do this before stripping ('Het' vs 'het')
        text = self.strip_words(text)  # expects array
        text = self.count(text)
        return text

    def stem(self, text):
        list = []
        for w in text:
            w = self.stemmer.stem(w)
            list.append(w)
        return list

    def strip_words(self, text):
        return [word for word in text if
                word not in stopwords.words(self.lang)]

    def strip_punctuations(self, text):
        return re.sub('[^\w\s]|_/g', '', text)

    def tokenize(self, text):
        return word_tokenize(text)

    def count(self, text):
        return Counter(w.title() for w in text)
