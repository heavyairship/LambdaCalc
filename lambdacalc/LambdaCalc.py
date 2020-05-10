##########################################################################
# Parsing/reduction for the Lambda Calculus
# 
#
# Syntax for valid Lambda terms:
#
# x      Variable: A character or string that represents an atomic value.
#
# (Lx.M) Abstraction: A function definition that binds the parameter 
#        variable x in the body M, which is a Lambda term.
#
# (M N)  Application: Application of a function M to an argument N, both
#        of which are lambda terms.
#
# Note that extra parentheses are allowed by the parser, but the 
# parentheses around Abstractions and Applications are required.

##########################################################################
# Abstract base class for a Lambda Calculus Expression
class LambdaExpr(object):
    def red(self):
        pass
    def bigRed(self):
        pass
    def app(self, argument):
        pass
    def sub(self, var, expr):
        pass
    def free(self):
        pass
    def normal(self):
        pass
    def __str__(self):
        pass

##########################################################################
# Lambda Calculus Variable
class Var(LambdaExpr):
    def __init__(self, var):
        self.var = var
    def red(self):
        return self
    def bigRed(self):
        return self
    def app(self, argument):
        if not isinstance(argument, LambdaExpr):
            raise TypeError
        return App(self, argument)
    def sub(self, var, expr):
        if not isinstance(var, str) or not isinstance(expr, LambdaExpr):
            raise TypeError
        return self if self.var != var else expr
    def free(self):
        return set([self.var])
    def normal(self):
        return True
    def __str__(self):
        return self.var

##########################################################################
# Lambda Calculus Abstraction
class Abs(LambdaExpr):
    def __init__(self, param, body):
        self.param = param
        self.body = body
    def red(self):
        return Abs(self.param, self.body.red())
    def bigRed(self):
        return Abs(self.param, self.body.bigRed())
    def app(self, argument):
        if not isinstance(argument, LambdaExpr):
            raise TypeError
        return self.body.sub(self.param, argument)
    def sub(self, var, expr):
        if not isinstance(var, str) or not isinstance(expr, LambdaExpr):
            raise TypeError
        if self.param == var:
            return self
        if self.param in expr.free():
            f = fresh()
            return Abs(f, self.body.sub(self.param, Var(f))).sub(var, expr)
        return Abs(self.param, self.body.sub(var, expr)) 
    def free(self):
        return self.body.free() - set([self.param])
    def normal(self):
        return self.body.normal()
    def __str__(self):
        return "(L%s.%s)" % (self.param, str(self.body))

##########################################################################
# Lambda Calculus Application
class App(LambdaExpr):
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def red(self):
        return self.first.red().app(self.second.red())
    def bigRed(self):
        out = self.first.bigRed().app(self.second.bigRed())
        return out if out.normal() else out.bigRed()
    def app(self, argument):
        if not isinstance(argument, LambdaExpr):
            raise TypeError
        return App(self, argument)
    def sub(self, var, expr):
        if not isinstance(var, str) or not isinstance(expr, LambdaExpr):
            raise TypeError
        return App(self.first.sub(var, expr), self.second.sub(var, expr))
    def free(self):
        return self.first.free().union(self.second.free())
    def normal(self):
        return self.first.normal() and self.second.normal() and not isinstance(self.first, Abs)
    def __str__(self):
        return "(%s %s)" % (str(self.first), str(self.second))

##########################################################################
# Parsing
def whitespace(c):
    return c in ['\t', '\r', '\n', ' ']

def separator(c):
    return c in ['let', '=', ';', '(', ')', '.', 'L']

def tokenize(data):
    tokens = []
    var = ''
    for idx, c in enumerate(data):
        c = data[idx]
        if whitespace(c):
            if var != '':
                tokens.append(var)
                var = ''
        elif separator(c):
            if var != '':
                tokens.append(var)
                var = ''
            tokens.append(c)
        else:
            var += c
    if var != '':
        tokens.append(var)
        var = ''
    return tokens

def parseTerm(t, bindings):
    # FixMe: need better name for this. Or better, a way to avoid needing this.
    if type(t) == str:
        if numeric(t):
            return encodeI(int(t))   
        elif t in bindings:
            return bindings[t]
        elif validIden(t):
            return Var(t) 
        else:
            raise ValueError("Invalid identifier `%s`" % t)
    assert isinstance(t, LambdaExpr)
    return t

def parseExpr(tokens, bindings):
    while tokens[0] == '(' and tokens[-1] == ')':
        tokens = tokens[1:-1]
    if len(tokens) == 1:
        return parseTerm(tokens[0], bindings)
    if len(tokens) >= 4 and tokens[-4] == 'L' and tokens[-2] == '.':
        return Abs(tokens[-3], parseTerm(tokens[-1], bindings))
    if len(tokens) == 2:
        return App(parseTerm(tokens[0], bindings), parseTerm(tokens[1], bindings))
    else:
        raise ValueError("Could not parse tokens `%s`" % [str(t) for t in tokens])

def alphabetic(c):
    return ('a' <= c and c <= 'z') or ('A' <= c and c <= 'Z')

def symbolic(c):
    return c in ['|', '&', '^', '!', '~', '*', '+', '/', '-', '%', '$', '@', '<', '>']

def numeric(iden):
    for c in iden:
        if c < '0' or c > '9':
            return False
    return True

def validIden(iden):
    if numeric(iden):
        return False
    for c in iden:
        if c == 'L':
            return False
        if not symbolic(c) and not alphabetic(c) and not numeric(c):
            return False
    return True

