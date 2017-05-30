from urbansearch.clustering import text_preprocessor

p = text_preprocessor.PreProcessor()


def test_strip_words():
    text = ['de', 'buik', 'van', 'Marko']
    expected = ['buik', 'Marko']
    assert expected == p.strip_words(text)


def test_strip_words_size():
    text = ['aa', 'bbb', 'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc']
    expected = ['bbb']
    assert p.strip_words(text) == expected


def test_clean_text():
    text = 'a, . cd ; f 23213'
    expected = 'a  cd  f '
    result = p.clean_text(text)
    assert result == expected


def test_tokenize():
    text = 'een twee drie'
    expected = ['een', 'twee', 'drie']
    assert expected == p.tokenize(text)


def test_full_preprocessing():
    text = 'Een is oke. Dit niet: twee, drie.'
    expected = ['oke', 'twee', 'drie']
    assert expected == p.pre_process_to_array(text)
