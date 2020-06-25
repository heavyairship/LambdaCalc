# Lambda Calculus in Python

## Overview 
 
This project provides a Python library and interpreter for parsing and reducing Lambda Calculus expressions. The reduction strategy used is [Normal Order Reduction to Normal Form](https://www.itu.dk/~sestoft/papers/sestoft-lamreduce.pdf).

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
>>> from lambdacalc.LambdaCalc import *
>>> expr = parse("((Lx.x) y)")
>>> reduced = expr.red()
>>> str(reduced)
'y'
```

You can also build an expression directly:

```
>>> expr = App(Abs("x", Var("x")), Var("y"))
>>> reduced = expr.red()
>>> str(reduced)
'y'
```

## Interpreter

To run the interpreter as a REPL:
```
$ lambdapy
> (Lx.x) y
y
```

To run the interpreter on a file:
```
$ lambdapy --file test.l
((M N) y)
```

For more info run:
```
$ lambdapy --help
```

## Details

### Let-bindings

Let-bindings are supported:

```
> let a = Lx.x;
> a
(Lx.x)
```

And they can refer to identifiers defined by previous let-bindings:

```
> let a = Lx.x;
> let b = a y;
> b
y
```

An identifier can be defined by a let-binding multiple times; the most recent one is used:

```
> let a = x;
> let a = y;
> a
y
```

### Church Encodings

The parser uses Church Encodings to encode (input) and decode (output) integers. All arithmetic evaluation is
done in the Lambda Calculus:

```
> 42
42
> Lf.Lx.f (f (f x))
3
```

### Stdlib

The standard library contains let-bindings for useful things, like arithmetic functions, logical constants and connectives, 
control flow structures (while, if), pairs, lists, etc. Note that this is a work in progress. 
Here are some examples.

#### Arithmetic
```
> ++ 1
2
> + 2 3
5
> * 4 3
12
> ^ 2 3
8
```

#### Logic
```
> true
True
> false
False
> && true false
False
> || false true
True
> -> false true
True
```

#### Control flow
```
> if true 1 2
1
> if false 1 2
2
> let cond = Ls.pair s (neq s 0);
> let body = Ls.-- s;
> (while cond body) 2
0
```

#### Pairs
```
> let p = pair a b;
> first p
a
> second p
b
````

#### Lists
```
> let l = (cons 1 (cons 2 nil));
> head l
1
> head (tail l)
2
> isnil l
False
> isnil (tail (tail l))
True
```

### Parentheses

Implied parentheses may be omitted; applications are left-associative:

```
> M N
(M N)
> M (N) O (P Q)
(((M N) O) (P Q))
> Lx.x
(Lx.x)
> Lx.Ly.Lz.a b c
(Lx.(Ly.(Lz.((a b) c))))
```

## Tests
To run tests:
```
$ make check
```

