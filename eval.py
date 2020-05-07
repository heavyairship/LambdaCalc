import argparse, sys

counter = -1
def fresh():
    global counter
    counter += 1
    return "@%d" % counter

def resetFresh():
    global counter
    counter = -1

##########################################################################
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
        
def testReduction():
    # Simple formulas
    assert str(Var("x").red()) == "x"
    assert str(Abs("x", Var("M")).red()) == "(Lx.M)"
    assert str(App(Var("M"), Var("N")).red()) == "(M N)"

    # Applications of variables
    assert str(App(Var("x"), Var("y")).red()) == "(x y)"
    assert str(App(Var("x"), Abs("x", Var("M"))).red()) == "(x (Lx.M))"
    assert str(App(Var("x"), App(Var("M"), Var("N"))).red()) == "(x (M N))"

    # Applications of basic abstractions
    assert str(App(Abs("x", Var("x")), Var("x")).red()) == "x"
    assert str(App(Abs("x", Var("x")), Abs("x", Var("x"))).red()) == "(Lx.x)"
    assert str(App(Abs("x", Var("x")), App(Var("M"), Var("N"))).red()) == "(M N)"


    # Application of abstraction with capture-avoiding substitution
    assert str(App(Abs("x", Var("M")), Var("x")).red()) == "M"
    assert str(App(Abs("x", Var("M")), Var("z")).red()) == "M"
    assert str(App(Abs("x", Var("x")), Var("r")).red()) == "r"
    assert str(App(Abs("x", Var("y")), Var("r")).red()) == "y"
    assert str(App(Abs("x", App(Var("t"), Var("s"))), Var("r")).red()) == "(t s)"
    assert str(App(Abs("x", App(Var("x"), Var("x"))), Var("r")).red()) == "(r r)"
    assert str(App(Abs("x", Abs("x", Var("t"))), Var("r")).red()) == "(Lx.t)"
    body = Abs("x", App(Var("x"), Var("y")))
    abst = Abs("y", body)
    assert str(App(abst, Var("x")).red()) == "(L@0.(@0 x))" # renaming example (alpha-conversion)
    resetFresh()

    # Application of applications
    assert str(App(App(Var("M"), Var("N")), Var("x")).red()) == "((M N) x)"
    assert str(App(App(Var("M"), Var("N")), Abs("x", Var("x"))).red()) == "((M N) (Lx.x))"
    assert str(App(App(Var("M"), Var("N")), App(Var("A"), Var("B"))).red()) =="((M N) (A B))"

def main():
    testReduction()
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="path to lambda calc file", type=str)
    args = parser.parse_args()
    with open(args.file) as f:
        expr = parse(f.read())
        print(expr.red())

if __name__ == "__main__":
    main()
