import json
from pprint import pprint

from untold.scripting import eval_script_node, eval_list_node, eval_expression

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
            # FIXME: Beautify this.
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
                var = eval_expression(set_command['var'], self.state)
                old_val = self.get_state_var(set_command['var'])
                new_val = eval_expression(set_command['val'], self.state)
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
