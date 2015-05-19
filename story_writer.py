#!/usr/bin/env python

# Node
# * id: id
#
# Story (Node)
# * story: Scene
# * actable: [Interactions]
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
#     * preconditions


story = [
{'id': 'start',
 'story': {'text': 'As the clouds finally part, the sun reveals this mornings vibrant green of the rolling hills to be buried under the blood and body parts of the battlefield.',
          },
 'autoact': {'goto': 'field',
            },
},
{'id': 'forest',
 'story': {'text': '',
          },
},
{'id': 'field',
 'case': [{'cond': {'var': 'warrior_on_field',
                    'val': None,
                   },
           'story': {'text': 'A fallen warrior lies face-down on the ground.',
                    },
           'actable': [{'text': 'Search warrior',
                        'result': {'goto': 'field',
                                   'set': {'var': 'warrior_on_field',
                                           'val': 'examined',
                                          },
                                  },
                       },
                       {'text': 'Leave battlefield',
                        'result': {'goto': 'forest'}
                       },
                      ],
          },
          {'cond': {'var': 'warrior_on_field',
                    'val': 'examined',
                   },
           'story': {'text': 'The fallen warrior stares blankly into the sky, an amulet on his chest glittering in the sunlight.',
                    },
          },
          {'cond': {'var': 'warrior_on_field',
                    'val': 'plundered'},
           'story': {'text': 'The fallen warrior that you have looted stares blankly into the sky, beyond accusation.',
                    },
          },
         ],
},
]

#--------------------------------------------------------------------
import json

f = open('story.json', 'w')
for story_node in story:
    f.write(json.dumps(story_node))
    f.write('\n')
    print('Wrote node %s' % (story_node['id'], ))
f.close()

