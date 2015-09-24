from untold.story import eval_expression
from tests.util import run_through_story

def test_const_1():
    cond_node = {'op': 'const',
                 'var': True}
    state = {}
    assert eval_expression(cond_node, state)

def test_const_2():
    cond_node = {'op': 'const',
                 'var': False}
    state = {}
    assert not eval_expression(cond_node, state)

def test_const_3():
    cond_node = {'op': 'const',
                 'var': 'foo'}
    state = {}
    assert eval_expression(cond_node, state) == 'foo'

def test_const_4():
    cond_node = {'op': 'const',
                 'var': 1}
    state = {}
    assert eval_expression(cond_node, state) == 1

def test_var_1():
    cond_node = {'op': 'get',
                 'var': 'foo'}
    state = {'foo': 1}
    assert eval_expression(cond_node, state) == 1

def test_op_eq_1():
    cond_node = {'op': '==',
                 'varl': {'op': 'get',
                          'var': 'foo'},
                 'varr': 23}
    state = {'foo': 23}
    assert eval_expression(cond_node, state)

def test_op_eq_2():
    cond_node = {'op': '==',
                 'varl': {'op': 'get',
                          'var': 'foo'},
                 'varr': {'op': 'const',
                          'var': 23}}
    state = {'foo': 23}
    assert eval_expression(cond_node, state)

# Absence 1
def test_op_eq_3():
    cond_node = {'op': '==',
                 'varl': {'op': 'get',
                          'var': 'foo'},
                 'varr': {'op': 'const',
                          'var': None}}
    state = {}
    assert eval_expression(cond_node, state)

# Absence 2
def test_op_eq_4():
    cond_node = {'op': '==',
                 'varl': {'op': 'get',
                          'var': 'foo'},
                 'varr': None}
    state = {}
    assert eval_expression(cond_node, state)

def test_op_eq_5():
    cond_node = {'op': '==',
                 'varl': {'op': 'get',
                          'var': 'foo'},
                 'varr': {'op': 'const',
                          'var': None}}
    state = {'foo': 23}
    assert not eval_expression(cond_node, state)

# (foo == True) == (bar == False)
def test_nesting_1():
    cond_node= {'op': '==',
                'varl': {'op': '==',
                         'varl': {'op': 'get',
                                  'var': 'foo'},
                         'varr': {'op': 'const',
                                  'var': True}},
                'varr': {'op': '==',
                         'varl': {'op': 'get',
                                  'var': 'bar'},
                         'varr': {'op': 'const',
                                  'var': False}}}
    state = {'foo': True,
             'bar': False}
    assert eval_expression(cond_node, state)

def test_nesting_2():
    cond_node= {'op': '==',
                'varl': {'op': '==',
                         'varl': {'op': 'get',
                                  'var': 'foo'},
                         'varr': {'op': 'const',
                                  'var': True}},
                'varr': {'op': '==',
                         'varl': {'op': 'get',
                                  'var': 'bar'},
                         'varr': {'op': 'const',
                                  'var': False}}}
    state = {'foo': False,
             'bar': True}
    assert eval_expression(cond_node, state)

def test_nesting_3():
    cond_node= {'op': '==',
                'varl': {'op': '==',
                         'varl': {'op': 'get',
                                  'var': 'foo'},
                         'varr': {'op': 'const',
                                  'var': True}},
                'varr': {'op': '==',
                         'varl': {'op': 'get',
                                  'var': 'bar'},
                         'varr': {'op': 'const',
                                  'var': False}}}
    state = {'foo': True,
             'bar': True}
    assert not eval_expression(cond_node, state)

def test_story_format_1():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'presentation': 'text',
                                      'autoact': {'set': {'var': 'foo',
                                                          'val': {'op': '==',
                                                                  'varl': 23,
                                                                  'varr': 23}},
                                                  'goto': 'end'}}},
                           {'id': 'end',
                            'special': 'exit'}]}
    s = run_through_story(story_doc)
    assert s.get_state_var('foo')
