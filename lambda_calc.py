##########################################################################
# Parsing/reduction for the Lambda Calculus

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
def parse(data):
    # FixMe: implement!
    return App(Abs("x", Var("x")), Abs("x", Var("x")))
        
counter = -1
def fresh():
    global counter
    counter += 1
    return "@%d" % counter

def resetFresh():
    global counter
    counter = -1
