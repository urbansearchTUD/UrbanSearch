import config
import os
from gensim import corpora, models

from decorators import list_required

CORPUS_DIRECTORY = config.get('resources', 'corpus')
DICTIONARY_DIRECTORY = config.get('resources', 'dictionaries')
MODELS_DIRECTORY = config.get('resources', 'models')


class ModelManager(object):
    """
    Base class for model specific manager objects.
    Combines dictionary, corpus and (un)trained model to one functional class.
    """

    def __init__(self, name, texts=None, load=False):
        """
        TODO: documentation
        """
        self.name = name
        self.corpus = []
        self.dictionary = corpora.Dictionary()
        self.NUM_OF_TOPICS = 20

        if texts:
            self.extend_dictionary(texts, multiple=True)


    @list_required
    def doc_to_bow(self, doc):
        """
        TODO: documentation
        """
        return self.dictionary.doc2bow(doc)

    @list_required
    def docs_to_bow(self, docs):
        """
        TODO: documentation
        """
        return [self.doc_to_bow(doc) for doc in docs]

    @list_required
    def extend_corpus(self, doc):
        """
        TODO: documentation
        """
        corpus = self.corpus
        corpus.append(doc)
        return corpus

    @list_required
    def extend_dictionary(self, doc, multiple=False):
        """
        TODO: documentation
        """
        if multiple:
            for text in doc:
                self.extend_corpus(self.dictionary.doc2bow(text,
                                                           allow_update=True))
        else:
            self.extend_corpus(self.dictionary.doc2bow(doc, allow_update=True))

    @list_required
    def extract_lda(self, doc):
        """
        TODO: documentation
        """
        if self.lda_model:
            return self.lda_model[self.doc_to_bow(doc)]

    def init_lda_model(self):
        """
        TODO: documentation and add functionality for LDA if desired
        """
        self.lda_model = models.LdaMulticore(self.corpus,
                                             num_topics=self.NUM_OF_TOPICS)

    def load(self):
        """
        TODO: documentation and add functionality for LDA if desired
        """
        try:
            print('laden')
            self.corpus = self.load_corpus(os.path.join(CORPUS_DIRECTORY, self.name + '.mm'))
            self.dictionary = self.load_dictionary(os.path.join(DICTIONARY_DIRECTORY, self.name + '.txt'))
            print('laden klaar')
        except:
            raise Exception('No such file found; <Category> : ' + self.category)

    def load_corpus(self, filename):
        """
        TODO: documentation
        """
        return corpora.MmCorpus(filename)

    def load_dictionary(self, filename):
        """
        TODO: documentation
        """
        return self.dictionary.load(filename)

    def load_lda(self, filename):
        """
        TODO: documentation
        """
        self.lda_model.load(filename)

    def save(self):
        self.save_dictionary(os.path.join(DICTIONARY_DIRECTORY, self.name + '.txt'))
        self.save_corpus(os.path.join(CORPUS_DIRECTORY, self.name + '.mm'))

    def save_corpus(self, filename):
        """
        TODO: documentation
        """
        corpora.MmCorpus.serialize(filename, self.corpus)

    def save_dictionary(self, filename):
        """
        TODO: documentation
        """
        self.dictionary.save(filename)

    def save_lda(self, filename):
        """
        TODO: documentation
        """
        self.lda_model.save(filename)

    # def update_corpus(self, corpus):
    #     """
    #     TODO: documentation
    #     """
    #     self.corpus = corpus
    #     self.update_tfidf_model(corpus)
