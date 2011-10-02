## Geom interpreter
## J. Williamson 2011
## Distributed in the public domain.

import sys, os, random
from xml.etree import ElementTree as et    
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


def length(start, end):
    return sqrt((start[0]-end[0])*(start[0]-end[0])+(start[1]-end[1])*(start[1]-end[1]))
           
def normal(v):
    return (-v[1], v[0])
    
def normalize(v):
    m = length((0,0),v)
    return (v[0]/m, v[1]/m)
    
def sub(a,b):
    return (b[0]-a[0], b[1]-a[1])

def add(a,b):
    return (a[0]+b[0], a[1]+b[1])

    
def dot(v1,v2):
    return v1[0]*v2[0]+v1[1]*v2[1]

# interesection point of two lines
def full_line_intersect(p1, p2, p3, p4):
    denom = (p4[1]-p3[1])*(p2[0]-p1[0]) - (p4[0]-p3[0])*(p2[1]-p1[1])        
    if denom==0:
        return []
        
    ua_nom =(p4[0]-p3[0])*(p1[1]-p3[1]) - (p4[1]-p3[1])*(p1[0]-p3[0])
    ub_nom =(p2[0]-p1[0])*(p1[1]-p3[1]) - (p2[1]-p1[1])*(p1[0]-p3[0])
    
    #return none if coincident
    if ua_nom == 0:            
        return []
    if ub_nom == 0:
        return []
    
    
    ua = ua_nom / denom
    ub = ub_nom / denom
        
    x = p1[0]+ua*(p2[0]-p1[0])
    y = p1[1]+ua*(p2[1]-p1[1])
    return [(x,y)]
    
    


# line circle intersection (points are line p1->p2, circle centered p3, p4 on radius)  
def line_circle_intersect(p1, p2, p3, p4):
    r = sqrt((p3[0]-p4[0])*(p3[0]-p4[0])+(p3[1]-p4[1])*(p3[1]-p4[1]))
    
    a = (p2[0]-p1[0])*(p2[0]-p1[0])+(p2[1]-p1[1])*(p2[1]-p1[1])
    b = 2 * ((p2[0]-p1[0])*(p1[0]-p3[0])+(p2[1]-p1[1])*(p1[1]-p3[1]))
    c = p3[0]*p3[0] + p3[1]*p3[1] + p1[0]*p1[0]+p1[1]*p1[1] - 2 * (p3[0]*p1[0]+p3[1]*p1[1]) - r*r
    
    
    det = b*b-4*a*c
    if det<0 or a==0.0:
        return []
        
    if det==0:
        u = -b/(2*a)
        x = p1[0]+u*(p2[0]-p1[0])
        y = p1[1]+u*(p2[1]-p1[1])
        return [(x,y)]
        
    if det>0:
          u = (-b + sqrt(b*b - 4*a*c )) / (2*a)
          x1 = p1[0]+u*(p2[0]-p1[0])
          y1 = p1[1]+u*(p2[1]-p1[1])
          u = (-b - sqrt(b*b - 4*a*c )) / (2*a);
          x2 = p1[0]+u*(p2[0]-p1[0])
          y2 = p1[1]+u*(p2[1]-p1[1])
          
          pts = [(x1,y1), (x2,y2)]
          
          # sort according to direction and distance
          # direction first, then nearest if both same
          
          # get vector
          l1 = length(p1, (x1,y1))
          l2 = length(p1, (x2,y2))
          
          # distance order
          if l1<l2:
            pts = [(x1,y1), (x2,y2)]
          else:
            pts = [(x2,y2), (x1,y1)]
            
          # return immediately if points are co-located
          if l1==0 or l2==0:            
            return pts
          
          v1 = normalize(sub(p1, p2))
          v2 = normalize(sub(p1, (x1,y1)))
          v3 = normalize(sub(p1, (x2,y2)))
          dp1 = dot(v1,v2)
          dp2 = dot(v1,v3)
        
          
          # now re-order if direction is wrong
          # i.e make sure we return always the point in the direction
          # the ray is facing first, if there is one
          if dp1>0 and dp1<0:
            pts = [(x1,y1), (x2,y2)]
          if dp1<0 and dp1>0:
            pts = [(x2,y2), (x1,y1)]
            
          
          
          return pts
                                  

