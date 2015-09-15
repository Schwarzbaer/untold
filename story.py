import json
import random
from pprint import pprint

# Conditions ---------------------------------------------------------

class InvalidCondition(Exception):
    pass

def eval_condition(cond_node, state):
    # Returns True or False
    # True, False: Return just that
    # {var: varname, val: value} # DONE: Exact match: TODO: value in list-in-state-variable
    # {var: varname, val: [value]} # TODO: Both list-in-state-variable and conditional-value can be lists
    # {var: varname, val_gt: value1, val_lt: value2} # TODO
    # {cond_list: [list of conditions]} # TODO
    if type(cond_node) in [bool, int, float, str]:
        return cond_node
    # FIXME: This should be folded into the one above, but NoneType
    # is undefined despite type(None) == NoneType. WTF is going on?
    elif cond_node == None:
        return None
    elif 'const' in cond_node.keys():
        return cond_node['const']
    elif 'var' in cond_node.keys():
        return state.get(cond_node['var'], None)
    elif 'op' in cond_node.keys():
        op = cond_node['op']
        varl = eval_condition(cond_node['varl'], state)
        varr = eval_condition(cond_node['varr'], state)
        if op == '==':
            return varl == varr
        elif op == '!=':
            return varl != varr
        elif op == '<=':
            return varl <= varr
        elif op == '>=':
            return varl >= varr
        elif op == '<':
            return varl < varr
        elif op == '>':
            return varl > varr
    else:
        # This is temporary, until the new syntax is implemented.
        raise InvalidCondition

# Scripting elements -------------------------------------------------

# Common features of list-bearing keywords, specifically:
# IF

def eval_list_node(node_list, state):
    virt_list = []
    for list_node in node_list:
        if 'if' in list_node.keys():
            cond_node = list_node['if']
            if eval_condition(cond_node, state):
                virt_list.append(list_node)
            else:
                pass
        else:
            # No 'if' keyword encountered
            virt_list.append(list_node)
    return virt_list

# CASE structure
# {case: [{cond: True, foo: 1}],
#  bar: 1}
# returns
# {foo: 1, bar: 1}
# Returns the first foo-containing node for which cond is true

class CaseWithoutActiveCond(Exception):
    pass

def eval_case_node(case_node, state):
    options = eval_list_node(case_node['case'], state)
    for leaf in options:
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
    options = eval_list_node(choice_node['choice'], state)
    weights = [eval_weight(leaf.get('weight', 1.0), state)
               for leaf in options]
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
    # FIXME: What to do about this debugging code?
    # print("|| Node before scene script evaluation")
    # pprint(node['scene'])
    scene_node = eval_script_node(node['scene'], state)
    # print("|| Node after scene script evaluation")
    # pprint(scene_node)
    if 'presentation' in scene_node.keys():
        presentation = eval_script_node(scene_node['presentation'], state)
    else:
        presentation = False
    if 'actables' in scene_node.keys():
        actables = eval_script_node(eval_list_node(scene_node['actables'], state), state)
    else:
        actables = False
    if 'autoact' in scene_node.keys():
        autoact = eval_script_node(scene_node['autoact'], state)
    else:
        autoact = False
    return {'presentation': presentation,
            'actables': actables,
            'autoact': autoact}

# Root nodes ---------------------------------------------------------

class StoryExited(Exception):
    pass

class NodeNotEvaluatable(Exception):
    def __init__(self, node):
        self.node = node
    def __str__(self):
        return repr(self.node)

def eval_special_node(node, state):
    if node['special'] == 'exit':
        raise StoryExited

node_funcs = {
    'scene': eval_scene_node,
    'special': eval_special_node,
}

# Check the nodes keywords against the functions that handle nodes
# with those keywords. Actually, one matching function will be chosen
# at pseudo-random (order of hashing) and its result will be
# returned. Thus each story node should have only exactly one keyword
# that is applicable here. 
def eval_root_node(node, state):
    node = eval_script_node(node, state)
    node_func_keys = node_funcs.keys()
    for key in node.keys():
        if key in node_func_keys:
            return node_funcs[key](node, state)
    # Raise exception, as there is no function to handle this node.
    raise NodeNotEvaluatable(node)

# Story management ---------------------------------------------------

class NoSuchMetadata(Exception):
    pass

class Story:
    def __init__(self, story_doc = 'story.json'):
        if type(story_doc) == str:
            self.load(story_doc)
        elif type(story_doc) == dict:
            self.document = story_doc
        else:
            # FIXME: Beautify ths.
            # No valid document reference has been provided.
            raise Exception
        # FIXME: Wrap this in a try block, as stories may be malformed.
        self.story = {node['id']: node for node in self.document['story']}

    def load(self, filename = 'story.json'):
        """Load a story. Telling it also requires a state, so start()
        or load_state() it."""
        # Read story
        f = open(filename, 'r')
        self.document = json.loads(f.read())
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
        self.state = {'__history': []}
        self.state['__current_node'] = self.document['start_node']

    # Utility

    def get_state_var(self, field):
        return self.state.get(field, None)

    def set_state_var(self, field, value):
        self.state[field] = value
    
    def get_metadata(self, field):
        try:
            return self.document[field]
        except KeyError:
            raise NoSuchMetadata
    
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
            if type(action['set']) == list:
                set_commands = action['set']
            else:
                set_commands = [action['set']]
            for set_command in set_commands:
                var = set_command['var']
                old_val = self.get_state_var(set_command['var'])
                new_val = eval_condition(set_command['val'], self.state)
                self.set_state_var(var, new_val)
                changes.append({'var': var,
                                'from': old_val,
                                'to': new_val})
        # FIXME: 'goto' could be merged into 'set', but syntactic
        # sugar may be nice here?
        if 'goto' in action:
            changes.append({'var': '__current_node',
                            'from': self.state['__current_node'],
                            'to': action['goto']})
            self.state['__current_node'] = action['goto']
        self.state['__history'].append(changes)

    # Game Flow

    def eval_current_node(self):
        return self.eval_node(self.state['__current_node'])
