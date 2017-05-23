from . import db_utils


def gravity_model_score(city_a, city_b):
    """
    Calculates the relationship strength between two cities based
    on the gravity model, defined as:

    (populationA * populationB) / distanceAB^2

    :param city_a: The name of city A
    :param city_b: The name of city B
    :return: The strength of the relationship between city A and city B
    """
    pop_a = db_utils.city_population(city_a)
    pop_b = db_utils.city_population(city_b)
    dist = db_utils.city_haversine_distance(city_a, city_b)
    return (pop_a * pop_b) / dist ** 2
