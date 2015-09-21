Untold
======

A little engine to run interactive stories. 

DEVELOPMENT HINTS
-----------------

* Instead of manipulating nodes directly, always create referential copies
  instead. Later evaluations of the same node might have to create different
  evaluations of them.
* When implementing tags that take lists at argument, process those with
  untold.scripting.eval_list_node(node_list, state) before proceeding.

KNOWN BUGS
----------

* Evaluation of scripted nodes is lacking (see FIXME in story_writer.py)
* Example story is highly buggy due to changes in the scripting syntax

TODO
----

##### "I'm working on that right now!"
* Maybe merge expressions into conditions, as conditions are just boolean expressions?
* test for choice-f (depends on expr)
* Rewrite scripting.eval_script_node(), because it's a mess!
* 'in' operator
* select, select-f: Select n elements (weighted?) from a list
* 'set' should take, exclusive-or to 'val', an 'expr' expression.
* choice: A weight should be able to take an expression
* Consider i18n/l10n and templating

#### Language features

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
* Add typechecking everywhere applicable
      from types import *
      assert foo is IntType, "foo is %s, not Int" % (type(foo), )

##### Documentation
* Story syntax (JSON and YAML)
  * Remove the stub from story_writer