def parseBindings(tokens, bindings):
    idx = 0

    while idx < len(tokens):
        t = tokens[idx]
        if t == "let":
            # Parse `let` keyword
            idx += 1

            # Parse identifier
            iden = tokens[idx]
            if not validIden(iden):
                raise ValueError("Identifier `%s` is not valid" % iden)
            idx += 1

            # Parse `=` assignment operator
            assn = tokens[idx]
            if not assn == "=":
                raise ValueError("Expected assignment operator `=` not `%s`" % assn)
            idx += 1

            # Find beginning/end for expression 
            begin = idx
            while idx < len(tokens) and tokens[idx] != ';':
                idx += 1
            if idx >= len(tokens):
                raise ValueError("expected token `;`")
            end = idx

            # Parse expression and add to bindings
            expr = parseTokens(tokens[begin:end], bindings)
            assert expr is not None
            bindings[iden] = expr

            # Parse `;` terminator
            idx += 1
        else:
            idx += 1

    return bindings
        
def parseTokens(tokens, bindings):            
    # FixMe: this function is pretty hacky.
    if len(tokens) == 0:
        return None
    if len(tokens) == 1:
        return parseTerm(tokens[0], bindings)
    stack = []
    idx = 0
    while idx < len(tokens):

        t = tokens[idx]

        if t == 'let':
            # Skip over let bindings
            while idx < len(tokens) and tokens[idx] != ';':
                idx += 1
            if idx >= len(tokens):
                raise ValueError("expected token `;`")
        else:
            stack.append(t)
            if t == ')':
                exprTokens = []
                while stack[-1] != '(':
                    exprTokens.insert(0, stack.pop(-1))
                    if len(stack) == 0:
                        raise ValueError("expected token `(`")
                exprTokens.insert(0, stack.pop(-1))
                stack.append(parseTokens(exprTokens[1:-1], bindings))
            while len(stack) >= 2 and not separator(stack[-1]) and not separator(stack[-2]):
                # Allow shorthand applications. E.g. a b or a b c, instead of (a b) or
                # ((a b) c), respectively.
                exprTokens = []
                for i in range(2):
                    exprTokens.insert(0, stack.pop(-1))
                stack.append(parseExpr(exprTokens, bindings))
        idx += 1

    while len(stack) >= 4:
        # Allow shorthand abstractions. E.g. Lx.Ly.z instead of (Lx.(Ly.z))
        exprTokens = []
        for i in range(4):
            exprTokens.insert(0, stack.pop(-1))
        stack.append(parseExpr(exprTokens, bindings))

    while len(stack) >= 2 and not separator(stack[-1]) and not separator(stack[-2]):
        # Allow shorthand applications. E.g. a b or a b c, instead of (a b) or
        # ((a b) c), respectively.
        exprTokens = []
        for i in range(2):
            exprTokens.insert(0, stack.pop(-1))
        stack.append(parseExpr(exprTokens, bindings))

    if len(stack) == 1:
        return parseTerm(stack[0], bindings)
    elif len(stack) == 0:
        # Happens if input only contains let bindings
        return None
    else:
        raise ValueError("invalid stack %s" % stack)
             
def parse(data):
    global bindings
    loadstdlib()
    tokens = tokenize(data)
    bindings.update(parseBindings(tokens, bindings))
    return parseTokens(tokens, bindings)
        
counter = -1
def fresh():
    global counter
    counter += 1
    return "@%d" % counter

def resetFresh():
    global counter
    counter = -1

##########################################################################
# Load the standard library
import os
stdlibLoaded = False
bindings = {}
def loadstdlib():
    global bindings
    global stdlibLoaded
    if stdlibLoaded:
        return
    stdlibLoaded = True
    prefix = os.path.join(os.path.dirname(os.path.realpath(__file__)), "stdlib")
    filenames = ['arithmetic.l', 'logic.l']
    for fname in filenames:
        with open(os.path.join(prefix, fname)) as f:
            bindings.update(parseBindings(tokenize(f.read()), bindings))

##########################################################################
# Church Encoding
def decode(l):
    try:
        return decodeB(l)
    except ValueError:
        pass
    try:
        return decodeI(l)
    except ValueError:
        pass
    return l

def encodeI(n):
    if not isinstance(n, int):
        raise TypeError("input must be an int")
    if n < 0:
        raise ValueError("negative ints not supported")

    def body(n):
        return Var("x") if n == 0 else App(Var("f"), body(n-1))

    return Abs("f", Abs("x", body(n)))

def decodeI(l):
    if not isinstance(l, LambdaExpr):
        raise TypeError("input must be a lambda expression")
    if not isinstance(l, Abs) or not isinstance(l.body, Abs):
        raise ValueError("cannot decode expression")
    f = l.param
    x = l.body.param
    if f == x:
        raise ValueError("cannot decode expression")

    def decodeBody(b):
        if isinstance(b, Var) and b.var == x:
            return 0
        if isinstance(b, App) and isinstance(b.first, Var) and b.first.var == f:
            return 1 + decodeBody(b.second)
        raise ValueError("cannot decode expression")

    return decodeBody(l.body.body)

# Note that boolean encoding is not required, since `true` and `false`
# are defined in stdlib.

def decodeB(l):
    if not isinstance(l, LambdaExpr):
        raise TypeError("input must be a lambda expression")
    if not isinstance(l, Abs) or not isinstance(l.body, Abs):
        raise ValueError("cannot decode expression")
    x = l.param
    y = l.body.param
    b = l.body.body
    if not isinstance(b, Var):
        raise ValueError("cannot decode expression")
    if b.var == x:
        return True
    if b.var == y:
        return False
    raise ValueError("cannot decode expression")
