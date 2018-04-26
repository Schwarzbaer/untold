from untold.story import eval_condition, Story, StoryExited
from .util import run_through_story
from numpy.testing.utils import assert_raises

# FIXME: These need some I/O checking, akin to a REPLL.

def test_minimal_story():
    story_doc = \
        {'start_node': 'start',
         'story': [{'id': 'start',
                    'special': 'exit'}]}
    s = run_through_story(story_doc)
    assert_raises(StoryExited)

def test_story_with_metadata():
    story_doc = \
        {'title': 'Example from the docs',
         'author': 'TheCheapestPixels',
         'start_node': 'start',
         'story': [{'id': 'start',
                    'special': 'exit'}]}
    s = run_through_story(story_doc)
    assert_raises(StoryExited)
