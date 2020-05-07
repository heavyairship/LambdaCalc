import sys
from optparse import OptionParser
from lambda_calc import *

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

    print("Unit tests for reductions passed!")

def main():
    print("Running unit tests...")
    testReduction()

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", help="path to lambda calc file", type=str)
    (options, args) = parser.parse_args()
    if options.filename:
        print("Running test file...")
        with open(options.filename) as f:
            expr = parse(f.read())
            assert str(expr.red()) == "((M N) y)"
            print("Test file passed!")

if __name__ == "__main__":
    main()
