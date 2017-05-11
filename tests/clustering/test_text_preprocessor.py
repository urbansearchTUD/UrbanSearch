from urbansearch.clustering import text_preprocessor
from unittest.mock import Mock

p = text_preprocessor.PreProcessor()
p.stemmer = Mock()
text_preprocessor.word_tokenize = Mock()
text_preprocessor.Counter = Mock()
text_preprocessor.stopwords = Mock()


def test_stem():
    """
    test the stemming method
    :return: 
    """
    text = ["handel", "bemoederen", "koe"]
    expected = ["handel", "bemoeder", "koe"]
    p.stem(text)
    p.stemmer.stem.assert_called()


def test_strip_words():
    """
    test the stripping words method
    :return: 
    """
    text_preprocessor.stopwords.words.return_value = ["het"]
    text = ["verantwoorden", "verantwoorde", "verantwoord"]
    p.strip_words(text)
    text_preprocessor.stopwords.words.assert_called()


def test_strip_punctuations():
    """
    test the stripping punctuations method
    :return: 
    """
    text = "a, . cd ; f"
    expected = "a  cd  f"
    result = p.strip_punctuations(text)
    assert(result == expected)


def test_tokenize():
    """
    test the tokenizing method
    :return: 
    """
    text = "een twee drie"
    expected = ["een", "twee", "drie"]
    result = p.tokenize(text)
    text_preprocessor.word_tokenize.assert_called()


def test_count():
    """
    test the counting method
    :return:
    """
    text = ["drie", "drie", "drie", "een", "twee", "twee"]
    expected = {'Drie': 3, 'Twee': 2, 'Een': 1}
    result = p.count(text)
    text_preprocessor.Counter.assert_called()


def test_pre_process():
    """
    test the combined methods
    :return: 
    """
    with open("tests/resources/test.txt", "r") as file_object:
        text_preprocessor.word_tokenize.return_value = ["a", "b", "c"]
        text_preprocessor.stopwords.words.return_value = ["het"]
        text = file_object.read()
        p.pre_process(text)

        text_preprocessor.word_tokenize.assert_called()
        p.stemmer.stem.assert_called()
        text_preprocessor.stopwords.words.assert_called()
        text_preprocessor.Counter.assert_called()
