from urbansearch.utils import score_utils


def test_gravity_score_diff():
    score_high = score_utils.gravity_model_score('Amsterdam', 'Rotterdam')
    score_low = score_utils.gravity_model_score('Appingedam', 'Rotterdam')
    assert score_low < score_high


def test_gravity_score_small_diff():
    score_high = score_utils.gravity_model_score('Den Haag', 'Rotterdam')
    score_low = score_utils.gravity_model_score('Amsterdam', 'Rotterdam')
    assert score_low < score_high


def test_gravity_score_eq():
    score_ab = score_utils.gravity_model_score('Rotterdam', 'Amsterdam')
    score_ba = score_utils.gravity_model_score('Amsterdam', 'Rotterdam')
    assert score_ab == score_ba
