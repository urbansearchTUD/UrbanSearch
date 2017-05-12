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

rex = relationextractor.RelationExtractor()
rex_filled = relationextractor.RelationExtractor(texts)

def test_extend_dictionary():
    """
    TODO: add documentation
    """
    assert len(rex.dictionary.items()) == 0
    rex.extend_dictionary(texts[0])
    assert len(rex.dictionary.items()) == 3
    rex.extend_dictionary(texts[1])
    assert len(rex.dictionary.items()) == 8
    rex.extend_dictionary(texts[2])
    assert len(rex.dictionary.items()) == len(rex_filled.dictionary.items())

def test_extend_dictionary_multiple():
    """
    TODO: add documentation
    """
    assert len(rex.dictionary.items()) == 12
    rex.extend_dictionary(new_texts, multiple=True)
    assert len(rex.dictionary.items()) == 20

def test_doc_to_bow():
    """
    TODO: add documentation
    """
    dictionary = rex.dictionary.token2id
    doc_to_test = ['kaart', 'klink', 'beeldscherm']
    id_set = [dictionary['kaart'], dictionary['klink']]

    for bow in rex.doc_to_bow(doc_to_test):
        assert (bow[0] in id_set)
        assert bow[1] == 1

def test_docs_to_bow():
    """
    TODO: add documentation
    """
    docs_to_test = [
        ['kaart', 'klink', 'beeldscherm'],
        ['boekje', 'koptelefoon', 'gisteren']
    ]
    assert len(rex.docs_to_bow(docs_to_test)) == 2



#
# def test_extend
