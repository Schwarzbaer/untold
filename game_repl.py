#!/usr/bin/env python3

# TODO:
# Consider i18n/l10 and templating
# Turn list-of-JSON-docs into one doc.
#   Add metadata: starting node, default node, author / copyright
# Lots of condition improvements

import json
from pprint import pprint

# Conditions ---------------------------------------------------------

def eval_condition(cond_node, state):
    # Returns True or False
    # True, False: Return just that
    # {var: varname, val: value} # DONE: Exact match: TODO: value in list-in-state-variable
    # {var: varname, val: [value]} # TODO: Both list-in-state-variable and conditional-value can be lists
    # {var: varname, val_gt: value1, val_lt: value2} # TODO
    # {cond_list: [list of conditions]} # TODO
    if type(cond_node) == bool:
        return cond_node
    var = cond_node['var']
    val = cond_node['val']
    if var in state.keys():
        return val == state[var]
    else:
        return val == None

# Scripting elements -------------------------------------------------

# CASE structure
# {case: [{cond: True, foo: 1}],
#  bar: 1}
# returns
# {foo: 1, bar: 1}
# Returns the first foo-containing node for which cond is true

class CaseWithoutActiveCond(Exception):
    pass

def eval_case_node(case_node, state):
    # FIXME: Find active leaf
    for leaf in case_node['case']:
        condition = leaf['cond']
        if eval_condition(condition, state):
            virt_node = case_node.copy()
            del virt_node['case']
            virt_node.update(leaf)
            return virt_node
    raise CaseWithoutActiveCond

# Managerial

script_funcs = {
    'case': eval_case_node,
}

func_tags = set(script_funcs.keys())

def node_has_script_elements(node):
    return any([script_tag in node for script_tag in script_funcs.keys()])

def eval_script_node(node, state):
    cont = node_has_script_elements(node)
    while cont:
        # print("eval_script_node: %s" % (str(node), ))
        node_tags = set(node.keys())
        tag = next((tag for tag in node_tags if tag in func_tags), False)
        if tag:
            node = script_funcs[tag](node, state)
        else:
            cont = False
    return node

TEXT_MODE = 1

# Scene nodes --------------------------------------------------------

def eval_scene_node(node, state):
    if 'scene' in node.keys():
        scene = eval_script_node(node['scene'], state)
    else:
        scene = False
    if 'actable' in node.keys():
        actable = eval_script_node(node['actable'], state)
    else:
        actable = False
    if 'autoact' in node.keys():
        autoact = eval_script_node(node['autoact'], state)
    else:
        autoact = False
    return (scene, actable, autoact)

# Root nodes ---------------------------------------------------------

class StoryExited(Exception):
    pass

def eval_special_node(node, state):
    if node['special'] == 'exit':
        raise StoryExited

node_funcs = {
    'scene': eval_scene_node,
    'actable': eval_scene_node,
    'autoact': eval_scene_node,
    'special': eval_special_node,
}

def eval_root_node(node, state):
    node = eval_script_node(node, state)
    # print("eval_root_node %s" % (str(node), ))
    node_func_keys = node_funcs.keys()
    for key in node.keys():
        if key in node_func_keys:
            return node_funcs[key](node, state)
    # FIXME: Raise exception, as there is no function to handle this node.
    return False

# --------------------------------------------------------------------

class Story:
    def __init__(self, mode = TEXT_MODE):
        self.mode = mode
    def load(self, filename = 'story.json'):
        # Read story
        self.story = {}
        f = open(filename, 'r')
        for line in f.readlines():
            node = json.loads(line)
            self.story[node['id']] = node
        f.close()
        # Set starting state
        self.state = {}#{'warrior_on_field': 'plundered'}
        self.history = []
        # current_node = self.story_nodes[self.story_state]
        # FIXME: Create representation object
        # return self.act(None)
    def eval_node(self, node_id):
        node = self.story[node_id]
        return eval_root_node(node, self.state)
    def enact(self, action):
        if 'set' in action:
            self.state[action['set']['var']] = action['set']['val']
            # print("set %s to %s" % (action['set']['var'], action['set']['val'],))
        if 'goto' in action:
            self.state['current_node'] = action['goto']
    # Game Flow
    def start(self):
        self.enact({'goto': 'start'})
    def eval_current_node(self):
        return self.eval_node(self.state['current_node'])

## Game states
#PRE_GAME = 1
#IN_GAME = 2
## Return codes for the REPL
#PROCEED = 0
#EXIT = 1
#REPOLL = 2 # send an empty command without prompting for input
#
#class GameManager:
#    """An abstraction between the actual story manager and the
#    interface, providing input parsing, and later on possibly time-
#    related event driving.
#    """
#    def __init__(self):
#        self.state = PRE_GAME
#    def command(self, *commands):
#        if self.state == PRE_GAME:
#            if len(commands) == 0: # Autostart
#                return (PROCEED, divider + start_menu)
#            elif commands[0] in ['quit', 'exit']:
#                return(EXIT, "Terminating.")
#            elif commands[0] == 'start': # Start a new game
#                self.story = Story()
#                self.story.load()
#                self.story.start()
#                self.state = IN_GAME
#                return (REPOLL, "Story loaded.")
#            else:
#                return(PROCEED, "Unknown command.")
#        elif self.state == IN_GAME:
#            if commands[0] == '':
#                triplet = self.story.eval_current_node()
#                return (PROCEED, triplet)
#            else:
#                # FIXME: Make sure that this really is the start of the game!
#                pass
#            representation = self.story.step()
#            return(PROCEED, representation)
#        else:
#            return (EXIT, "No proper state.")

# REPL ---------------------------------------------------------------

divider = '----------------------------------------------------------------------\n'
start_menu = \
"""start: Start new game.
list : Show list of savegames. (Not implemented)
load : Load a savegame. (Not implemented)
quit : Exit game.
exit : Exit game.
"""

#if __name__ == '__main__':
#    game = GameManager()
#    meta, output = game.command()
#
#    # A simple REPL to drive the Game Manager interactively in lieu of a
#    # graphical interface.
#    print("Interactive Storytelling REPL v0.1")
#    cont = True
#
#    while cont:
#        print(output)
#        try:
#            if meta == PROCEED:
#                cmd = input('> ')
#            elif meta == REPOLL:
#                cmd = ''
#            else:
#                # Something's fucky
#                break # FIXME: Better do some exception or so.
#            (meta, output) = game.command(cmd)
#            if meta == EXIT:
#                cont = False
#        except EOFError:
#            print()
#            cont = False
#    print(output)

if __name__ == '__main__':
    s = Story()
    s.load()
    s.start()
    while True:
        try:
            scene, actables, autoacts = s.eval_current_node()
            if scene:
                print(scene['text'])
            if actables:
                for act_id in range(0, len(actables)):
                    print("%d) %s" % (act_id+1, actables[act_id]['text']))
            if autoacts and not actables:
                s.enact(autoacts)
            else:
                #if autoacts:
                #    print("a) %s" % (str(autoacts),))
                cmd = input('> ')
                if cmd=="a":
                    s.enact(autoacts)
                else:
                    cmd_id = int(cmd)-1
                    s.enact(actables[cmd_id]['result'])
                    #print("Executed %d: %s" % (cmd_id, str(actables[cmd_id])))
        except StoryExited:
            break

