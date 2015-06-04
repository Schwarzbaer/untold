Untold
======

A little engine to run interactive stories. 

KNOWN BUGS
----------

* Evaluation of scripted nodes is lacking (see FIXME in story_writer.py)
* Example story is highly buggy due to changes in the scripting syntax

TODO
----

#####"As soon as possible"
* Change scene format to
      {'scene': {'presentation': <foo>,
                 'actables': <bar>,
                 'autoact': <baz>}}
* Turn test_story from story_writer.py into actual tests

#####"Someday soon"
* Rewind / Forward
* Inspecting / Editing of document / current node in the REPL

#####"Whenever"
* Consider i18n/l10n and templating
* Conditions
  * any/all/at-least-n/at-most-n for lists of conditions
  * Fold conditions and scripting nodes into a uniform system
* Syntax
  * choice weights
    * variable-stores values
    * variables-stored values weighted by constants
    * conditions as weights?
* Document story syntax (JSON and YAML)
  * ...and remove the stub from story_writer
* Proper story_writer
  * yaml2json story converter (come on, it's just loads() and dumps())
  * Some syntax checking (re: story syntax)
* Rename conditions to expressions? Formulas?
* Debugging
  * Improve Exceptions with Node IDs
  * Catch and ovverride CaseWithoutActiveCond
* readline interface instead of raw_input()
  * tab completion
  * automatic creation of matching parens / node stubs
* Add syntax checking to file tools
  