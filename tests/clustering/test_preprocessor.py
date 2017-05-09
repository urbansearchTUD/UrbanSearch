from urbansearch.clustering import preprocessing
p = preprocessing.PreProcessor()


def test_stem():
    text = ["handel", "bemoederen", "koe"]
    expected = ["handel", "bemoeder", "koe"]
    result = p.stem(text)
    for w in result:
        print(w)
    assert (result == expected)


def test_strip():
    text = "de, het. verantwoord"
    expected = ["verantwoord"]
    result = p.strip_punctuations(text)
    result = p.tokenize(result)
    result = p.strip_words(result)
    assert (result == expected)


def test_tokenize():
    text = "een twee drie"
    expected = ["een", "twee", "drie"]
    result = p.tokenize(text)
    assert (result == expected)


def test_count():
    text = ["drie", "drie", "drie", "een", "twee", "twee"]
    expected = {'Drie': 3, 'Twee': 2, 'Een': 1}
    result = p.count(text)
    assert (result == expected)


def test_text_file():
    file_object = open("tests/resources/test.txt", "r")
    text = file_object.read()
    words = p.pre_process(text)
    print(words)
    assert 1 == 1
    file_object.close()
