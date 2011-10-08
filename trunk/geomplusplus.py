## Geom interpreter
## J. Williamson 2011
## Distributed in the public domain.

import sys, os, random, threading, Queue
from optparse import OptionParser
from geo import length   
from math import floor

try:
    # use symbolic solver if it's available
    from sympy import Rational, sqrt, atan2, pi    
    symbolic = True
except ImportError:
    print "You don't have SymPy (http://sympy.org) installed. Falling back to floating point solver."
    # use float solver if no sympy
    from math import sqrt, atan2, pi
    def Rational(x):
        return x
    symbolic = False

from geo import *
from svg_output import *
from tk_output import *
        
        
class Geom:
    circle = 0
    line = 1
    def __init__(self, type, pt1, pt2):
        self.type = type
        self.pt1 = pt1
        self.pt2 = pt2
        

class Nil:
    def __init__(self):
        self.uid = random.getrandbits(64)
        
    def __hash__(self):
        return self.uid
        
    def __eq__(self, object):
        return isinstance(object, Nil) and self.uid == object.uid
    
    def __ne__(self, object):
    
        return not isinstance(object, Nil) or self.uid != object.uid
        
    def __repr__(self):
        return "nil"
        
    def __str__(self):
        return "nil"
        
    def __nonzero__(self):
        return False


def quantize(pt):
    """Quantize a point so that it falls exactly on a grid line"""
    eps = 1e5
    if isinstance(pt, Nil):
        return pt
    else:
        x, y = pt
        x = floor(x * eps+0.5)/float(eps)
        y = floor(y * eps+0.5)/float(eps)
        return (x,y)        
    
        
def split_indices(text):
    # split text into space separated tokens
    # along with the indices of those tokens
    text = text.strip()
    cur = 0
    tokens = []
    
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    indices = []
    while 1:
        end = text.find(' ',cur)                        
        token = text[cur:end].strip()     
        if end==-1:
            break                    
        if len(token)>0:
            indices.append((cur,end))
            tokens.append(token)        
        cur = end+1
      
    
    token = text[cur:].strip()     
    if len(token)>0:
        indices.append((cur,end))
        tokens.append(token)                        
    return zip(tokens, indices)                                   
        
    
