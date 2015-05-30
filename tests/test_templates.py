from template import template_lookup, render

def test_1():
    test_template = {'text': "This is %s, this is only %s, if this was %s they would have given us %s.",
                     'parameters': ['what_this_is', 'what_this_is', 'what_this_is_not', 'what_they_would_have_given_us_otherwise']}
    test_data = {'what_this_is': {'text': 'a test'},
                 'what_this_is_not': {'text': 'real life'},
                 'what_they_would_have_given_us_otherwise': {'var': 'the_other_option'}}
    test_state = {'the_other_option': 'instructions on where to go and what to do'}
    output = render(test_template, test_data, test_state)
    assert output == "This is a test, this is only a test, if this was real life they would have given us instructions on where to go and what to do."
