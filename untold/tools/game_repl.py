#!/usr/bin/env python3

# TODO:
#   rewind / redo history
# FIXME: repl_command has to raise an Exception or something so that it breaks
# out of the two endless loops around it.

import argparse
from pprint import pprint
import textwrap

from untold.story import Story, StoryExited, NoSuchMetadata


# REPL ---------------------------------------------------------------

divider = '-' * 70 + '\n'
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
        self.story = Story(story_file)
        self.pretext()
        self.story.start()

    def load_game(self, savegame_file = 'autosave.json'):
        self.story.load_state()

    def save_game(self, savegame_file = 'autosave.json'):
        self.story.save_state()

    def restart_game(self):
        self.story.start()

    def pretext(self):
        try:
            title = self.story.get_metadata('title')
            print()
            print(title)
            print('-'*len(title))
            print()
        except NoSuchMetadata:
            pass
        try:
            print("By %s" % (self.story.get_metadata('author'), ))
            print()
        except NoSuchMetadata:
            pass

    def repl_command(self, cmd_str):
        repl_command = cmd_str.split(' ')
        if repl_command[0] == 'history':
            # FIXME: Story should have an interface to access the history
            history = self.story.state['__history']
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

    def repl_entry(self, current_node, num_actions, has_autoact):
        while True:
            try:
                cmd = input('> ')
                if len(cmd)>0 and cmd.split(' ')[0] in self.repl_commands:
                    self.repl_command(cmd)
                elif cmd == "a":
                    if has_autoact:
                        return -1
                    else:
                        raise ValueError
                elif cmd == '?':
                    print("Current node:")
                    pprint(current_node)
                    print("Current state:")
                    pprint(self.story.state)
                else:
                    cmd_id = int(cmd)  # FIXME: Not an int? ValueError!
                    if cmd_id > num_actions or cmd_id < 1:
                        raise ValueError
                    else:
                        return cmd_id - 1
            except ValueError:
                print("Please enter a number from 1 to {}".format(num_actions))

    def loop(self, debug=False):
        while True:
            try:
                # Display everything
                current_node = self.story.eval_current_node()
                presentation = current_node.get('presentation', False)
                actables = current_node.get('actables', False)
                autoacts = current_node.get('autoact', False)
                if debug:
                    print()
                    print("-- Current node (pre-evaluation):")
                    pprint(self.story.story[self.story.state['__current_node']])
                    print("-- Current node (post-evaluation):")
                    pprint(current_node)
                    print("-- Current story state:")
                    pprint(self.story.state)
                    print()
                if presentation:
                    for line in textwrap.wrap(presentation['text']):
                        print(line)
                if actables:
                    for act_id in range(0, len(actables)):
                        print("%d) %s" % (act_id+1, actables[act_id]['text']))
                if autoacts and not actables:
                    self.story.enact(autoacts)
                else:
                    # Let user choose his action, enact it, end loop
                    if actables is False:
                        num_actables = 0
                    else:
                        num_actables = len(actables)
                    cmd_id = self.repl_entry(
                        current_node,
                        num_actables,
                        bool(autoacts),
                    )
                    if cmd_id == -1:
                        self.story.enact(autoacts)
                    else:
                        self.story.enact(actables[cmd_id]['result'])
            except StoryExited:
                print("Story has ended.")
                break
            except EOFError:
                # Ctrl-D in input()
                print()
                print("See you later, hope you had a good time!")
                print()
                break


def run_repl():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'story',
        type=str,
        help='Story file.',
    )
    args = parser.parse_args()
    story_file = args.story
    repl = REPL(story_file=story_file)
    repl.loop()


if __name__ == '__main__':
    run_repl()
