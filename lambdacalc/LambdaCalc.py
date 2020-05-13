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
            selfFree = self.free()
            while (f in selfFree) or (f == self.param):
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

counter = -1
def fresh():
    global counter
    counter += 1
    return "@%d" % counter

def resetFresh():
    global counter
    counter = -1

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
    # Terms are integers, bound identifiers, and variables 
    if not isinstance(t, str):
        raise TypeError("expected to parse term from string")
    if numeric(t):
        return encodeI(int(t))   
    elif t in bindings:
        return bindings[t]
    elif validIden(t):
        return Var(t) 
    else:
        raise ValueError("invalid identifier `%s`" % t)

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
                raise ValueError("identifier `%s` is not valid" % iden)
            idx += 1

            # Parse `=` assignment operator
            assn = tokens[idx]
            if not assn == "=":
                raise ValueError("expected assignment operator `=` not `%s`" % assn)
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
            if expr is None:
                raise ValueError("empty expressions not allowed");
            bindings[iden] = expr

            # Parse `;` terminator
            idx += 1
        else:
            idx += 1

    return bindings

def removeLetBindings(tokens):
    out = []
    idx = 0
    while idx < len(tokens):
        t = tokens[idx]
        if t == 'let':
            while idx < len(tokens) and tokens[idx] != ';':
                idx += 1
            if idx >= len(tokens):
                raise ValueError("expected token `;`")
        else:
            out.append(t)
        idx += 1
    return out

def parseTokens(tokens, bindings):

    # Holds parsed expressions
    stack = []

    while len(tokens) != 0:
        if tokens[0] == '(':
            # Parse expression in `( )`

            # Parse opening `(`
            temp = []
            temp.append(tokens.pop(0))

            # Parse until matching `)`
            left = 1
            right = 0
            while left != right and len(tokens) > 0:
                if tokens[0] == '(':
                    left += 1
                if tokens[0] == ')':
                    right += 1
                temp.append(tokens.pop(0))
            if left != right:
                raise ValueError("could not match parentheses")

            # Recurse on contents between `( )`, leaving off the parentheses
            stack.append(parseTokens(temp[1:-1], bindings))

        elif tokens[0] == 'L':
            # Parse abstraction expression, e.g. Lx.M

            # Parse `L`
            tokens.pop(0)

            # Parse param
            if len(tokens) == 0:
                raise ValueError("missing param after `L`")
            param = tokens.pop(0)
            if not validIden(param):
                raise ValueError("`%s` is an invalid abstraction param" % param)

            # Parse `.`
            if len(tokens) == 0 or tokens.pop(0) != '.':
                raise ValueError("expected `.` after param")

            # Parse body
            temp = []
            while len(tokens) != 0:
                temp.append(tokens.pop(0))

            # Recurse on body
            stack.append(Abs(param, parseTokens(temp, bindings)))
        else:
            # Parse a term expression (base case)
            stack.append(parseTerm(tokens.pop(0), bindings))

    while len(stack) > 1:
        # Parse applications in a left-associative manner
        first = stack.pop(0)
        second = stack.pop(0)
        stack.insert(0, App(first, second))

    # Return the parsed expression if it exsits. If there is no expression, 
    # that means the input was empty or entirely let-bindings.
    return stack[0] if len(stack) > 0 else None
             
def parse(data):
    global bindings
    loadstdlib()
    tokens = tokenize(data)
    bindings.update(parseBindings(tokens, bindings))
    return parseTokens(removeLetBindings(tokens), bindings)
        
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
    # This ordering is important, e.g. since pair.l depends on logic.l
    # FixMe: implement some kind of dependency system.
    filenames = ['logic.l', 'pair.l', 'list.l', 'arithmetic.l']
    for fname in filenames:
        with open(os.path.join(prefix, fname)) as f:
            bindings.update(parseBindings(tokenize(f.read()), bindings))

##########################################################################
# Church Encoding
def decode(l):

    # The Church encodings for 0 and False are alpha-equivalent,
    # so we need to use the hack below to force decoding Lf.Lx.x 
    # as 0 rather than False.
    if str(l) == "(Lf.(Lx.x))":
        return 0

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
