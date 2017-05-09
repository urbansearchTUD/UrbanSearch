from .urbansearch.ml import termfrequency

def test_termfrequency():
    tf = termfrequency.TermFrequency()
    print(tf.tfDoc('bla.txt'))

    assert 1 == 1
