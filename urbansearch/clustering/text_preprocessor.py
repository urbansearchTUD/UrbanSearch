# Tokenizes, Stems, removes stop words and counts

import re
from collections import Counter

from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize


class PreProcessor:
    def __init__(self, lang='dutch'):
        self.lang = lang
        self.stemmer = None

    def pre_process(self, text):
        """
        stripping, tokenizing, stemming and counting
        :param text: String
        :return: Dictionary
        """
        text = self.strip_punctuations(text)  # expects string
        text = self.tokenize(text)  # transfers to array
        text = self.stem(text)  # Do this before stripping ('Het' vs 'het')
        text = self.strip_words(text)  # expects array
        text = self.count(text)
        return text

    def stem(self, text):
        """
        Stems all the words in the text
        :param text: String list
        :return: String list
        """
        if not self.stemmer:
            self.stemmer = SnowballStemmer(self.lang)

        return [self.stemmer.stem(w) for w in text]

    def strip_words(self, text):
        """
        removes all stop words
        :param text: String list
        :return: String list
        """
        return [word for word in text if
                word not in stopwords.words(self.lang)]

    @staticmethod
    def strip_punctuations(text):
        """
        removes everything except letters and spaces
        :param text: String
        :return: String
        """
        return re.sub('[^\w\s]|_/g', '', text)

    @staticmethod
    def tokenize(text):
        """
        splits the String in a list of tokens (consisting of all words)
        :param text: String
        :return: String list
        """
        return word_tokenize(text)

    @staticmethod
    def count(text):
        """
        counts how many times each words is present
        :param text: String list
        :return: dictionary
        """
        return Counter(w.title() for w in text)
