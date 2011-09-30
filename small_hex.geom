: under > x > y  x y x ;
: hex_segment > x > y  x y @ drop drop y x @ drop > p x p p - p ;
: neq > a > b a b @ drop drop b a @ drop ;
: hex_loop  > x > y y x under hex_segment > p p a neq [ y p hex_loop | ] ;
> a > b b a b - b a 
hex_loop
