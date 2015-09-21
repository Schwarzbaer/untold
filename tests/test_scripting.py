from tests.util import run_through_story

def test_case_node():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'autoact': {'case': [{'cond': False,
                                                            'set': {'var': 'foo',
                                                                    'val': {'const': False}},
                                                            'goto': 'end'},
                                                           {'cond': True,
                                                            'set': {'var': 'foo',
                                                                    'val': {'const': True}},
                                                            'goto': 'end'}]}}},
                           {'id': 'end',
                            'special': 'exit'}]}
    s = run_through_story(story_doc)
    assert s.get_state_var('foo')

def test_if_node_1():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'case': [{'if': False,
                                      'cond': True,
                                      'scene': {'autoact': {'set': {'var': 'foo',
                                                                    'val': {'const': False}},
                                                            'goto': 'end'}}},
                                     {'if': True,
                                      'cond': True,
                                      'scene': {'autoact': {'set': {'var': 'foo',
                                                                    'val': {'const': True}},
                                                            'goto': 'end'}}}]},
                           {'id': 'end',
                            'special': 'exit'}]}
    s = run_through_story(story_doc)
    assert s.get_state_var('foo')

def test_if_node_2():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'autoact': {'case': [{'if': False,
                                                            'cond': True,
                                                            'set': {'var': 'foo',
                                                                    'val': {'const': False}},
                                                            'goto': 'end'},
                                                           {'if': True,
                                                            'cond': True,
                                                            'set': {'var': 'foo',
                                                                    'val': {'const': True}},
                                                            'goto': 'end'}]}}},
                           {'id': 'end',
                            'special': 'exit'}]}
    s = run_through_story(story_doc)
    assert s.get_state_var('foo')

def test_choice_node_1():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'autoact': {'choice': [{'set': {'var': 'foo',
                                                                      'val': {'const': 'A'}},
                                                              'goto': 'end'},
                                                             {'set': {'var': 'foo',
                                                                      'val': {'const': 'B'}},
                                                              'goto': 'end'}]}}},
                           {'id': 'end',
                            'special': 'exit'}]}
    A, B = 0, 0
    for _ in range(1000):
        s = run_through_story(story_doc)
        choice = s.get_state_var('foo')
        if choice == 'A':
            A += 1
        else:
            B += 1
    assert 300<A<700 and 300<B<700

def test_choice_node_2():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'autoact': {'choice': [{'weight': 1,
                                                              'set': {'var': 'foo',
                                                                      'val': {'const': 'A'}},
                                                              'goto': 'end'},
                                                             {'weight': 9,
                                                              'set': {'var': 'foo',
                                                                      'val': {'const': 'B'}},
                                                              'goto': 'end'}]}}},
                           {'id': 'end',
                            'special': 'exit'}]}
    A, B = 0, 0
    for _ in range(1000):
        s = run_through_story(story_doc)
        choice = s.get_state_var('foo')
        if choice == 'A':
            A += 1
        else:
            B += 1
    assert 50<A<150 and 700<B<1001

# FIXME: There's a n infinite-loop-bug here.
# FIXME: It also lacks an actual, intended loop to check that the coice is fixed.
#def test_choice_f_node():
#    story_doc = {'start_node': 'start',
#                 'story': [{'id': 'start',
#                            'scene': {'autoact': {'choice-f': [{'weight': 1,
#                                                                'set': {'var': 'foo',
#                                                                        'val': {'const': 'A'}},
#                                                                'goto': 'end'},
#                                                               {'weight': 9,
#                                                                'set': {'var': 'foo',
#                                                                        'val': {'const': 'B'}},
#                                                                'goto': 'end'}]}}},
#                             {'id': 'end',
#                              'special': 'exit'}]}
#    A, B = 0, 0
#    for _ in range(1000):
#        s = run_through_story(story_doc)
#        choice = s.get_state_var('foo')
#        if choice == 'A':
#            A += 1
#        else:
#            B += 1
#    assert 50<A<150 and 700<B<1001
