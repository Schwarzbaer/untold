#!/usr/bin/env python3

import json
from pprint import pprint
import textwrap
import random

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
    for leaf in case_node['case']:
        condition = leaf['cond']
        if eval_condition(condition, state):
            virt_node = case_node.copy()
            del virt_node['case']
            virt_node.update(leaf)
            return virt_node
    raise CaseWithoutActiveCond

# CHOICE
# {choice: [{weights: 1},
#           {weights: 1}]}

class UnknownWeightType(Exception):
    pass

def eval_weight(weight_node, state):
    if type(weight_node) == int:
        return float(weight_node)
    elif type(weight_node) == float:
        return weight_node
    else:
        raise UnknownWeightType

def eval_choice_node(choice_node, state):
    weights = [eval_weight(leaf.get('weight', 1.0), state)
               for leaf in choice_node['choice']]
    total_weights = sum(weights)
    c = random.random()
    idx = 0
    w_sum = weights[0] / total_weights
    # FIXME: This should never run beyond the list elements, but maybe I should try/except it anyway?
    while w_sum < c:
        idx += 1
        w_sum += weights[idx] / total_weights
    virt_node = choice_node.copy()
    del virt_node['choice']
    virt_node.update(choice_node['choice'][idx])
    # pprint(virt_node)
    return virt_node

# Managerial

script_funcs = {
    'case': eval_case_node,
    'choice': eval_choice_node,
}

func_tags = set(script_funcs.keys())

def node_has_script_elements(node):
    return any([script_tag in node for script_tag in script_funcs.keys()])

def eval_script_node(node, state):
    cont = node_has_script_elements(node)
    while cont:
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
    # return (scene, actable, autoact)
    return {'scene': scene,
            'actable': actable,
            'autoact': autoact}

# Root nodes ---------------------------------------------------------

class StoryExited(Exception):
    pass

class NodeNotEvaluatable(Exception):
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
    node_func_keys = node_funcs.keys()
    for key in node.keys():
        if key in node_func_keys:
            return node_funcs[key](node, state)
    # FIXME: Raise exception, as there is no function to handle this node.
    raise NodeNotEvaluatable

# Story management ---------------------------------------------------

class Story:
    def __init__(self, mode = TEXT_MODE):
        self.mode = mode
    def load(self, filename = 'story.json'):
        """Load a story. Telling it also requires a state, so start()
        or load_state() it."""
        # Read story
        f = open(filename, 'r')
        self.document = json.loads(f.read())
        self.story = {node['id']: node for node in self.document['story']}
        f.close()
    # Session management
    def load_state(self, filename = 'autosave.json'):
        f = open(filename, 'r')
        self.state = json.loads(f.read())
        f.close()
    def save_state(self, filename = 'autosave.json'):
        f = open(filename, 'w')
        f.write(json.dumps(self.state))
        f.close()
    def start(self):
        self.state = {'history': []}
        self.state['current_node'] = self.document['start_node']
    # Utility
    def get_metadata(self, field):
        return self.document[field]
    # Running a session
    def eval_node(self, node_id):
        node = self.story[node_id]
        return eval_root_node(node, self.state)
    def enact(self, action):
        # FIXME: This should also take the user choice, so it'll be
        # easier to actually show actions being rewound/forwarded, not
        # just state changes being made.
        changes = [] # List of tuples of (variable, (before, after))
        if 'set' in action:
            changes.append((action['set']['var'],
                            (self.state.get(action['set']['var'], None),
                             action['set']['val'])))
            self.state[action['set']['var']] = action['set']['val']
        # FIXME: 'goto' could be merged into 'set', but syntactic
        # sugar may be nice here?
        if 'goto' in action:
            changes.append(('current_node',
                            (self.state['current_node'],
                             action['goto'])))
            self.state['current_node'] = action['goto']
        self.state['history'].append(changes)
    # Game Flow
    def eval_current_node(self):
        return self.eval_node(self.state['current_node'])

# REPL ---------------------------------------------------------------

divider = '----------------------------------------------------------------------\n'
start_menu = \
"""start: Start new game.
list : Show list of savegames. (Not implemented)
load : Load a savegame. (Not implemented)
quit : Exit game.
exit : Exit game.
"""

class REPL:
    def __init__(self, story_file = 'story.json'):
        self.repl_commands = ['history', 'load', 'save', 'restart']
        self.story = Story()
        self.story.load(story_file)
        self.pretext()
        self.story.start()
    def load_game(self, savegame_file = 'autosave.json'):
        self.story.load_state()
    def save_game(self, savegame_file = 'autosave.json'):
        self.story.save_state()
    def restart_game(self):
        self.story.start()
    def pretext(self):
        print()
        title = self.story.get_metadata('title')
        print(title)
        print('-'*len(title))
        print()
        print("By %s" % (self.story.get_metadata('author'), ))
        print()
    def repl_command(self, cmd_str):
        repl_command = cmd_str.split(' ')
        if repl_command[0] == 'history':
            history = self.story.state['history']
            if len(repl_command) == 1:
                print("History so far:")
                pprint(history)
            else:
                try:
                    n = int(repl_command[1])
                    print("Last %d history entries:" % (n, ))
                    pprint(history[-n:])
                except ValueError:
                    print("Usage: history <n>")
        elif repl_command[0] == 'load':
            self.load_game()
        elif repl_command[0] == 'save':
            self.save_game()
        elif repl_command[0] == 'restart':
            self.restart_game()
    def loop(self):
        skip_eval = False
        while True:
            try:
                if not skip_eval:
                    current_node = self.story.eval_current_node()
                    scene = current_node.get('scene', False)
                    actables = current_node.get('actable', False)
                    autoacts = current_node.get('autoact', False)
                else:
                    skip_eval = False
                if scene:
                    for line in textwrap.wrap(scene['text']):
                        print(line)
                if actables:
                    for act_id in range(0, len(actables)):
                        print("%d) %s" % (act_id+1, actables[act_id]['text']))
                if autoacts and not actables:
                    self.story.enact(autoacts)
                else:
                    cmd = input('> ')
                    if len(cmd)>0 and cmd.split(' ')[0] in self.repl_commands:
                        self.repl_command(cmd)
                    elif cmd=="a":
                        # FIXME: Make sure that autoact exists, otherwise reprompt
                        self.story.enact(autoacts)
                    elif cmd=='?':
                        pprint(current_node)
                        skip_eval = True
                    else:
                        try:
                            # FIXME: Make sure that answer is in range, otherwise reprompt
                            cmd_id = int(cmd)-1
                        except ValueError:
                            pass # FIXME: Reprompt (What was entered wasn't an int)
                        if cmd_id > len(actables):
                            pass # FIXME: Reprompt (list is too long)
                        self.story.enact(actables[cmd_id]['result'])
            except StoryExited:
                break
            except EOFError:
                # Ctrl-D in input()
                print()
                print("See you later, hope you had a good time!")
                print()
                break

if __name__ == '__main__':
    repl = REPL()
    repl.loop()

