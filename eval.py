import argparse, sys

counter = -1
def fresh():
    global counter
    counter += 1
    return "___fresh_var_%d__" % counter

##########################################################################
class LambdaExpr(object):
    def eval(self):
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
class Var(LambdaExpr):
    def __init__(self, var):
        self.var = var
    def eval(self):
        return self
    def app(self, argument):
        return Application(self, argument)
    def sub(self, var, expr):
        return self if self.var != var else expr
    def free(self):
        return set([self.var])
    def __str__(self):
        return self.var

##########################################################################
class Abstraction(LambdaExpr):
    def __init__(self, param, body):
        self.param = param
        self.body = body
    def eval(self):
        return Abstraction(self.param, self.body.eval())
    def app(self, argument):
        return self.body.sub(self.param, argument)
    def sub(self, var, expr):
        if self.param == var:
            return self
        if self.param in expr.free():
            f = fresh()
            return Abstraction(f, self.body.sub(self.param, f)).sub(var, expr)
        return Abstraction(self.param, self.body.sub(var, expr)) 
    def free(self):
        return self.body.free() - set([self.param])
    def __str__(self):
        return "(L%s.%s)" % (self.param, str(self.body))

##########################################################################
class Application(LambdaExpr):
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def eval(self):
        return self.first.eval().app(self.second.eval())
    def app(self, argument):
        return Application(self, argument)
    def sub(self, var, expr):
        return Application(self.first.sub(var, expr), self.second.sub(var, expr))
    def free(self):
        return self.first.free().union(self.second.free())
    def __str__(self):
        return "(%s %s)" % (str(self.first), str(self.second))

##########################################################################
def parse(data):
    return Application(Abstraction("x", Var("x")), Abstraction("x", Var("x")))
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="path to lambda calc file", type=str)
    args = parser.parse_args()
    with open(args.file) as f:
        expr = parse(f.read())
        print(expr.eval())

if __name__ == "__main__":
    main()
