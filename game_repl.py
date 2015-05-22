#!/usr/bin/env python3

import json
from pprint import pprint

# Scripting elements

# Conditions
# Returns True or False
# {var: varname, val: value} # DONE: Exact match: TODO: value in list-in-state-variable
# {var: varname, val: [value]} # TODO: Both list-in-state-variable and conditional-value can be lists
# {var: varname, val_gt: value1, val_lt: value2} # TODO
# {cond_list: [list of conditions]} # TODO
# TODO
def eval_condition(node, state):
    var = node['var']
    val = node['val']
    if var in state.keys():
        return val == state[var]
    else:
        return val == None

# CASE structure
# {case: [{cond: {}, foo}]} # Returns the first foo-containing node for which cond is true
def eval_case_node(node, state):
    # FIXME: Find active leaf
    for leaf in node['case']:
        condition = leaf['cond']
        if eval_condition(condition, state):
            return eval_root_node(leaf, state)
    # FIXME: Raise exception. No applicable case has been found.
    return False

TEXT_MODE = 1

# Structural nodes

# STORY
# A node containing at least an actable or autoact, and optionally a story
def eval_story_node(node, state):
    if 'story' in node.keys():
        story = node['story']
    else:
        story = False
    if 'actable' in node.keys():
        actable = node['actable']
    else:
        actable = False
    if 'autoact' in node.keys():
        autoact = node['autoact']
    else:
        autoact = False
    return (story, actable, autoact)

node_funcs = {
    'story': eval_story_node,
    'actable': eval_story_node,
    'autoact': eval_story_node,
    'case': eval_case_node,
}

def eval_root_node(node, state):
    node_func_keys = node_funcs.keys()
    for key in node.keys():
        if key in node_func_keys:
            return node_funcs[key](node, state)
    # FIXME: Raise exception, as there is no function to handle this node.
    return False

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
            print("set %s to %s" % (action['set']['var'], action['set']['val'],))
        if 'goto' in action:
            self.state['current_node'] = action['goto']
    # Game Flow
    def start(self):
        self.enact({'goto': 'start'})
    def eval_current_node(self):
        return self.eval_node(self.state['current_node'])

# Game states
PRE_GAME = 1
IN_GAME = 2
# Return codes for the REPL
PROCEED = 0
EXIT = 1
REPOLL = 2 # send an empty command without prompting for input

class GameManager:
    """An abstraction between the actual story manager and the
    interface, providing input parsing, and later on possibly time-
    related event driving.
    """
    def __init__(self):
        self.state = PRE_GAME
    def command(self, *commands):
        if self.state == PRE_GAME:
            if len(commands) == 0: # Autostart
                return (PROCEED, divider + start_menu)
            elif commands[0] in ['quit', 'exit']:
                return(EXIT, "Terminating.")
            elif commands[0] == 'start': # Start a new game
                self.story = Story()
                self.story.load()
                self.story.start()
                self.state = IN_GAME
                return (REPOLL, "Story loaded.")
            else:
                return(PROCEED, "Unknown command.")
        elif self.state == IN_GAME:
            if commands[0] == '':
                triplet = self.story.eval_current_node()
                return (PROCEED, triplet)
            else:
                # FIXME: Make sure that this really is the start of the game!
                pass
            representation = self.story.step()
            return(PROCEED, representation)
        else:
            return (EXIT, "No proper state.")

# REPL

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
        story, actables, autoacts = s.eval_current_node()
        if story:
            print(story['text'])
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

