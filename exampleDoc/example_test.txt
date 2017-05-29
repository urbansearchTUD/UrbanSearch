import importname

from exampleDoc import example_functional

exClass = example_functional.ExClass(bar=something)
exClass2 = example_functional.ExClass2(bar=something)


def test_environment_function():
    foo = inputdata
    bar = inputdata2
    output = expect_output_data
    assert output == example_functional.environment_function(foo, bar)


def test_exClass_class_function():
    foo = inputdata
    bar = inputdata2
    output = expect_output_data
    assert output == exClass.class_function(foo, bar)


def test_exClass_class_function2():
    foo = inputdata
    bar = inputdata2
    output = expect_output_data
    assert output == exClass.class_function2(foo, bar)


def test_exClass2_class_function():
    foo = inputdata
    bar = inputdata2
    output = expect_output_data
    assert output == exClass.class_function(foo, bar)


def test_exClass_class_function1():
    foo = inputdata
    bar = inputdata2
    output = expect_output_data
    assert output == exClass2.class_function2(foo, bar)
