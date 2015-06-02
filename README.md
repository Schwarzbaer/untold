Untold
======

A little engine to run interactive stories. 

KNOWN BUGS
----------

* Evaluation of scripted nodes is lacking (see FIXME in story_writer.py)
* Example story is highly buggy due to changes in the scripting syntax

TODO
----

#####Immediate changes
* Change history format to
      [[{'var': <>,
         'from': <>,
         'to': <>},
        {...}],
       [...],
      ]
* Allow 'set' to have conditions, and lists of conditions, as arguments
* Change scene format to
      {'scene': {'presentation': <foo>,
                 'actables': <bar>,
                 'autoact': <baz>}}

#####Someday-soon changes
* Rewind / Forward
* Inspecting / Editing of document / current node in the REPL
* Consider i18n/l10 and templating
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
