Untold
======

A little engine to run interactive stories. 

KNOWN BUGS
----------

* Evaluation of scripted nodes is lacking (see FIXME in story_writer.py)
* Example story is highly buggy due to changes in the scripting syntax

TODO
----

##### "I'm working on that right now!"
* Consider i18n/l10n and templating
* Turn test_story from story_writer.py into actual tests

##### Gameplay features
* Rewind / Forward

##### REPL features
* Inspecting / Editing of document / current node
* readline interface instead of raw_input()
  * tab completion
  * automatic creation of matching parens / node stubs

##### Tools
* Proper story_writer
  * yaml2json story converter (come on, it's just loads() and dumps())
  * Some syntax checking (re: story syntax)
* Syntax checker
  * Warnings when multiple evaluatable keys are used in root nodes

##### Minor enhancements
* Conditions
  * any/all/at-least-n/at-most-n for lists of conditions
  * Fold conditions and scripting nodes into a uniform system
* Syntax
  * choice weights
    * variable-stores values
    * variables-stored values weighted by constants
    * conditions as weights?
* Rename conditions to expressions? Formulas?
* Debugging
  * Improve Exceptions with Node IDs
  * Catch and override CaseWithoutActiveCond

##### Documentation
* Story syntax (JSON and YAML)
  * Remove the stub from story_writer
  