=== Geom++ ===

Geom++ is an extension of Geom, which is a stack-based simple esoteric language. Like Geom, Geom++'s only datatype is two-dimensional points, and its only operators are Euclidean geometric operations. Geom++ adds a small number of operators that substantially increase the expressive power of the language. In particular, code fragments are linked to points (or, more precisely, continuations are linked to points which are linked to names), so that "functions" become first-class objects.

Geom++ has a stack, which contains points or nils, a dictionary, which maps tokens to points and points to continuations. Geom++ has lexical scoping, so definitions within an executed word do not leak into the calling namespace. In addition to Geom's functionality, Geom++ also supports closures, coroutines, partial application and anonymous functions.

The implementation uses exact symbolic solving (when SymPy is installed) and thus suffers no accuracy loss from repeated operations.

--- Running

Make sure you have Python installed. Install SymPy (http://sympy.org) if you want exact algebraic solving. Then:

python geomplusplus.py file.gpp

will generate file.svg 

If you want to turn on drawing of all construction lines and
labelling of points, you can do:

python geomplusplus.py file.gpp -d

Interactive mode can be enabled with -i:

python geomplusplus.py file.gpp -i

In interactive mode, pressing "s" single-steps through the code and "p" pauses/resumes the execution of code.


--- Operators

 @ Circle
 / Line
 > Variable
 ( ) Link
 ^ Bake
 * Execute
 | Yield
 " Print string  
 ? If-then-else
 - Draw

--- Details

As with Geom, at the start of the program there are two points on the stack: (0,0) and (1,0). Geom++ remembers the previous geometric operation, and computes the intersection between it and new geometric operations.

Intersections follow the Geom rules:

    * Two lines have at most one intersection.
    * Two circles can have two intersections; the first intersection is the first point clockwise from the line which joins the centers of the circles.
    * A line and circle can have two intersections. The first point is the the point in the direction the line is running (even though lines are infinite, they have a direction defined by the order they are defined). If both intersections are on this side of the ray, then the nearest point is returned first. 

 @ Circle. a b -- c d 
Compute (but don't draw) a circle between the top two stack points, and intersect it with the previous geometric object. Puts two new points on the stack, which can be nil, if there are not enough intersections (e.g. nil, nil if no intersections, pt, nil if one intersection or pt, pt if there are two).

 / Line. a b -- c d 
Compute (but don't draw) an (infinite) line between top stack entries, and intersect with previous line/circle. Puts intersection points back on stack.

 > Variable. a -- 
Define variable from stack. Takes top of stack and associates it with the following token. The token will put that value back on the stack the next time it occurs.

 ( ) Link. a -- a
Takes a block of code, and links it to the point on top of the stack (the point is left on the stack). Note that all nils are unique, so linking to a "different" nil will not replace the first definition.

 - Draw arc. a b c -- 
Draws an arc through the top three stack points, from a -> c with radius b. If a==c, draws a full circle. If a==b, draws a straight line. If a==b==c, draws a point.

 ? If-then-else. a b c -- d
If stack top is non-nil, then keep b, else keep a.

 * Execute. a --
Look up the code associated with the point on top of the stack, and execute it.

 ^ Bake. a -- 
Bake the top of stack entry into the current definition. Bake is executed at definition-time. So ( ^ @) defines a bit of code which when called will compute a circle between whatever was on top of stack at definition time, and what is on the stack at call-time (in other words partial application).

 | Yield. --
Return to the calling definition. The caller can return to the callee by executing (with *) again. Continuations are linked to points, and are scoped with the same rules as variables. So:

make_nil * ( " a " | " b " | " c " ) > print
make_nil * ( print * ) > t1
make_nil * ( print * ) > t2
t1 *
t1 *
t2 *
t1 > t2
t2 * 

prints "a b a c"

Note that the way that Geom++ is scoped, a continuation has the variables bound when it was originally called until it finally returns, even if those are overwritten by the caller in the meantime.


 " --
Print the string up until the matching quote. Mainly for debugging. Note, that like Forth, quotes must be space separated:

" This will be printed "
"This will not"

--- Debugging commands 

 . --

Print stack to console.

 ! --

Print dictionaries and continuations to console.

--- Converting Geom

Being able to make "new" nils is important in Geom++:

> origin > unit
origin origin @ > _ ( origin origin @ > _ ) > nil
nil * ( " message " ) > print_message
nil * ( " Hello, world! " ) > print_hello_world
print_message *
print_hello_world *

The only things that need changed to convert Geom to Geom++ are calling conventions (* must be put after tokens to execute them), colon definitions and if-then-else:

: dup > a a a ; dup               // Geom
nil * ( > a a a ) > dup dup *     // Geom++

a [ stuff | other ]               // Geom
stuff other a ? *                 // Geom++



