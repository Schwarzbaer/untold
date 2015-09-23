from tests.util import run_through_story

def test_case_node():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'autoact': {'case': [{'cond': False,
                                                            'set': {'var': 'foo',
                                                                    'val': {'op':'const',
                                                                            'var': False}},
                                                            'goto': 'end'},
                                                           {'cond': True,
                                                            'set': {'var': 'foo',
                                                                    'val': {'op':'const',
                                                                            'var': True}},
                                                            'goto': 'end'}]}}},
                           {'id': 'end',
                            'special': 'exit'}]}
    s = run_through_story(story_doc)
    assert s.get_state_var('foo')

def test_if_node_1():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'case': [{'if': {'op': 'const',
                                             'var': False},
                                      'cond': {'op': 'const',
                                               'var': True},
                                      'scene': {'autoact': {'set': {'var': 'foo',
                                                                    'val': {'op': 'const',
                                                                            'var': True}},
                                                            'goto': 'end'}}},
                                     {'if': {'op': 'const',
                                             'var': True},
                                      'cond': {'op': 'const',
                                               'var': True},
                                      'scene': {'autoact': {'set': {'var': 'foo',
                                                                    'val': {'op': 'const',
                                                                            'var': True}},
                                                            'goto': 'end'}}}]},
                           {'id': 'end',
                            'special': 'exit'}]}
    s = run_through_story(story_doc)
    assert s.get_state_var('foo')

def test_if_node_2():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'autoact': {'case': [{'if': {'op': 'const',
                                                                   'var': False},
                                                            'cond': {'op': 'const',
                                                                     'var': True},
                                                            'set': {'var': 'foo',
                                                                    'val': {'op': 'const',
                                                                            'var': False}},
                                                            'goto': 'end'},
                                                           {'if': {'op': 'const',
                                                                   'var': True},
                                                            'cond': {'op': 'const',
                                                                     'var': True},
                                                            'set': {'var': 'foo',
                                                                    'val': {'op': 'const',
                                                                            'var': True}},
                                                            'goto': 'end'}]}}},
                           {'id': 'end',
                            'special': 'exit'}]}
    s = run_through_story(story_doc)
    assert s.get_state_var('foo')

def test_choice_node_1():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'autoact': {'choice': [{'set': {'var': 'foo',
                                                                      'val': {'op': 'const',
                                                                              'var': 'A'}},
                                                              'goto': 'end'},
                                                             {'set': {'var': 'foo',
                                                                      'val': {'op': 'const',
                                                                              'var': 'B'}},
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
                                                                      'val': {'op': 'const',
                                                                              'var': 'A'}},
                                                              'goto': 'end'},
                                                             {'weight': 9,
                                                              'set': {'var': 'foo',
                                                                      'val': {'op': 'const',
                                                                              'var': 'B'}},
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

def test_choice_f_node():
    story_doc = {'start_node': 'start',
                 'story': [{'id': 'start',
                            'scene': {'autoact': {'set': [{'var': 'A',
                                                           'val': {'op': 'const',
                                                                   'var': 0},
                                                           },
                                                          {'var': 'B',
                                                           'val': {'op': 'const',
                                                                   'var': 0},
                                                           },
                                                          ],
                                                  'goto': 'loop'},
                                      },
                            },
                           {'id': 'loop',
                            'scene': {'autoact': {'case': [{'cond': {'op': 'or',
                                                                     'varl': {'op': '==',
                                                                              'varl': {'op': 'get',
                                                                                       'var': {'op': 'const',
                                                                                               'var': 'A'}},
                                                                              'varr': {'op': 'const',
                                                                                       'var': 100}},
                                                                     'varr': {'op': '==',
                                                                              'varl': {'op': 'get',
                                                                                       'var': {'op': 'const',
                                                                                               'var': 'B'}},
                                                                              'varr': {'op': 'const',
                                                                                       'var': 100}}},
                                                            'goto': 'end'},
                                                           {'cond': {'op': 'const',
                                                                     'var': True},
                                                            'goto': 'loop',
                                                            'choice-f': {'storage': '_stor',
                                                                         'choices': [{'weight': 1,
                                                                                      'set': {'var': 'A',
                                                                                              'val': {'op': '+',
                                                                                                      'varl': {'op': 'get',
                                                                                                               'var': {'op': 'const',
                                                                                                                       'var': 'A'}},
                                                                                                      'varr': {'op': 'const',
                                                                                                               'var': 1},
                                                                                                      },
                                                                                              },
                                                                                      },
                                                                                     {'weight': 9,
                                                                                      'set': {'var': 'B',
                                                                                              'val': {'op': '+',
                                                                                                      'varl': {'op': 'get',
                                                                                                               'var': {'op': 'const',
                                                                                                                       'var': 'B'}},
                                                                                                      'varr': {'op': 'const',
                                                                                                               'var': 1},
                                                                                                      },
                                                                                              },
                                                                                      }]
                                                                         } 
                                                            },
                                                           ],
                                                  }
                                      },
                            },
                           {'id': 'end',
                            'special': 'exit'}
                           ]
                 }
    A_test, B_test = 0, 0
    for _ in range(1000):
        s = run_through_story(story_doc)
        A = s.get_state_var('A')
        B = s.get_state_var('B')
        assert (A==100 and B==0) or (A==0 and B==100)
        if A==100:
            A_test += 1
        if B==100:
            B_test += 1
    print(A_test, B_test)
    assert 50<A_test<150 and 700<B_test<1001
