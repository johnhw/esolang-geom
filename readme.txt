=== Geom ===

Geom is a simple esoteric language roughly in the style of Forth. 
It has a small number of primitive operations, each given by a 
single character. Geom's unique point (pardon the pun) is that 
its only datatype are two-dimensional points, and its only operators 
are Euclidean geometric operations. In other words, the only things 
that can be done to points are to draw circles and (infinite) lines
through them, and find intersections of these.

Geom has a stack, which contains points or nils, and a dictionary,
which maps tokens to variables or code. Tokens are space separated. 
Geom has lexical scoping, so definitions within an executed word do
not leak into the calling namespace.

It is unclear whether Geom is Turing-complete.


--- Running

Make sure you have Python installed. Then:

python geom.py file.geom

will generate file.svg 

If you want to turn on drawing of all construction lines and
labelling of points, you can do:

python geom.py file.geom -d

--- Operators

 @ Circle
 / Line
 > Variable
 :; Define
 [|] If-then-else
 - Draw

--- Details

At the start of the program there are two points on the stack: 
(0,0) and (1,0). Geom remembers the previous geometric operation, and computes the 
intersection between it and new geometric operations.

Intersections always occur in a defined order:

    * Two lines have at most one intersection.
    
    * Two circles can have two intersections; the first intersection 
    is the first point clockwise from the line which joins the centers of the circles.
    
    * A line and circle can have two intersections. The first point is
    the the point in the direction the line is running (even though 
    lines are infinite, they have a direction defined by the order they 
    are defined). If both intersections are on this side of the ray, 
    then the nearest point is returned first. 

    * @ Circle. a b -- c d 

Compute (but don't draw) a circle between the top two stack points, and 
intersect it with the previous geometric object. Puts two new points on 
the stack, which can be nil, if there are not enough intersections (e.g.
 nil, nil if no intersections, pt, nil if one intersection or pt, pt if 
 there are two).


    * / Line. a b -- c d 

Compute (but don't draw) an (infinite) line between top stack entries, and 
intersect with previous line/circle. Puts intersection points back on stack.


    * > Variable. a -- 

Define variable from stack. Takes top of stack and associates it with the 
following token. The token will put that value back on the stack the next 
time it occurs.


    *  : Define. -- 

Defines a new word which will execute a block of code. Format is as Forth: 
: word definition here ; Can be nested, and definitions will be locally scoped.


    * - Draw arc. a b c -- 

Draws an arc through the top three stack points, from a -> c with radius b. 
If a==c, draws a full circle. If a==b, draws a straight line.


    * [ If-then-else. -- 

Begins a conditional. Form is [ if not nil | if nil ]. If stack top is nil, 
executes the second part, otherwise executes the first part. Can be nested.

    * . -- 

Print stack to console. Not really a command, but a handy debugging tool.


