#!/usr/bin/env python

# Node
# * id: id
# * 
#
# Story (Node)
# * story: Scene
# * actables: [Interactions]
# * autoact: {Consequences}
#
# Scene
# * text: textual description
#
# Consequences
# * set
#   * var: variable_name
#   * val: value
# * goto: Node.id
#
# Script
# * case
#   * cond
#     * Preconditions
#
# Interactions
# * text: textual description
# * result: Consequences
# * Script


import argparse
import json


test_story = {
 'author': 'TheCheapestPixels',
 'title': 'Test case',
 'start_node': 'start',
 'story': [{'id': 'start',
            'case': [{'cond': True,
                      'scene': {'text': 'Testing boolean node'},
                      'autoact': {'goto': 'test_2'},},],},
           {'id': 'test_2',
            'case': [{'cond': {'op': '==',
                               'varl': {'var': 'var1'},
                               'varr': None},
                      'scene': {'text': 'Testing var for absence'},
                      'autoact': {'goto': 'test_3',
                                  'set': {'var': 'var1',
                                          'val': 1},},},],},
           {'id': 'test_3',
            'case': [{'cond': {'op': '==',
                               'varl': {'var': 'var1'},
                               'varr': 1},
                      'scene': {'text': 'Testing var for value'},
                      'autoact': {'goto': 'test_4',},},],},
           {'id': 'test_4',
            'scene': {'case': [{'cond': {'op': '==',
                                         'varl': {'var': 'var1'},
                                         'varr': 1},
                                'text': 'Testing case-in-scene/autoact.'},
                               {'cond': True,
                                'text': 'case-in-scene/autoact failed.'},],},
            'autoact': {'case': [{'cond': {'op': '==',
                                           'varl': {'var': 'var1'},
                                           'varr': 1},
                                  'goto': 'unweighted_choice',},
                                 {'cond': True,
                                  'goto': 'broken',},],},},
           {'id': 'unweighted_choice',
            'scene': {'choice': [{'text': 'Unweighted choice chose foo'},
                                 {'text': 'Unweighted choice chose bar'},
                                 {'text': 'Unweighted choice chose baz'},],},
            'autoact': {'goto': 'weighted_choice'},},
           {'id': 'weighted_choice',
            'choice': [{'weight': 1,
                        'scene': {'text': 'Weighted choice chose foo'},
                        'autoact': {'goto': 'done'},},
                       {'weight': 2,
                        'scene': {'text': 'Weighted choice chose bar'},
                        'autoact': {'goto': 'done'},},
                       {'weight': 3,
                        'scene': {'text': 'Weighted choice chose baz'},
                        'autoact': {'goto': 'done'},},],},
           {'id': 'done',
            'special': 'exit',},],}


new_story_format_story = {
    'author': 'TheCheapestPixels',
    'title': 'Labyrinth of foobarbaz',
    'start_node': 'start',
    'story': [{'id': 'start',
               'scene': {'presentation': {'text': 'This is the anteroom. There are three doors.'},
                         'actables': [{'text': 'Door foo',
                                       'result': {'goto': 'foo'}},
                                      {'text': 'Door bar',
                                       'result': {'goto': 'bar'}},
                                      {'text': 'Door baz',
                                       'result': {'goto': 'baz'}},
                                      ]}},
              {'id': 'foo',
               'scene': {'presentation': {'text': 'This is room foo. There are three doors'},
                         'actables': [{'text': 'Door bar',
                                       'result': {'goto': 'bar'}},
                                      {'text': 'Door baz',
                                       'result': {'goto': 'baz'}},
                                      {'text': 'Door exit',
                                       'result': {'goto': 'exit'}},
                                      ]}},
              {'id': 'bar',
               'scene': {'presentation': {'text': 'This is room bar. There are three doors'},
                         'actables': [{'text': 'Door foo',
                                       'result': {'goto': 'foo'}},
                                      {'text': 'Door baz',
                                       'result': {'goto': 'baz'}},
                                      {'text': 'Door exit',
                                       'result': {'goto': 'exit'}},
                                      ]}},
              {'id': 'baz',
               'scene': {'presentation': {'text': 'This is room baz. There are three doors'},
                         'actables': [{'text': 'Door foo',
                                       'result': {'goto': 'foo'}},
                                      {'text': 'Door bar',
                                       'result': {'goto': 'bar'}},
                                      {'text': 'Door exit',
                                       'result': {'goto': 'exit'}},
                                      ]}},
              {'id': 'exit',
               'special': 'exit'}]}
#--------------------------------------------------------------------
choice_test_story = {'start_node': 'start',
                     'story': [{'id': 'start',
                                'scene': {'presentation': {'text': 'Start node'},
                                          'autoact': {'goto': 'loop',
                                                      'set': {'var': 'counter',
                                                              'val': 0,
                                                              },
                                                      },
                                          }
                                },
                               {'id': 'loop',
                                'scene': {'case': [{'cond': {'op': '==',
                                                             'varl': {'var': 'counter'},
                                                             'varr': 0,
                                                             },
                                                    'presentation': {'text': 'Loop node'},
                                                    'autoact': {'goto': 'loop',
                                                                'set': {'var': 'counter',
                                                                        'val': 5,
                                                                        },
                                                                },
                                                    },
                                                   {'cond': {'op': '==',
                                                             'varl': {'var': 'counter'},
                                                             'varr': 5,
                                                             },
                                                    'presentation': {'text': 'End of Loop node'},
                                                    'autoact': {'goto': 'exit'},
                                                    },
                                                   ],
                                          },
                                },
                               {'id': 'exit',
                                'special': 'exit',
                                }],
                     }
#--------------------------------------------------------------------

if __name__ == '__main__':
    stories = {
        'test': test_story,
        'newformat': new_story_format_story,
        'choicetest': choice_test_story,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'stories',
        type=str,
        nargs='+',
        help='Stories to write. At least one of: test, newformat, choicetest',
    )
    args = parser.parse_args()

    for story_name in args.stories:
        if story_name not in stories:
            print("\"{}\" is not a known story!".format(story_name))
            continue
        story = stories[story_name]
        f = open('{}.json'.format(story_name), 'w')
        f.write(json.dumps(story))
        f.write('\n')
        print("Wrote story \"{}\".".format(story_name))
        f.close()
