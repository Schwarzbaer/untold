#!/usr/bin/env python

def template_lookup(data_point, state):
    if 'text' in data_point.keys():
        return data_point['text']
    elif 'var' in data_point.keys():
        return state[data_point['var']]
    else:
        raise Exception # Malformed data point

def render(template, data, state):
    return template['text'] % tuple([template_lookup(data[param], state) for param in template['parameters']])

test_template = {'text': "This is %s, this is only %s, if this was %s they would have given us %s.",
                 'parameters': ['what_this_is', 'what_this_is', 'what_this_is_not', 'what_they_would_have_given_us_otherwise']}
test_data = {'what_this_is': {'text': 'a test'},
             'what_this_is_not': {'text': 'real life'},
             'what_they_would_have_given_us_otherwise': {'var': 'the_other_option'}}
test_state = {'the_other_option': 'instructions on where to go and what to do'}

if __name__ == '__main__':
    print(render(test_template, test_data, test_state))
