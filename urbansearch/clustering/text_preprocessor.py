# Tokenizes, removes stop words

import re

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class PreProcessor:
    def __init__(self, lang='dutch'):
        self.lang = lang

    def pre_process(self, text):
        text = self.clean_text(text)

    def pre_process_to_array(self, text):
        """
        stripping and tokenizing
        :param text: String
        :return: Dictionary
        """
        text = self.clean_text(text)  # expects string
        text = self.tokenize(text)  # transfers to array
        text = self.strip_words(text)  # expects array
        return text

    def strip_words(self, text):
        """
        removes all stop words
        :param text: String list
        :return: String list
        """
        return [word for word in text if
                word not in stopwords.words(self.lang) and 2 < len(word) < 37]

    @staticmethod
    def clean_text(text):
        """
        removes everything except letters and spaces
        :param text: String
        :return: String
        """
        return re.sub('[^\w\s]|_|\d', '', text)

    def tokenize(self, text):
        """
        splits the String in a list of tokens (consisting of all words)
        :param text: String
        :return: String list
        """
        return word_tokenize(text.lower(), language=self.lang)
