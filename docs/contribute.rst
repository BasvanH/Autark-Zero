Developing the Context-Aware Recommendation Engine
========================================================
Of course, anyone can contribute to this program as it is fully open
source project licensed under the MIT license. Development can be done
using any Python IDE or text editor, but using the free `Qt Designer <https://doc.qt.io/qt-5/qtdesigner-manual.html>`_ IDE
is preferred since it has native support for QML and Python.


Debugging
-------------
Debugging on the application can be done using the default Python
debugging facilities, however they will not work whenever Qt is
called. This is because Qt is a C++ library which the debugging tools
are not programmed to deal with. You can run a separate Qt debugging
tool called `Gamma Ray <https://www.kdab.com/development-resources/qt-tools/gammaray/>`_, but this cannot be used for Python
code. Therefore, it is recommend to test these separately. No profiler
has been known to work on the program either.

Developing
--------------
A development system can be loaded using Python's virtual
environment as described in the README. This will create an entirely
new Python environment which can be used to install the exact version
required to run the project. Using this will also avoid tainting your
global Python installation and can avoid nasty dependencies bugs.

Testing
--------------
Currently there is no simple one command system to run all the
tests. Instead, you have to manually run the Python scrips by hand. To
do so simply run `python -m path.to.test``. All tests are written
using the native `unittest
<https://docs.python.org/3/library/unittest.html>`_ module in Python's
standard library. They are also run in the pipeline.

Quality Assurance
------------------
In order to ensure that the software is of the right quality we use a
plethora of tools and style guides. All the tools are run in the
pipeline and are run before committing the code. To ensure the
`pre-commit <https://pre-commit.com/>`_ program is used.

This software makes use of the standard `PEP-8
<https://www.python.org/dev/peps/pep-0008/>`_ Python style guide and the
`Google Python Style Guide
<https://google.github.io/styleguide/pyguide.html>`_. In particular,
this program adheres to the Docstring format outlined in the
former. Documentation is generated using `Sphinx <https://www.sphinx-doc.org/en/master/index.html>`_

For this project the following pre-commit hooks are being used:

* *yapf*: An auto-formatter for Python
* *check-yaml*: Ensures that any commited yaml files are correctly
  formatted
* *end-of-file-fixer*: Ends all files in a newline
* *trailing-whitespace*: Removes all trailing whitespace
* *check-added-large-files*: Doesn't allow anyone to commit large
  files
* *check-json*: Ensures all JSON is valid
* *pretty-format-json*: Prettifies JSON files.
* *requirements-txt-fixer*: Sorts entries
* *autoflake*: Another auto-formatter
* *reorder-python-imports*: Ensures all the imports are sorted.
* *python-use-type-annotations*: Requires that some variables are type checked
* *mypy*: Actually enforces the types in the code
* *flake8*: Checks the formatting of the code to the styleguides.