class GeomLang:
    def __init__(self, code, filename, debug=False, interactive=False):
        # initialise stack

        self.stack = [(Rational(0),Rational(0)), (Rational(1),Rational(0))]
        self.dictionary = {}
        self.interactive = interactive
        self.dictionaries = []
        self.continuation = {}
        self.continuations = []
        self.current_tag_point = Nil()
        self.debug = debug
        self.eps = 1e-4
        self.filename = filename
        
        self.code = code        
        # create the output function 
        self.output = SVGOutput()                
        self.highlight = [0,0]
        self.string_stack = ""
            
            
            
        self.geoms = []
        
        for pt in self.stack:
            if pt:
                self.output.point(pt)
                        
        tokens = split_indices(self.code)        
        if self.interactive:                    
            # start the parser in another thread
            
            in_queue = Queue.Queue()            
            out_queue = Queue.Queue()            
            interactive_output = TKOutput(out_queue, in_queue)
            out_queue.put(("code", self.code), block=False)
            parse_thread = threading.Thread(target=self.do_parse, args=(tokens,),kwargs={"in_queue" : in_queue, "out_queue":out_queue})                        
            
            for pt in self.stack:
                if pt:                         
                    interactive_output.transient_point(pt)        
            parse_thread.start()
            interactive_output.start()                        
        else:
            self.do_parse(tokens)            
        
               
                    
    # compute the intersection of the last two geometric operations
    def intersect(self, g):
        self.geoms.append(g)
        if len(self.geoms)>1:
            self.geoms = self.geoms[-2:]
                    
            first_geom = self.geoms[0]
            second_geom = self.geoms[1]
            f, s = first_geom, second_geom
            a, b, c, d = f.pt1, f.pt2, s.pt1, s.pt2
            if f.type==Geom.line and s.type==Geom.line:            
                intersections = full_line_intersect(a,b,c,d)
                
            if f.type==Geom.line and s.type==Geom.circle:            
                intersections = line_circle_intersect(a,b,c,d)
                
            if  s.type==Geom.line and f.type==Geom.circle:
                # reverse in this case
                intersections = line_circle_intersect(c,d,a,b)
                
            if f.type==Geom.circle and s.type==Geom.circle:            
                if not symbolic and length(a,b)<self.eps:
                    # don't interesect circles < eps apart!
                    intersections=[]
                else:
                    intersections = circle_circle_intersect(a,b,c,d)
                
            for intersection in intersections:                
                self.output.point(intersection)
                self.push(intersection)
            
            # fill any remaining gaps
            if len(intersections)==1:
                self.push(Nil())
                
            if len(intersections)==0:
                self.push(Nil())
                self.push(Nil())
        else:
            self.push(Nil())
            self.push(Nil())
                
         
                
    def push(self, pt):        
        if not symbolic:
            pt = quantize(pt)
        
        if self.interactive:
            self.out_queue.put(("transient_point", (pt)), block=False)
        self.stack.append(pt)
        
        
    def pop(self):        
        if len(self.stack)>0:
            p = self.stack.pop()
            if not symbolic:
                return quantize(p)
            else:
                return p            
        else: 
            return Nil()
            
                
    def draw_arc(self):
        p1 = self.pop()
        p2 = self.pop()
        p3 = self.pop()
        if p1 and p2 and p3:            
            if length(p1,p3)<self.eps:                                
                self.output.circle(p1, p2, debug=False)
                if self.interactive:                
                    self.out_queue.put(("circle", (p1,p2)), block=False)           
            elif length(p1,p2)<self.eps:                
                self.output.line(p1, p3, debug=False)            
                if self.interactive:                
                    self.out_queue.put(("line", (p1,p2)), block=False)
                    
                        
            elif length(p1,p3)<self.eps and length(p1,p2)<self.eps:
                self.output.point(p1, debug=False)                        
                if self.interactive:                
                    self.out_queue.put(("point", (p1)), block=False)
                    
            else:
                self.output.arc(p1, p2, p3)
                if self.interactive:                
                    self.out_queue.put(("arc", (p1,p2,p3)), block=False)
                    
        
    def circle(self):
        # create, but don't draw, a circle
        p1 = self.pop()
        p2 = self.pop()
        if p1 and p2:
            g = Geom(Geom.circle, p1, p2)        
            self.intersect(g)
            if self.debug:
                self.output.circle(p1, p2)
            if self.interactive:                
                self.out_queue.put(("transient_circle", (p1,p2)), block=False)
                
        
        
    def line(self):
        p1 = self.pop()
        p2 = self.pop()                
        if p1 and p2:
            g = Geom(Geom.line, p1, p2)        
            self.intersect(g)
            if self.debug:
                self.output.inf_line(p1, p2)
            if self.interactive:                
                self.out_queue.put(("transient_line", (p1,p2)), block=False)
        
            
            
        
        
    def get_string_stack(self):
        stack_string = []
        for elt in self.stack:
                if isinstance(elt,tuple):
                    stack_string.append("[%.02f, %.02f]" % (elt[0], elt[1]))
                else:
                    stack_string.append(str(elt))
        stack_string.append("<<")
        stack_string = " ".join(stack_string)
        return stack_string
    
    def do_parse(self, tokens,in_queue=None,out_queue=None):
        self.out_queue = out_queue
        self.parse(tokens, in_queue, out_queue)
        self.output.write(filename=self.filename)      
        
        if self.interactive:
            self.out_queue.put(("terminate", ()), block=False)
            
            
    # parse the entire string
    def parse(self,tokens, in_queue=None, out_queue=None):                
    

        while len(tokens)>0:            
            token,index = tokens.pop(0)            
                
                
            self.out_queue.put(("highlight", index), block=False)
            self.out_queue.put(("stack", self.get_string_stack()), block=False)
            
            # wait for gui if we need to 
            if in_queue:
                in_queue.get()
                
            self.highlight = index
            self.string_stack = self.get_string_stack()            
            
            # circle
            if token=='@':
               self.circle()
                              
            # line
            elif token=='/':
                self.line()
                 
            # raw token
            elif isinstance(token, (Nil, tuple)):
                self.push(token)
             
            # define
            elif token=='(':                 
                pt = self.pop()                
                defn = []
                                
                cnt = 1
                while cnt!=0:         
                    if len(tokens)==0:
                        print "%s definition missing terminating ) " % name
                        sys.exit(-1)
                    
                    token,index = tokens.pop(0)                                                            
                    if token=='(':
                        cnt = cnt + 1
                    if token==')':
                        cnt = cnt - 1                                            
                        
                    if cnt==1 and token=='^':
                        p = self.pop()                        
                        defn.append((p, index))
                    else:
                        defn.append((token,index))                    
                
                self.dictionary[pt] = defn[0:-1]
                self.push(pt)
            
                
            # variable
            elif token=='>':               
                name,index = tokens.pop(0)                                                                
                p1 = self.pop()
                
                self.dictionary[name] = p1
                if self.debug and p1:
                    self.output.text(p1, name)
                
            # conditional
            elif token=='?':               
                p1 = self.pop()
                p2 = self.pop()
                p3 = self.pop()
                
                if p3:
                    self.push(p1)
                else:
                    self.push(p2)
                                                 
            
            elif token=='*':
                p1 = self.pop()
                self.current_tag_point = p1
                       
                code = self.dictionary.get(p1, [])                
                
                # preserve state
                self.dictionaries.append(self.dictionary)                    
                self.dictionary = dict(self.dictionary)                                                                        
                self.continuations.append(self.continuation)
                self.continuation = dict(self.continuation)                                                                        
                
                # replace with current continuation if there is one
                code,context = self.continuation.get(p1, (code, (self.dictionary, self.continuation)))
                self.dictionary = context[0]
                self.continuation = context[1]
                
                
                continuation = self.parse(list(code), condition=condition)
                
                # restore state
                self.dictionary = self.dictionaries.pop()                        
                self.continuation = self.continuations.pop()                        
                
                # record continuation
                if continuation:
                    self.continuation[p1] = continuation
                else:
                    if self.continuation.has_key(p1):
                        del self.continuation[p1] 
                    
            # draw 
            elif token=='-':              
                self.draw_arc()
                
            # yield
            elif token=='|':              
                continuation = tokens
                return continuation, (dict(self.dictionary), dict(self.context))
            
            # print stack
            elif token=='.':                
    
                print self.get_string_stack()
                
                
            
            # print dictionary
            elif token=='!':
                print "--- Dictionary ---"
                for key in self.dictionary:
                    if isinstance(key, str):
                        s = self.dictionary.get(self.dictionary[key], "")
                        print "%s : %s -> %s" % (key, self.dictionary[key], s)
                    else:
                        print "%s : %s" % (key, self.dictionary[key])
                    
                print "--- Continuations ---"
                for key in self.continuation:
                    print "%s : %s" % (key, self.continuation[key])
                
                
            # print string
            elif token=='"':
                cnt = 1
                old_tokens = list(tokens)
                quoted = []
                while cnt!=0:         
                    if len(tokens)==0:
                        print "Mismatched quotes %s"  %old_tokens
                        sys.exit(-1)                    
                    token, index = tokens.pop(0)                                                                                
                    if token=='"':
                        cnt = cnt - 1                                            
                    else:
                        quoted.append(token)
                        
                print " ".join(quoted)
            
                
                
            # lookup in dictionary
            else:
                v = self.dictionary.get(token, None)                                
                if v!=None:                    
                    self.push(v)
                
                
        
                        
    
def start_geom():
        usage = "usage: %prog [options] file.geompp"        
        parser = OptionParser(usage=usage)
        parser.add_option("-d", "--debug", dest="debug", help="enable drawing of construction geometry, and label points", action="store_true", default=False)
        parser.add_option("-i", "--interactive", dest="interactive", help="enable interactive drawing on a Tk canvas", action="store_true", default=False)
        options, args = parser.parse_args()
        
        if len(args)!=1:
            parser.print_help()
            sys.exit(0)
            
        
        filename = args[0]                
        base, ext = os.path.splitext(filename)
        file = open(sys.argv[1], "r").read()
        g = GeomLang(file, base, debug=options.debug, interactive=options.interactive)
        print "Wrote to %s.svg" % base
        
if __name__=="__main__":
        start_geom()
                
                
                               
        
        
        
        
   
 
            
                   
        
    