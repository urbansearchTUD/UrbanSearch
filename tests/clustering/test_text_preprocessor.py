from urbansearch.clustering import text_preprocessor

p = text_preprocessor.PreProcessor()


def test_stem():
    text = ['handelt', 'bemoederen', 'koe', 'vallen', 'valt', 'gymt']
    expected = ['handel', 'bemoeder', 'koe', 'val', 'val', 'gym']
    assert expected == p.stem(text)


def test_strip_words():
    text = ['de', 'buik', 'van', 'Marko']
    expected = ['buik', 'Marko']
    assert expected == p.strip_words(text)


def test_strip_punctuations():
    text = 'a, . cd ; f'
    expected = 'a  cd  f'
    result = p.strip_punctuations(text)
    assert result == expected


def test_tokenize():
    text = 'een twee drie'
    expected = ['een', 'twee', 'drie']
    assert expected == p.tokenize(text)


def test_count():
    text = ['drie', 'drie', 'drie', 'een', 'twee', 'twee']
    expected = {'Drie': 3, 'Twee': 2, 'Een': 1}
    assert expected == p.count(text)


def test_full():
    text = "Dit is een liedje: een, twee, drie, vier. " \
           "Hoedje van, hoedje van. Een, twee, drie, vier. Hoeden van papier"
    expected = {'Hoed': 3, 'Drie': 2, 'Twee': 2,
                'Vier': 2, 'Papier': 1, 'Lied': 1}
    assert expected == p.pre_process(text)


def test_stem_diminutives_standard():
    text = ['hoedjes', 'feetje', 'tafeltjes']
    expected = ['hoed', 'fee', 'tafel']
    assert expected == p.stem(text)


def test_stem_diminutives_exceptions():
    text = ['welletjes', 'innetjes', 'vieruurtjes']
    expected = ['welletjes', 'innetjes', 'vieruurtje']
    assert expected == p.stem(text)


def test_stem_diminutives_etjes():
    text = ['slangetje', 'vinnetje', 'leerlingetje']
    expected = ['slang', 'vin', 'leerling']
    assert expected == p.stem(text)


def test_stem_diminutives_inkjes():
    text = ['koninkje', 'plankje', 'vinkje']
    expected = ['koning', 'plank', 'ving']
    assert expected == p.stem(text)


def test_stem_double_consonents():
    text = ['hoedden', 'klanten', 'rijdt', 'lessen']
    expected = ['hoed', 'klant', 'rijd', 'les']
    assert expected == p.stem(text)


def test_stem_double_vowels():
    text = ['lopen', 'loop', 'keren', 'keer', 'maken', 'maak', 'vuren', 'vuur']
    # Since its more difficult to correct the
    # vowels, all double vowels are replaced by singles.
    expected = ['lop', 'lop', 'ker', 'ker', 'mak', 'mak', 'vur', 'vur']
    assert expected == p.stem(text)


def test_stem_changing_consonants():
    text = ['boffen', 'roven', 'vissen', 'glazen']
    expected = ['bof', 'rof', 'vis', 'glas']
    assert expected == p.stem(text)


def test_stem__dimmunative_pje():
    text = ['riempje', 'helmpje', 'museumpje']
    expected = ['riem', 'helm', 'museum']
    assert expected == p.stem(text)


def test_stem_end():
    text = ['groeiend', 'vermoeiend', 'verkopend']
    expected = ['groei', 'vermoei', 'verkop']
    assert expected == p.stem(text)


def test_stem_past_irregular():
    text = ['kocht', 'liep', 'mocht']
    expected = ['kocht', 'liep', 'mocht']
    assert expected == p.stem(text)


def test_stem_past_regular():
    text = ['deelde', 'werkten', 'smeedde', 'vergrootte']
    expected = ['deel', 'werk', 'smed', 'vergrot']
    assert expected == p.stem(text)
