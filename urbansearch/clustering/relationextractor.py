from gensim import corpora, models
from .decorators import list_required


class RelationExtractor(object):
    def __init__(self, texts=None):
        """
        TODO: documentation
        """
        self.corpus = []
        self.dictionary = corpora.Dictionary()
        self.tfidf_model = None
        self.lda_model = None
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
    def extract_tfidf(self, doc):
        """
        TODO: documentation
        """
        if self.tfidf_model:
            return self.tfidf_model[self.doc_to_bow(doc)]

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

    def init_tfidf_model(self):
        """
        TODO: documentation
        """
        if self.corpus and not self.tfidf_model:
            self.tfidf_model = models.TfidfModel(self.corpus)

        return self.tfidf_model

    def load_corpus(self, filename):
        """
        TODO: documentation
        """
        corpora.MmCorpus(filename)

    def load_dictionary(self, filename):
        """
        TODO: documentation
        """
        self.dictionary.load(filename)

    def load_lda(self, filename):
        """
        TODO: documentation
        """
        self.lda_model.load(filename)

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

    def update_tfidf_model(self, corpus):
        """
        TODO: documentation
        """
        self.tfidf_model = models.TfidfModel(corpus)
