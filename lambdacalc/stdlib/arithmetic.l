let succ = Ln.Lf.Lx.f (n f x);
let ++ = succ;

let pred = Ln.first (n (Lp.pair (second p) (succ (second p))) (pair 0 0));
let -- = pred;

let add = Lm.Ln.Lf.Lx.(m f) (n f x);
let + = add;

let sub = Lm.Ln.n pred m;
let - = sub;

let mul = Lm.Ln.Lx.m (n x);
let * = mul;

let pow = Lm.Ln.n m;
let ^ = pow;

let iszero = Ln.n (Lx.false) true;
let gte = Lm.Ln.iszero (- n m);
let eq = Lm.Ln.&& (gte m n) (gte n m);
let neq = Lm.Ln.! (eq m n);
let <> = neq;

let fact = Ln.first (n ((Lp.pair (* (first p) (second p)) (++ (second p)))) (pair 1 1));
