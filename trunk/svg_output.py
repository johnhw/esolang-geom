from xml.etree import ElementTree as et 


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
        for line in self.inf_lines:
            pts = get_bounded_inf_lines(bbox, line[0], line[1])
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
       