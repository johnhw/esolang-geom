: rem Basic arithmetic in Geom ;

: rem store original points ;
> unit > origin origin unit


: dup > a a a ;             : rem duplicate stack top ;
: dup2 > a > b b a b a ;    : rem duplicate two top entries ;
: drop_under > a > b a ;    : rem drop second entry ;
: drop > _ ;                : rem drop top entry ;
: drop2 > _ > _ ;           : rem drop top two entries ;
: swap > a > b a b ;        : rem swap top two entries ;

: rem return nil if point are equal ;
: neq > a > b a b @ drop drop b a @ drop ;

: rem extend a line along a vector ;
: extend > a > b a b @ drop2 a b / drop > d a d ;

: rem given a,b,c return if nil if a is not inside a circle from b->c ;
: circle_inside > d > a > b  b a extend > c c a @ drop2 a d @ drop drop_under ;


: rem given a,b produce c, which is the projection from b along a->b ;
: inc > b > a a b @ drop2 b a / > c drop b c ; 

: rem given a,b produce c, which is the projection from a along b->a ;
: dec > a > b a b @ drop2 a b / drop > c c b ;

: rem bisect a,b and return the midpoint ;
: bisect > a > b a b @ drop2 b a @ > c > d a b / drop2 c d / drop > e e ;

: rem given a,b, return c,d where c is twice as far from the origin as b, and d = c + (b-a) ;
: double > a > b origin a inc drop_under origin b inc drop_under > b > a a b bisect a ;

: rem given a,b, return c,d where c is half as far from the origin as b, and d = c + (b-a) ;
: halve > a > b origin a bisect origin b bisect > b > a b a dec drop a  ;

: rem given a,b, return b,c where c = b + ((b-a).y, (b-a).x) ;
: up > a > b  b a @ drop2 a b @ > c > d  b a inc > a > b b a @ drop2 a b @ > e > f d f bisect > g a b @ drop2 g b / drop > h b h ;

: rem given a, return a point b which is sqrt(|b|) away from the origin in the same direction ;
: sqrt > b  unit origin @ drop2 b origin / drop > a  a b bisect > c unit origin up drop_under > p a c @ drop2 origin p / drop_under ;

.       : rem (0,0) (1,0) ;
inc .   : rem (1,0) (2,0) ;
inc .   : rem (2,0) (3,0) ;
inc .   : rem (3,0) (4,0) ;
inc .   : rem (4,0) (5,0) ;
inc .   : rem (5,0) (6,0) ;
halve . : rem (2,0) (3,0) ; 
inc .   : rem (3,0) (4,0) ;
up  .   : rem (4,0) (4,1) ;
inc .   : rem (4,1) (4,2) ;
dec .   : rem (4,0) (4,1) ;

drop2

: rem square root test ;
origin unit inc drop_under sqrt  ;

: rem insideness test ;

origin unit inc inc inc > p1 drop       : rem p1 = (4,0) ;
origin unit bisect > p2                 : rem p2 = (0.5, 0) ; 

p1 origin unit circle_inside . drop     : nil, p1 not closer to origin than unit ;
p2 origin unit circle_inside . drop     : non-nil, p2 closer to origin than unit ; 
