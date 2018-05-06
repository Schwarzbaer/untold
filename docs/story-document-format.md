`Untold` Story Document Format
==============================

WARNING
-------

About half of this document is description of the current state of the project,
and half of planning. In particular:
* action nodes don't have proper `presentation`s yet, they just directly take a
  text field.
* In `result` nodes, `set` only takes a single argument.


Basic Workcycle
---------------

* `Untold` generates a dictionary of `presentation`, `actable`s (list of
  Actions) and `autoact`s (an Action to take if the user doesn't act) for the
  frontend to present to the user.
* The frontend passes the selected Action to Untold to enact.
* This continues until the story ends due to a special exit node, at which
  point StoryExited is raised.


Document Format
---------------

A document contains
* a `story`, which is a list of story nodes,
* `start_node`, declaring which node the story starts at,
* optionally, metadata like `title` and `author`.

A story node has an `id` field. Its value is a string that is used to identify
the node for purposes of `start_node` (document-level field) and `goto` (result
field).


##### Special nodes

Additionally, a story node can be a `special node`, which will trigger a special
action declared in the `special` field. Currently the only such action is to
`exit` the story.

The most minimal story in JSON:

      {
        "start_node": "start",
        "story": [
          {
            "id": "start",
            "special": "exit"
          }
        ]
      }

...and in YAML:

      start_node: start
      story:
      - id: start
        special: exit

...with some more metadata:

      {
        "title": "Example from the docs",
        "author": "TheCheapestPixels",
        "start_node": "start",
        "story": [
          {
            "id": "start",
            "special": "exit"
          }        ]
      }

...and again in YAML:

      title: Example from the docs
      author: TheCheapestPixels
      start_node: start
      story:
      - id: start
        special: exit


##### Scene Nodes

A story node can also be (and typically is) a `scene node`. These do have a
`scene` field (and no `special` field), which contains several sub-nodes:
* `presentation` determines the possible ways to represent this node in a user
  frontend, be they text, audio, image, movie, 3D scenery,... It is up to the
  frontend to select the most appropriate representation and present it to the
  user.
* `actable` contains a list of actions that the user can take. Each action
  consists of a `presentation` for frontend purposes, and a `result`.
  * The `presentation` works just the same for result nodes as it does for scene
    nodes.
  * `result` nodes consist of the effects of an action. Currently, two kinds of
    effect are supported:
    * `set` contains a list of variable / value pairs, and will set each given
      variable in the game's state to given value. This field is optional. For
      more on game state, see `Scripting Sub-Nodes`.
    * `goto` will cause a transition to the indicated story node. This field is
      mandatory.
    Do note that if both kinds of field are present, first the `set`s will be
    performed, then the `goto`.

Thus, a typical story node would look like this in JSON:

      {
        "scene": {
          "presentation": {
            "text": "This is the scene as it presents itself."
          },
          "actable": [
            {
              "presentation": {
                "text": "This is a possible action you can take."
              },
              "result": {
                "set": {
                  "var": "foo",
                  "val": 17
                },
                "goto": "target_node"
              }
            }
          ],
          "autoact": {
            "set": {
              "var": "foo",
              "val": 23
            },
            "goto": "target_node"
          }
        }
      }

...and like this in YAML:

      scene:
        presentation:
          text: This is the scene as it presents itself.
        actable:
        - presentation:
            text: This is a possible action you can take.
          result:
            set:
              var: foo
              val: 17
            goto: target_node
        autoact:
          set:
            var: foo
            val: 23
          goto: target_node

Since JSON can be embedded in YAML, a better human-readable form might be:

      scene:
        presentation: {text: This is the scene as it presents itself.}
        actable:
        - presentation: {text: This is a possible action you can take.}
          result:
            set: {var: foo, val: 17}
            goto: target_node
        autoact:
          set: {var: foo, val: 23}
          goto: target_node

And putting it all together in a complete story document (and slightly extending
it) would look like this:

      title: Second example from the docs
      author: TheCheapestPixels
      start_node: start
      story:
      - id: start
       scene:
          presentation: {text: This is the scene as it presents itself.}
          actable:
          - presentation: {text: This is a possible action you can take.}
            result:
              set: {var: foo, val: 17}
              goto: exit_node
          - presentation: {text: This is another action.}
            result:
              set: {var: foo, val: 5}
              goto: exit_node
          autoact:
            set: {var: foo, val: 23}
            goto: exit_node
      - id: exit_node
        special: exit


##### Scripting Sub-Nodes

Within `scene` elements (that is, within the nodes in a `scene` field),
scripting elements can be used to customize a node based on game state.

The game state is a set of variables with strings, ints, floats, or booleans
for their value. The absence of a variable is, programmatically, the same as
its value being none.

Currently there are two types of scripting elements, `case`-likes and
`if`-likes. Both use `conditions`, which are explained in the next chapter.

`case`-like elements work by embedding the possible actual sub-nodes in a list,
and annotating them with conditions and / or other metadata on which the
decision which actual sub-node is to be used will be based. When during game
play a node with scripting elements is reached, that node will be evaluated,
meaning that all relevant scripting elements in it will be run. The `case`-like
nodes will then replace themselves with the embedded node that is selected based
on the current game state. Thus, scripting elements will never be visible to the
frontend (outside of debug modes). The nodes will always appear like regular,
non-scripted nodes, but their specific appearence may chance when they are
entered (and thus evaluated) again with a different game state in place.
* case/cond:

        {
          "case": [
            {
              "cond": <condition>,
              <other_fields>: ...
            },
            {
              "cond": <condition>,
              <other_fields>: ...
            }
          ]
        }

  During an evaluation of the node, the case will be (virtually) removed, and
  the other_fields from the first leaf node in the cases list for which cond is
  true will take its place.
* choice/weight:

        {
          "choice": [
            {
              "weight": 3,
              <other_fields>: ...
            },
            {
              "weight": 2,
              <other_fields>: ...
            }
          ]
        }

  Similar to case in functionality, except that the sub-node actually used is
  chosen at random. This choice is biased by the weights that sub-nodes have,
  with each sub-nodes chance of being chosen being its weight divided by the
  sum of weights.
  If no weight is given for a sub-node, then its weight implicitly is 1.


`if`-like elements occur in lists. During evaluation, all list elements with an
`if` get removed if the `if`'s condition is not fulfilled.
* if:

        {
          <list_using_field>: [
            {
              "if": <condition>,
              <other_fields>: ...
            },
            {
              "if": <condition>,
              <other_fields>: ...
            }
          ]
        }

  When a list is evaluated, only the nodes for which the if-condition is true
  (or which do not have an if-field) are considered.


##### Conditions

Conditions are expressions that allow to write stories that are reactive to the
current state of the story. They return a value. Usually, i.e. in a case/cond,
it is relevant whether that value is equivalent to a boolean True or False.

* None, booleans, strings, ints and floats get returned verbatim.
* Constants in the story (will return that value):

        {'const': <foo>}

* References to variables (value will be None if variable isn't specified in the
  state, its value otherwise):

        {'var': 'foo'}

* Equality test between two sub-conditions

        {'op': '==',
         'varl': {<cond1>},
         'varr': {<cond2>}}

* Is foo absent in the state?

        {'op': '==',
         'varl': {'var': 'foo'},
         'varr': {'const': None}}

* (foo == True) == (bar == False)

        {'op': '==',
         'varl': {'op': '==',
                  'varl': {'var': 'foo'},
                  'varr': {'const': True}},
         'varr': {'op': '==',
                  'varl': {'var': 'bar'},
                  'varr': {'const': False}}}

* Other operators: !=, <, <=, >, >=
* TODO
  * String operators? ~=?
  * sum, abs, other expressions?
