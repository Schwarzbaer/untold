#!/usr/bin/env python

def template_lookup(data_point, state):
    if 'text' in data_point.keys():
        return data_point['text']
    elif 'var' in data_point.keys():
        return state[data_point['var']]
    else:
        raise Exception # Malformed data point

def render(template, data, state, client = {}):
    return template['text'] % tuple([template_lookup(data[param], state) for param in template['parameters']])