# return intersection of circles
def circle_circle_intersect(p1, p2, p3, p4):
        r0 = sqrt((p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1]))
        r1 = sqrt((p3[0]-p4[0])*(p3[0]-p4[0]) + (p3[1]-p4[1])*(p3[1]-p4[1]))
        d = sqrt((p1[0]-p3[0])*(p1[0]-p3[0])+(p1[1]-p3[1])*(p1[1]-p3[1]))
        
        if d>r0+r1:
            return []
            
        if d<r0-r1:
            return []
            
        if d==0:
            return [] 
            
        a = (r0*r0 - r1*r1 + d*d) / (2*d)
        
        if a==0.0:
            return []
            
        if r0*r0-a*a<=0.0:
            return []
            
        
        x2 = p1[0] + (p3[0]-p1[0])*(a/d)
        y2 = p1[1] + (p3[1]-p1[1])*(a/d)
        
        
        h = sqrt((r0*r0) - (a*a))
        rx = -(p3[1]-p1[1]) * (h/d)
        ry = (p3[0]-p1[0]) * (h/d)
        
        xa = x2+rx
        xb = x2-rx
        ya = y2+ry
        yb = y2-ry
        
        if xa==xb and ya==yb:
            return [(xa,ya)]
        
        # now sort so that the first intersection is always clockwise
        # from the line joining the centres (wrt the first centre)
        cline = normal(normalize(sub(p1,p3)))
        aline = normalize(sub(p1,(xa,ya)))
        bline = normalize(sub(p1,(xb,yb)))
        
        dp1 = dot(cline, aline)
        dp2 = dot(cline, bline)
        
        if dp1<0 and dp2>0:
            return [(xb,yb), (xa,ya)]
        else:
            return [(xa,ya), (xb, yb)]
                

                
# return true if p1 is inside circle from p2 to p2
def circle_inside(p1, p2, p3):
    r = length(sub(p2,p3))
    d = length(sub(p1,p2))
    return d<=r
    
    
# return true if p1 is left of p2->p3
def line_inside(p1, p2, p3):
        cline = normal(normalize(sub(p2,p3)))
        aline = normalize(sub(p2,p1))        
        dp1 = dot(cline, aline)        
        return dp1>0

                



        

class SVGElement(object):
    circle = 0
    line = 1
    text = 2
    arc = 3
    point = 4
    def __init__(self, type, pts, debug=False, text=""):
        self.type = type
        self.pts = pts
        self.text = text
        self.debug = debug

