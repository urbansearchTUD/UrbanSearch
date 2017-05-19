from urbansearch.clustering import relationextractor

texts = [
    ['handelt', 'bemoederen', 'koe'],
    ['vallen', 'valt', 'zicht', 'gymt', 'breedte'],
    ['dromen', 'muis', 'bezorgen', 'zeeziek']
]

new_texts = [
    ['ajax', 'kampioen', 'bezorgen', 'europees', 'kampioen'],
    ['kaart', 'pet', 'lamp', 'klink', 'honkbalknuppel'],
]

rex_filled = relationextractor.RelationExtractor(texts)


def test_extend_dictionary():
    rex = relationextractor.RelationExtractor()
    assert len(rex.dictionary.items()) == 0
    rex.extend_dictionary(texts[0])
    assert len(rex.dictionary.items()) == 3
    rex.extend_dictionary(texts[1])
    assert len(rex.dictionary.items()) == 8
    rex.extend_dictionary(texts[2])
    assert len(rex.dictionary.items()) == len(rex_filled.dictionary.items())


def test_extend_dictionary_multiple():
    rex = relationextractor.RelationExtractor()
    assert len(rex.dictionary.items()) == 0
    rex.extend_dictionary(texts, multiple=True)
    assert len(rex.dictionary.items()) == 12
    rex.extend_dictionary(new_texts, multiple=True)
    assert len(rex.dictionary.items()) == 20


def test_doc_to_bow():
    rex = relationextractor.RelationExtractor()
    rex.extend_dictionary(texts, multiple=True)

    dictionary = rex.dictionary.token2id
    doc_to_test = ['koe', 'muis', 'beeldscherm']
    id_set = [dictionary['koe'], dictionary['muis']]

    for bow in rex.doc_to_bow(doc_to_test):
        assert (bow[0] in id_set)
        assert bow[1] == 1


def test_docs_to_bow():
    rex = relationextractor.RelationExtractor()
    docs_to_test = [
        ['kaart', 'klink', 'beeldscherm'],
        ['boekje', 'koptelefoon', 'gisteren']
    ]
    assert len(rex.docs_to_bow(docs_to_test)) == 2


def test_extend_corpus():
    rex = relationextractor.RelationExtractor()
    corpus_length = len(rex.corpus)
    rex.extend_corpus([])
    assert len(rex.corpus) == corpus_length + 1


def test_init_tfidf_model_no_corpus():
    rex = relationextractor.RelationExtractor()
    tfidf = rex.init_tfidf_model()
    assert tfidf is None


def test_init_tfidf_model():
    rex = relationextractor.RelationExtractor(texts)
    tfidf = rex.init_tfidf_model()
    assert tfidf is not None


def test_extract_tfidf():
    rex = relationextractor.RelationExtractor(texts)
    rex.init_tfidf_model()

    non_corpus_text = ['bla', 'blu', 'doggy']
    empty = rex.extract_tfidf(non_corpus_text)
    assert len(empty) == 0

    corpus_text = ['gym', 'zeeziek']
    non_empty = rex.extract_tfidf(corpus_text)
    assert len(corpus_text) == 2

    for score in non_empty:
        assert score[1] != 0


def test_update_tfidf():
    rex = relationextractor.RelationExtractor(texts)
    old_tfidf = rex.tfidf_model
    rex.update_tfidf_model([])
    assert old_tfidf != rex.tfidf_model
