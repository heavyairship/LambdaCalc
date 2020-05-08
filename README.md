# Lambda Calculus in Python!

## Overview 
 
This project provides a Python library and interpreter for parsing and reducing Lambda Calculus expressions.

## Prerequisities

The project is designed for a MacOS/Linux environment.

Running tests or the interpreter requires python3 and pip3.

Make sure you've set your `$PYTHONOPATH` to include where pip3 installs packages.

## Installation

To install the library and interpreter:
```
$ make install
```

## Library

Here's an example of importing the module, parsing an expression from a string, and reducing that expression:

```
$ python
>>> from LambdaCalc import *
>>> expr = parse("((Lx.x) y)")
>>> reduced = expr.red()
>>> str(reduced)
'y'
```

You can also use the LambdaCalc types to build an expression directly:

```
>>> expr = App(Abs("x", Var("x")), Var("y"))
>>> reduced = expr.red()
>>> str(reduced)
'y'
```

## Interpreter

To run the interpreter:
```
$ lambdapy
> ((Lx.x) y)
y
```

## Tests
To run tests:
```
$ make check
```

