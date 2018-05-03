#!/usr/bin/env python3

from pprint import pprint
import textwrap

from untold.story import Story, StoryExited, NoSuchMetadata


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

    def loop(self, debug=False):
        skip_eval = False
        while True:
            try:
                if not skip_eval:
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
                else:
                    skip_eval = False
                if presentation:
                    for line in textwrap.wrap(presentation['text']):
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
                print("Story has ended.")
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
