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

def tokenize(data):
    tokens = []
    var = ''
    for idx, c in enumerate(data):
        c = data[idx]
        if whitespace(c):
            if var != '':
                tokens.append(var)
                var = ''
        elif c in ['let', '=', ';', '(', ')', '.', 'L']:
            if var != '':
                tokens.append(var)
                var = ''
            tokens.append(c)
        elif alphanumeric(c):
            var += c
        else:
            raise ValueError("Illegal variable character `%s`" % c) 
    if var != '':
        tokens.append(var)
        var = ''
    return tokens

def parseTerm(t, bindings):
    # FixMe: need better name for this. Or better, a way to avoid needing this.
    if type(t) == str:
        if t in bindings:
            return bindings[t]
        return Var(t) 
    return t

def parseExpr(tokens, bindings):
    while tokens[0] == '(' and tokens[-1] == ')':
        tokens = tokens[1:-1]
    if len(tokens) == 1:
        return parseTerm(tokens[0], bindings)
    if len(tokens) == 4 and tokens[0] == 'L' and tokens[2] == '.':
        return Abs(tokens[1], parseTerm(tokens[3], bindings))
    if len(tokens) == 2:
        return App(parseTerm(tokens[0], bindings), parseTerm(tokens[1], bindings))
    else:
        raise ValueError("Could not parse tokens `%s`" % str(tokens))

def alphanumeric(iden):
    for c in iden:
        if (c < 'a' or c > 'z') and (c < 'A' or c > 'Z') and (c < '1' and c > '9'):
            return False
    return True

def symbolic(iden):
    for c in iden:
        if c not in ['|', '&', '^', '!', '~', '*', '+', '/', '-', '%', '$', '@', '<', '>']:
            return False
    return True

def validIden(iden):
    return alphanumeric(iden) or symbolic(iden)

def stdlib():
    # Logic
    """
    let true = (Lx.(Ly.x));
    let false = (Lx.(Ly.y));
    let && = (Lm.(Ln.(Lx.(Ly.((m ((n x) y)) y)))));
    let || = (Lm.(Ln.(Lx.(Ly.((m x) ((n x) y))))));
    let ! = (Lm.(Lx.(Ly.((m y) x))));
    let -> = (Lm.(Ln.((|| (! m)) n)));
    """
    # Arithmetic
    """
    """
def getBindings(tokens):
    idx = 0
    bindings = {}

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
            while tokens[idx] != ";":
                idx += 1
            end = idx

            # Parse expression and add to bindings
            expr = parseTokens(tokens[begin:end], bindings)
            bindings[iden] = expr

            # Parse `;` terminator
            idx += 1
        else:
            idx += 1

    return bindings
        
def parseTokens(tokens, bindings):            
    if len(tokens) == 0:
        raise ValueError("Empty expressions not allowed")
    if len(tokens) == 1:
        return parseTerm(tokens[0], bindings)
    stack = []
    idx = 0
    while idx < len(tokens):
        t = tokens[idx]
        if t == 'let':
            while tokens[idx] != ';':
                idx += 1
        else:
            stack.append(t)
            if t == ')':
                exprTokens = []
                while stack[-1] != '(':
                    exprTokens.insert(0, stack.pop(-1))
                exprTokens.insert(0, stack.pop(-1))
                stack.append(parseExpr(exprTokens, bindings))
        idx += 1
    if len(stack) != 1:
        raise ValueError("Expected end of input but found more tokens")
    return parseTerm(stack[0], bindings)
             
def parse(data):
    tokens = tokenize(data)
    bindings = getBindings(tokens)
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
# Church Encoding
def encode(n):
    if not isinstance(n, int):
        raise TypeError
    if n < 0:
        raise ValueError

    def body(n):
        return Var("x") if n == 0 else App(Var("f"), body(n-1))

    return Abs("f", Abs("x", body(n)))

def decode(l):
    if not isinstance(l, LambdaExpr):
        raise TypeError
    if not l.body:
        raise ValueError
    if not l.body.body:
        raise ValueError

    def decodeBody(b):
        if isinstance(b, Var):
            return 0
        if isinstance(b, App):
            return 1 + decodeBody(b.second)
        raise ValueError

    return decodeBody(l.body.body)

def succ(l):
    if not isinstance(l, LambdaExpr):
        raise TypeError
    return App(parse("(Ln.(Lf.(Lx.(f ((n f) x)))))"), l).bigRed()
