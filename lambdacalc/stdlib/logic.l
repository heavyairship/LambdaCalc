let true = (Lx.(Ly.x));
let false = (Lx.(Ly.y));
let && = (Lm.(Ln.(Lx.(Ly.((m ((n x) y)) y)))));
let || = (Lm.(Ln.(Lx.(Ly.((m x) ((n x) y))))));
let ! = (Lm.(Lx.(Ly.((m y) x))));
let -> = (Lm.(Ln.((|| (! m)) n)));
((-> false) true)