class SVGOutput(object):
    def __init__(self):
        self.elements = []
        self.pt_texts = {}
        self.inf_lines = []
        
    def textnow(self, p1, t):                
        self.elements.append(SVGElement(type=SVGElement.text, pts=[p1], text=t))
                
        
    # add to the text to be drawn at the current point
    def text(self, pt, c):
        # quantize pt
        if not c.startswith('_'):
            self.pt_texts[pt] = self.pt_texts.get(pt, "") + c + " "
        
        
    def point(self, p1, debug=False):                
        self.elements.append(SVGElement(type=SVGElement.point, pts=[p1], debug=debug))
                           
        
    def circle(self, p1, p2, debug=True):                   
        self.elements.append(SVGElement(type=SVGElement.circle, pts=[p1, p2], debug=debug))
        
        
    def line(self, p1, p2, debug=False):           
        self.elements.append(SVGElement(type=SVGElement.line, pts=[p1, p2], debug=debug))
        
        
    def arc(self, p1, p2, p3):
        l = length(p1, p2)
        v1 = sub(p1, p2)
        v2 = sub(p1, p3)
        
        a1 = atan2(v1[1], v1[0])
        a2 = atan2(v2[1], v2[0])
        
        self.elements.append(SVGElement(type=SVGElement.arc, pts=[p1, p2], debug=False))
                
        
        
    def inf_line(self, p1, p2):           
        self.inf_lines.append((p1, p2))
        
    
    def write_text(self): 
        for pt in self.pt_texts.keys():
            self.textnow(pt, self.pt_texts[pt])
                        
            
    def draw_inf_lines(self):
        bbox = self.get_bbox()
        
        bboxscale = 0.1
        
        
        y1 = bbox[2]-(bbox[3]-bbox[2])*bboxscale
        y2 =bbox[3]+(bbox[3]-bbox[2])*bboxscale
        x1= bbox[0]-(bbox[1]-bbox[0])*bboxscale
        x2 = bbox[1]+(bbox[1]-bbox[0])*bboxscale
        
        
        # get bounding box lines
        topline = ((x1,y1), (x2,y1))
        bottomline = ((x1,y2), (x2,y2))
        leftline = ((x1,y1), (x1,y2))
        rightline = ((x2,y1), (x2,y2))
              
        
        for line in self.inf_lines:
            pts = []
                    
            
            # get edge intersection
            itop = full_line_intersect(line[0], line[1], topline[0], topline[1])
            ibottom = full_line_intersect(line[0], line[1], bottomline[0], bottomline[1])
            ileft = full_line_intersect(line[0], line[1], leftline[0], leftline[1])
            iright = full_line_intersect(line[0], line[1], rightline[0], rightline[1])
            
            
     
            # ok, which lines are possible
            if itop!=[] and itop[0][0]>=x1 and itop[0][0]<=x2:
                
                pts.append(itop[0])
                
            if ibottom!=[] and ibottom[0][0]>=x1 and ibottom[0][0]<=x2:
                
                pts.append(ibottom[0])
                
            
            if ileft!=[] and ileft[0][1]>=y1 and ileft[0][1]<=y2:                
                pts.append(ileft[0])
            
            if iright!=[] and iright[0][1]>=y1 and iright[0][1]<=y2:                              
                pts.append(iright[0])
                
            if len(pts)>1:
                self.line(pts[0], pts[1], debug=True)
            
            
    def get_bbox(self): 
        minx = 1e6
        maxx = -1e6
        miny = 1e6
        maxy = -1e6
        for element in self.elements:
        
            pts = element.pts
            # for circles, we need to compute radius
            if element.type==SVGElement.circle or element.type==SVGElement.arc:
                r = length(pts[0], pts[1])                
                x1 = add(pts[0], (-r,0))
                x2 = add(pts[0], (r,0))
                y1 = add(pts[0], (0,-r))
                y2 = add(pts[0], (0,r))
                
                if x1[0]<minx:
                    minx=x1[0]
                if x2[0]>maxx:
                    maxx=x2[0]
                if y1[1]<miny:
                    miny=y1[1]                    
                if y2[1]>maxy:
                    maxy=y2[1]
                

            # compute bound of all points
            for pt in pts:
                if pt[0]<minx:
                    minx=pt[0]
                    
                if pt[0]>maxx:
                    maxx=pt[0]
                    
                if pt[1]<miny:
                    miny=pt[1]
                    
                if pt[1]>maxy:
                    maxy=pt[1]
        return [float(x) for x in [minx, maxx, miny, maxy]]
                    
        
    def write(self, filename="output"):
        self.write_text()
        self.draw_inf_lines()
        
        bbox = self.get_bbox()
        
        scale = 1000
        x_extent = (bbox[1] - bbox[0])
        y_extent = (bbox[3] - bbox[2])
        
        
        center = (bbox[0], bbox[2])
        doc = et.Element('svg', width=str(x_extent*scale), height=str(y_extent*scale), version='1.1', xmlns='http://www.w3.org/2000/svg')
        
        title = et.Element( "title")
        title.text ="Geom output for %s" % filename
        doc.append(title)
 
        # now points
        for element in self.elements:         
            # draw point
            pts = [(float(scale*(p[0]-center[0])), float(scale*(p[1]-center[1]))) for p in element.pts]
            if element.type==SVGElement.point and element.debug:                            
                r = 15
                et.SubElement(doc, 'circle', cx=str(pts[0][0]), cy=str(pts[0][1]), r=str(r), fill='rgb(255,0,0)')            
        
            
        # debug lines first        
        for element in self.elements: 
            if element.debug:
                stroke='rgb(100,100,100)'
                stroke_width = '2; stroke-opacity:0.3'
                
                stroke = "stroke: %s; stroke-width: %s" % (stroke, stroke_width)
                    
                # shift points by canvas offset
                pts = [(float(scale*(p[0]-center[0])), float(scale*(p[1]-center[1]))) for p in element.pts]
                
                # draw circle            
                if element.type==SVGElement.circle:                            
                    r = length(pts[0], pts[1])                
                    et.SubElement(doc, 'circle', cx=str(pts[0][0]), cy=str(pts[0][1]), r=str(r), style=stroke, fill='none')
                    
                # draw line
                if element.type==SVGElement.line:                                                
                    et.SubElement(doc, 'line', x1=str(pts[0][0]), y1=str(pts[0][1]),x2=str(pts[1][0]), y2=str(pts[1][1]), style=stroke)
                    
                
                # draw arc
                if element.type==SVGElement.arc:                                
                    r = length(pts[0], pts[1])                
                    path = "M%f,%f A %f,%f 0 0,0 %f, %f" % (pts[0][0], pts[0][1], r,r, pts[1][0], pts[1][1])
                    et.SubElement(doc, 'path', d=path, style=stroke, fill="none")
                    
        # other lines next
        for element in self.elements: 
            if not element.debug:
                stroke='rgb(0,0,0)'
                stroke_width = '10'
 
                stroke = "stroke: %s; stroke-width: %s" % (stroke, stroke_width)
                # shift points by canvas offset
                pts = [(float(scale*(p[0]-center[0])), float(scale*(p[1]-center[1]))) for p in element.pts]
                
                # draw circle            
                if element.type==SVGElement.circle:                            
                    r = length(pts[0], pts[1])                
                    et.SubElement(doc, 'circle', cx=str(pts[0][0]), cy=str(pts[0][1]), r=str(r), style=stroke, fill='none')
                
                # draw points
                if element.type==SVGElement.point:                            
                    r = 15
                    et.SubElement(doc, 'circle', cx=str(pts[0][0]), cy=str(pts[0][1]), r=str(r), fill='rgb(255,0,0)')            
                
                
                # draw line
                if element.type==SVGElement.line:                                                
                    et.SubElement(doc, 'line', x1=str(pts[0][0]), y1=str(pts[0][1]),x2=str(pts[1][0]), y2=str(pts[1][1]), style=stroke)
                    
                # draw arc
                if element.type==SVGElement.arc:                                
                    r = length(pts[0], pts[1])                
                    path = "M%f,%f A %f,%f 0 0,0 %f, %f" % (pts[0][0], pts[0][1], r,r, pts[1][0], pts[1][1])
                    et.SubElement(doc, 'path', d=path, style=stroke, fill="none")

        
        # text last
        for element in self.elements:         
            pts = [(float(scale*(p[0]-center[0])), float(scale*(p[1]-center[1]))) for p in element.pts]
            # draw text
            if element.type==SVGElement.text:                                            
                text = et.Element('text', x=str(pts[0][0]+20), y=str(pts[0][1]+20), fill='gray', style='font-family:Sans;font-size:72pt;text-anchor:center;dominant-baseline:middle')
                
                text.text = element.text
                doc.append(text)
         
        # ElementTree 1.2 doesn't write the SVG file header errata, so do that manually
        f = open('%s.svg' % filename, 'w')
        f.write('<?xml version=\"1.0\" standalone=\"no\"?>\n')
        f.write('<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\"\n')
        f.write('\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n')
        f.write(et.tostring(doc))
        f.close()
        
        
        
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
        
    
class GeomLang:
    def __init__(self, code, filename, debug=False):

        # initialise stack
        self.stack = [(Rational(0),Rational(0)), (Rational(1),Rational(0))]
        self.dictionary = {}
        self.dictionaries = []
        self.continuation = {}
        self.continuations = []
        
        self.debug = debug
        self.eps = 1e-4
                
        # create the output function 
        self.output = SVGOutput()        
        self.geoms = []
        
        for pt in self.stack:
            if pt:
                self.output.point(pt)
        # start parsing
        self.parse(code.split())                
        self.output.write(filename=filename)
        
               
                    
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
                
            elif length(p1,p2)<self.eps:
                
                self.output.line(p1, p3, debug=False)            
            elif length(p1,p3)<self.eps and length(p1,p2)<self.eps:
                self.output.point(p1, p3, debug=False)                        
            else:
                self.output.arc(p1, p2, p3)
                
        
    def circle(self):
        # create, but don't draw, a circle
        p1 = self.pop()
        p2 = self.pop()
        if p1 and p2:
            g = Geom(Geom.circle, p1, p2)        
            self.intersect(g)
            if self.debug:
                self.output.circle(p1, p2)
        
            
        
        
    def line(self):
        p1 = self.pop()
        p2 = self.pop()        
        if p1 and p2:
            g = Geom(Geom.line, p1, p2)        
            self.intersect(g)
            if self.debug:
                self.output.inf_line(p1, p2)
            
    # parse the entire string
    def parse(self,tokens):
        
        while len(tokens)>0:
            
            token = tokens.pop(0)
                        
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
                    
                    token = tokens.pop(0)                                                            
                    if token=='(':
                        cnt = cnt + 1
                    if token==')':
                        cnt = cnt - 1                                            
                        
                    if cnt==1 and token=='^':
                        p = self.pop()                        
                        defn.append(p)
                    else:
                        defn.append(token)                    
                
                self.dictionary[pt] = defn[0:-1]
                self.push(pt)
            
                
            # variable
            elif token=='>':               
                name = tokens.pop(0)                                                                
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
            
                code = self.dictionary.get(p1, [])
                
                # preserve state
                self.dictionaries.append(self.dictionary)                    
                self.dictionary = dict(self.dictionary)                                                                        
                self.continuations.append(self.continuation)
                self.continuation = dict(self.continuation)                                                                        
                
                # replace with current continuation if there is one
                code,context = self.continuation.get(p1, (code, (self.dictionary, self.contiunation)))
                self.dictionary = context[0]
                self.continuation = context[1]
                                
                continuation = self.parse(list(code))
                
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
                
                for elt in self.stack:
                    if isinstance(elt,tuple):
                        print "[%.02f, %.02f]" % (elt[0], elt[1])
                    else:
                        print elt,                    
                print "<<"
            
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
                    token = tokens.pop(0)                                                                                
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
                        
    
if __name__=="__main__":
    if len(sys.argv)<2:
        print "Usage: geomplusplus.py <file.geom> [-d]"
    else:
        filename = sys.argv[1]
        debug = False
        if len(sys.argv)>2 and sys.argv[2]=='-d':
            debug = True
        base, ext = os.path.splitext(filename)
        file = open(sys.argv[1], "r").read()
        g = GeomLang(file, base, debug=debug)
        print "Wrote to %s.svg" % base
                
                
                               
        
        
        
        
   
 
            
                   
        
    