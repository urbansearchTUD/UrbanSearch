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
        self.lsi_model = None

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
                self.extend_corpus(self.dictionary.doc2bow(text, allow_update=True))
        else:
            self.extend_corpus(self.dictionary.doc2bow(doc, allow_update=True))


    @list_required
    def extract_tfidf(doc):
        """
        TODO: documentation
        """
        if self.tfidf_model:
            return self.tfidf_model[self.doc_to_corpus(doc)]

    @list_required
    def extract_lsi(doc):
        """
        TODO: documentation
        """
        if self.lsi_model:
            return self.lsi_model[self.doc_to_corpus(doc)]

    def init_tfidf_model(self):
        """
        TODO: documentation
        """
        if self.corpus and not self.tfidf_model:
            self.tfidf_model = models.TfidfModel(self.corpus)

        return self.tfidf_model

    def init_lda_model(self):
        """
        TODO: documentation and add functionality for LDA if desired
        """
        pass

    def init_lsi_model(self):
        """
        TODO: documentation
        """
        if self.corpus and not self.lsi_model:
            self.lsi_model = models.LsiModel(corpus_tfidf,
                                             id2word=self.dictionary,
                                             num_topics=20)

        return self.lsi_model

    def load_dictionary(self):
        """
        TODO: documentation
        """
        pass

    def update_corpus(self, corpus):
        """
        TODO: documentation
        """
        self.corpus = corpus
        self.update_tfidf_model(corpus)
        self.update_lsi_model(corpus)

    def update_tfidf_model(self, corpus):
        """
        TODO: documentation
        """
        self.tfidf_model = models.TfidfModel(corpus)

    def update_lsi_model(self, corpus):
        """
        TODO: documentation
        """
        self.lsi_model = models.LsiModel(corpus)