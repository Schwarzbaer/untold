from untold.story import Story, StoryExited
from tests.util import run_through_story

def test_set_state_var_1():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'autoact': {'set': {'var': 'foo',
                                                          'val': 23},
                                                  'goto': 'end'}}},
                           {'id': 'end',
                            'special': 'exit'}]}
    s = Story(story_doc)
    s.start()
    while True:
        try:
            story_state = s.eval_current_node()
            s.enact(story_state['autoact'])
        except StoryExited:
            break
    assert s.get_state_var('foo') == 23

def test_set_state_var_2():
    # Using a condition as value for a set
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'autoact': {'set': {'var': 'foo',
                                                          'val': {'op': '==',
                                                                  'varl': 23,
                                                                  'varr': 23}},
                                                  'goto': 'end'}}},
                           {'id': 'end',
                            'special': 'exit'}]}
    s = run_through_story(story_doc)
    assert s.get_state_var('foo')
