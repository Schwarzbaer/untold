#!/usr/bin/env python3

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

# Story management ---------------------------------------------------

class Story:
    def __init__(self, mode = TEXT_MODE):
        self.mode = mode
    def load(self, filename = 'story.json'):
        # Read story
        f = open(filename, 'r')
        self.document = json.loads(f.read())
        self.story = {node['id']: node for node in self.document['story']}
        f.close()
        # Set starting state
        self.state = {}
        self.history = []
    def get_metadata(self, field):
        return self.document[field]
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
        self.enact({'goto': self.document['start_node']})
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
    def __init__(self, filename = 'story.json'):
        self.repl_commands = ['history']
        self.story = Story()
        self.story.load(filename)
        self.pretext()
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
            if len(repl_command) == 1:
                print("History so far:")
                pprint(self.story.history)
            else:
                try:
                    n = int(repl_command[1])
                    print("Last %d history entries:" % (n, ))
                    pprint(self.story.history[:-n])
                except ValueError:
                    print("Usage: history <n>")
    def loop(self):
        while True:
            try:
                scene, actables, autoacts = self.story.eval_current_node()
                if scene:
                    print(scene['text'])
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
                break

        
        
def story_repl(filename = 'story.json'):
    repl_commands = ['history']
    s = Story()
    s.load(filename)
    print()
    title = s.get_metadata('title')
    print(title)
    print('-'*len(title))
    print()
    print("By %s" % (s.get_metadata('author'), ))
    print()
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
                # FIXME: Catch EOFError from Ctrl-d
                cmd = input('> ')
                if len(cmd)>0 and cmd.split(' ')[0] in repl_commands:
                    repl_command = cmd.split(' ')
                    if repl_command[0] == 'history':
                        if len(repl_command) == 1:
                            pprint(s.history)
                        else:
                            pass # FIXME: Show last n history entries
                elif cmd=="a":
                    # FIXME: Make sure that autoact exists, otherwise reprompt
                    s.enact(autoacts)
                else:
                    try:
                    # FIXME: Make sure that answer is in range, otherwise reprompt
                        cmd_id = int(cmd)-1
                    except ValueError:
                        pass # FIXME: Reprompt (What was entered wasn't an int)
                    if cmd_id > len(actables):
                        pass # FIXME: Reprompt (list is too long)
                    s.enact(actables[cmd_id]['result'])
        except StoryExited:
            break

if __name__ == '__main__':
    repl = REPL()
    repl.loop()
    # story_repl()

