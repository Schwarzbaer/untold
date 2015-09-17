from tests.util import run_through_story

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
