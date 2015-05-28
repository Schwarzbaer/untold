UNTOLD
======

A little engine to run interactive stories. 

KNOWN BUGS
----------

* Evaluation of scripted nodes is lacking 8see FIXME in story_writer.py)

TODO
----

* Rewind / Forward
* Inspecting / Editing of document / current node in the REPL
* Consider i18n/l10 and templating
* Conditions
  * any/all/at-least-n/at-most-n for lists of conditions
* Syntax
  * choice weights
    * variable-stores values
    * variables-stored values weighted by constants
* Document story syntax (JSON and YAML)
  * ...and remove the stub from story_writer
* Proper story_writer
  * yaml2json story converter (come on, it's just loads() and dumps())
  * Some syntax checking (re: story syntax)

