from story import Story, StoryExited

def run_through_story(story_doc, catch_exit = True):
    s = Story(story_doc)
    s.start()
    while True:
        try:
            story_state = s.eval_current_node()
            s.enact(story_state['autoact'])
        except StoryExited:
            if catch_exit:
                break
            else:
                raise
    return s
