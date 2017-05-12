# Tokenizes, Stems, removes stop words and counts

import re
import config
from collections import Counter

from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer, DutchStemmer
from nltk.tokenize import word_tokenize

class EnhancedDutchStemmer(DutchStemmer):
    def __init__(self):
        super().__init__()
        self._double_consonants = (  # double consonants
                                   'bb', 'cc', 'dd', 'ff', 'gg', 'kk', 'll',
                                   'mm', 'nn', 'pp', 'rr', 'ss', 'tt', 'zz',
                                   # for -t verbs
                                   'bt', 'ct', 'dt', 'ft', 'gt', 'kt', 'lt',
                                   'mt', 'pt', 'rt', 'st', 'zt'
                                   # diminutives -je
                                   'aj', 'bj', 'cj', 'dj', 'ej', 'fj', 'gj',
                                   'hj', 'jj', 'kj', 'lj', 'mj', 'nj', 'pj',
                                   'qj', 'rj', 'sj', 'tj', 'uj', 'vj', 'wj',
                                   'xj', 'zj',
                                   # for diminutives -*dje, * being a consonant
                                   'bd', 'cd', 'dd', 'fd', 'gd', 'kd', 'ld',
                                   'md', 'nd', 'pd', 'rd', 'sd', 'zd')

    def stem_double_consonants(self, word):
        """
        The following is taken from step 4
        from the DanishStemmer class (also NLTK)
        It improves stems such as 'val' for verb 'vallen',
        which would otherwise be stemmed as 'vall'.
        This conflicts with third singular form 'valt',
        which would be stemmed to 'val'.
        In Dutch, there are many words behaving similarly.
        :param word: A word that may contain a double equal consonant
        :return: A word that does not have double consonants (**, *t, *j or *d)
        """
        for double_cons in self._double_consonants:
            if word.endswith(double_cons) and 3 < len(word):
                word = word[:-1]
                break
        return word

    def stem_diminutives(self, word):
        """
        Changes words from diminutive form to root form.
        :param word in a diminutive form (e.g. basje)
        :return: word in a root form (e.g. bas)
        """
        exceptions = ['welletjes', 'innetjes', 'sprookje',
                      'rotje', 'akkefietje', 'poffertje' 'vieruurtje']
        if word in exceptions:
            return word
        if word in ['poffertjes', 'vieruurtjes']:      # plural exception
            return word[:-1]

        # word ends with -etje(s)
        if word.endswith('etjes'):
            if word.endswith('eetjes'):
                return word[:-4]        # -tjes
            else:
                return word[:-5]        # -etjes
        if word.endswith('etje'):
            if word.endswith('eetje'):
                return word[:-3]        # -tje
            else:
                return word[:-4]        # -etje

        # word ends with '-inkje'
        # This proves difficult.
        # 62 words with ink, 2752 words with ing -> everything to ing
        if word.endswith('inkje'):
            word = word[:-3]
            return word + 'g'
        if word.endswith('inkjes'):
            word = word[:-4]
            return word + 'g'

        # word ends with pje(s)
        if word.endswith('pjes'):
            return word[:-4]
        if word.endswith('pje'):
            return word[:-3]

        # word ends with (t)je(s) and (t)je(s)
        if word.endswith('jes'):    # -t gets removed in double consonant step
            return word[:-3]
        if word.endswith('je'):
            return word[:-2]

        return word

    # method for past verbs?

    def stem_changed_consonant(self, word):
        """
        some words when changed to plural change consonants,
        this methods reverses that.
        :param word: word in plural form (e.g. beven)
        :return: word in root form (e.g. bef)
        """
        if len(word) > 4:
            if word.endswith('oven') or word.endswith('aven') \
                    or word.endswith('uven') or word.endswith('even'):
                word = word[:-3] + 'f'
        if len(word) > 4:
            if word.endswith('azen') or word.endswith('ozen') \
                    or word.endswith('uzen') or word.endswith('ezen'):
                word = word[:-3] + "s"
        return word

    def stem(self, word):
        """
        Stems Dutch words
        Included features:
        - classic snowball
        - double consonants (dt -> d)
        - verbs where consonants changed (blozen -> blos)
        - dimmunitives (slangetje -> slang)

        known errors:
        - words ending in kje that are derived from words
          ending in nk are changed to ng ('vinkje' -> 'ving').
        - double vowels are changed to single vowels ('gooi' -> 'goi').
        - irregular (strong) verbs in past tense

        :param word: The word to stem
        :return: The stemmed word
        """
        word = self.stem_double_consonants(word)
        word = self.stem_changed_consonant(word)

        if word.startswith('groei'):
            print(word)
        word2 = self.stem_diminutives(word)
        if word2 is word:
            word2 = DutchStemmer.stem(self, word)

        word2 = self.stem_double_consonants(word2)

        return word2


class PreProcessor:
    def __init__(self, lang='dutch'):
        self.lang = lang
        self.stemmer = None
        self.nltk_dir = config.get('resources', 'nltk')
        print(nltk)

    def _get_stemmer(self):
        if self.stemmer:
            return self.stemmer
        if self.lang == 'dutch':
            return EnhancedDutchStemmer()
        else:
            return SnowballStemmer(self.lang)

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
        return [self._get_stemmer().stem(w) for w in text]

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
