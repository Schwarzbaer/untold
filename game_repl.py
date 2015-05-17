#!/usr/bin/env python3

import json
from pprint import pprint

divider = '----------------------------------------------------------------------\n'
start_menu = \
"""start: Start new game. (Not implemented)
list : Show list of savegames. (Not implemented)
load : Load a savegame. (Not implemented)
quit : Exit game.
exit : Exit game.
"""

TEXT_MODE = 1

class Representation:
    def __init__(self, node, history, mode = TEXT_MODE):
        self.node = node
        self.history = history
        self.mode = mode
    def get_premise(self):
        # FIXME: Re
        return None

class Story:
    def __init__(self, mode = TEXT_MODE):
        self.mode = mode
    def load(self, filename = 'story.json'):
        # Read story
        self.story_nodes = {}
        f = open(filename, 'r')
        for line in f.readlines():
            node = json.loads(line)
            self.story_nodes[node['id']] = node
        f.close()
        # Set starting state
        self.story_state = {'current_node': 'start'}
        self.history = []
        # current_node = self.story_nodes[self.story_state]
        # FIXME: Create representation object
        # return self.act(None)
    def eval_stored_node(self, node_id):
        story = self.story_nodes[node_id]['story']
        self.eval_node(story)
    # Evaluating JSON nodes to representation/actables/autoact triplets
    def eval_node(self, node):
        node_keys = node.keys()
        if any([story_key in node_keys for story_key in ['story', 'act', 'autoact']]):
            # This is a story node
            return self.eval_story_node(node)
        elif any([script_key in node_keys for script_key in ['case']]):
            return self.eval_node(self.eval_case_node)
        else:
            print('Node is broken')
    def eval_story_node(self, node):
        print('Exec story node')
        representation = ''
        if 'scene' in node.keys():
            representation = node['scene']['text']+'\n'
        return (representation, actables, autoact)
    def eval_case_node(self, node):
        return decased_node

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
                self.state = IN_GAME
                return (PROCEED, "Story loaded.")
            else:
                return(PROCEED, "Unknown command.")
        elif self.state == IN_GAME:
            representation = self.story.step()
            return(PROCEED, representation)
        else:
            return (EXIT, "No proper state.")

if __name__ == '__main__':
    game = GameManager()
    meta, output = game.command()

    # A simple REPL to drive the Game Manager interactively in lieu of a
    # graphical interface.
    print("Interactive Storytelling REPL v0.1")
    cont = True

    while cont:
        print(output)
        try:
            if meta == PROCEED:
                cmd = input('> ')
            elif meta == REPOLL:
                cmd = ''
            else:
                # Something's fucky
                break # FIXME: Better do some exception or so.
            (meta, output) = game.command(cmd)
            if meta == EXIT:
                cont = False
        except EOFError:
            print()
            cont = False
    print(output)

