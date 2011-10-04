try:
    # use symbolic solver if it's available
    from sympy import Rational, sqrt, atan2, pi        
except ImportError:    
    # use float solver if no sympy
    from math import sqrt, atan2, pi
    
    
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

def get_bounded_inf_lines(bbox, p1, p2, border=0.1):
    bboxscale = border
    
    y1 = bbox[2]-(bbox[3]-bbox[2])*bboxscale
    y2 =bbox[3]+(bbox[3]-bbox[2])*bboxscale
    x1= bbox[0]-(bbox[1]-bbox[0])*bboxscale
    x2 = bbox[1]+(bbox[1]-bbox[0])*bboxscale
    
    # get bounding box lines
    topline = ((x1,y1), (x2,y1))
    bottomline = ((x1,y2), (x2,y2))
    leftline = ((x1,y1), (x1,y2))
    rightline = ((x2,y1), (x2,y2))
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
     
        
    return pts

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
    