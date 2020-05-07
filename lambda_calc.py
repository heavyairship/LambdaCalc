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
    def app(self, argument):
        pass
    def sub(self, var, expr):
        pass
    def free(self):
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
    def __str__(self):
        return "(%s %s)" % (str(self.first), str(self.second))

##########################################################################

def whitespace(c):
    return c in ['\t', '\r', '\n', ' ']

def tokenize(data):
    tokens = []
    var = ''
    for idx, c in enumerate(data):
        c = data[idx]
        if whitespace(c):
            if var != '':
                tokens.append(var)
                var = ''
        elif c in ['(', ')', '.', 'L']:
            if var != '':
                tokens.append(var)
                var = ''
            tokens.append(c)
        elif ('A' <= c and c <= 'Z') or ('a' <= c and c <= 'z'):
            var += c
        else:
            raise ValueError("Illegal variable character: %s" % c) 
    if var != '':
        tokens.append(var)
        var = ''
    return tokens

def parseTerm(t):
    return Var(t) if type(t) == str else t

def parseExpr(tokens):
    while tokens[0] == '(' and tokens[-1] == ')':
        tokens = tokens[1:-1]
    if len(tokens) == 1:
        return parseTerm(tokens[0])
    if len(tokens) == 4 and tokens[0] == 'L' and tokens[2] == '.':
        return Abs(tokens[1], parseTerm(tokens[3]))
    if len(tokens) == 2:
        return App(parseTerm(tokens[0]), parseTerm(tokens[1]))
    else:
        raise ValueError("Could not parse tokens: %s" % str(tokens))

def parse(data):
    tokens = tokenize(data)
    if len(tokens) == 0:
        raise ValueError("Empty expressions not allowed")
    if len(tokens) == 1:
        return Var(tokens[0])
    stack = []
    for t in tokens:
        stack.append(t)
        if t == ')':
            exprTokens = []
            while stack[-1] != '(':
                exprTokens.insert(0, stack.pop(-1))
            exprTokens.insert(0, stack.pop(-1))
            stack.append(parseExpr(exprTokens))
    if len(stack) != 1:
        raise ValueError("Expected end of input but found more tokens")
    return stack[0]
        
counter = -1
def fresh():
    global counter
    counter += 1
    return "@%d" % counter

def resetFresh():
    global counter
    counter = -1
