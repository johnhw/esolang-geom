import sys, os, random
from geomplusplus import Nil
from Tkinter import *
from geo import *

def to_degrees(x):
        return (x/pi) * 180.0
        
class TkObject:
    # represent one object to be drawn on a canvas
    oval = 0
    line = 1
    inf_line = 4
    arc = 2
    point = 3
    
    def __init__(self, t, p1, p2=None, p3=None, start=None, extent=None, fill="", outline="black", r=0.02):
        self.t = t
        
        # create the bounding box
        if t==TkObject.oval:            
            r = length(p1,p2)            
            self.bbox = [p1[0]-r, p1[0]+r, p1[1]-r, p1[1]+r]
        if t==TkObject.point:            
            self.bbox = [p1[0]-r, p1[0]+r, p1[1]-r, p1[1]+r]
        if t==TkObject.line or t==TkObject.inf_line:
            self.bbox = [p1[0], p2[0], p1[1], p2[1]]
        if t==TkObject.arc:
            r = length(p1,p2)
            self.bbox = [p1[0]-r, p1[0]+r, p1[1]-r, p1[1]+r]                                
            
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        
        self.fill = fill
        self.outline = outline       
        self.start = start
        self.extent = extent
        self.uid = random.getrandbits(64)
        
    def set_transform(self, transform, bbox):
        self.transform = transform
        if self.t==TkObject.inf_line:
            pts = get_bounded_inf_lines(bbox, self.p1, self.p2)        
            if pts and len(pts)==2:                
                self.bbox = [pts[0][0], pts[1][0], pts[0][1], pts[1][1]]
        self.screen_transform()        
                
    def extents(self):
        bbox = self.bbox
        xmin = min(bbox[0], bbox[1])
        xmax = max(bbox[0], bbox[1])
        ymin = min(bbox[2], bbox[3])
        ymax = max(bbox[2], bbox[3])
        return [xmin,xmax,ymin,ymax]        
        
    def screen_transform(self):        
        w = 600
        h = 400        
        self.screen_bbox = [float(f) for f in [self.transform[2] * (self.bbox[0] - self.transform[0]) * (w/2)+w/2, 
        self.transform[3] * (self.bbox[2] - self.transform[1])* (h/2)+h/2, 
        self.transform[2] * (self.bbox[1] - self.transform[0])* (w/2)+w/2, 
        self.transform[3] * (self.bbox[3] - self.transform[1])* (h/2)+h/2]]
        
        
    def __hash__(self):
        return self.uid
        
    def __eq__(self, object):
        return isinstance(object, TkObject) and self.uid == object.uid
    
    def __ne__(self, object):    
        return not isinstance(object, TkObject) or self.uid != object.uid
        
        
class TKOutput(object):
    def __init__(self, geom):
        
        self.geom = geom
        self.root = Tk()
        self.canvas = Canvas(self.root, width=600, height=400, background="White")
        
        self.object_tk_binding = {}        
        self.canvas.focus_set()
        self.canvas.bind("<Key>", self.key)
        self.canvas.bind("<Button-1>", self.callback)
        self.canvas.bind("<Button-2>", self.callback)        
        self.permanent = []
        self.transient = []
        self.transient_points = []
        self.transform = [0,0,0.5,0.5*(6/4.0)]        
        self.bbox = [-2,2,-2,2]
        self.canvas.pack()        
        self.stack = Text(self.root, height=1)
        self.stack.pack(fill=X)
        
        text_frame = Frame(self.root)
        
        self.code_text = Text(text_frame)
        
        self.scrollbar = Scrollbar(self.root)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.code_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.code_text.yview)
        self.code_text.pack(fill=BOTH)
        text_frame.pack(fill=X)        
        self.paused = True
        self.tag_circle = None
        self.tag_point = None
        self.step = False
        self.set_highlight(self.geom.code, [0,0], "")
    
    def start(self):
        self.update()
        mainloop()
        
    def set_highlight(self, text, highlight, stack):                
        
        self.stack.config(state=NORMAL)
        self.stack.delete(1.0, END)
        self.stack.insert(END, stack)
        self.stack.config(state=DISABLED)
        
        self.code_text.tag_config("h", foreground="red")        
        self.code_text.config(state=NORMAL)
        self.code_text.delete(1.0, END)
        self.code_text.insert(END, text[0:highlight[0]])
        self.code_text.insert(END, text[highlight[0]:highlight[1]], 'h')
        self.code_text.insert(END, text[highlight[1]:])        
        self.code_text.config(state=DISABLED)
        
    def key(self, event):        
        # pause / go
        if event.char=='p':
            self.paused = not self.paused            
        # one step 
        if event.char=='s':
            self.step = True
                    
    def callback(self, event):
        pass
        
    def point(self, p1):                
        # draw a point        
        oval = TkObject(TkObject.point, p1, fill="black", outline="")                
        self.permanent.append(oval)                
        self.rescale()
                                                   
    def circle(self, p1, p2):                   
        # draw a circle
        oval = TkObject(TkObject.oval, p1, p2, fill="", outline="black")
        self.permanent.append(oval)        
        self.rescale()
                
    def line(self, p1, p2):           
        # draw  a line
        line = TkObject(TkObject.line, p1, p2, fill="black", outline="")
        self.permanent.append(line)        
        self.rescale()
                
    def arc(self, p1, p2, p3):
        # draw an arc
        l = length(p1, p2)
        v1 = sub(p1, p2)
        v2 = sub(p1, p3)        
        a1 = atan2(v1[1], v1[0])
        a2 = atan2(v2[1], v2[0])
        oval = TkObject(TkObject.arc, p2, p3, p3, fill="", outline="black", start=to_degrees(a2), extent=to_degrees(a2-a1))
        self.permanent.append(oval)        
        self.rescale()
            
    def update_transients(self):
        # delete old transients
        if len(self.transient)>2:
            if self.object_tk_binding.has_key(self.transient[0]):
                del self.object_tk_binding[self.transient[0]]
            self.transient = self.transient[1:]                                    
            self.rescale()
            
        if len(self.transient_points)>2:
            del self.object_tk_binding[self.transient_points[0]]
            self.transient_points = self.transient_points[1:]                                    
            self.rescale()
                    
    def transient_circle(self, p1, p2):
        # draw a temporary circle        
        oval = TkObject(TkObject.oval, p1, p2, fill="", outline="lightblue")
        self.transient.append(oval)
        self.update_transients()                        
        
    def transient_inf_line(self, p1, p2):
        # draw an "infinite" line
        line = TkObject(TkObject.inf_line, p1, p2, fill="lightblue")
        self.transient.append(line)
        self.update_transients()
    
    def transient_point(self, p):
        # draw an "infinite" line
        if p:
            point = TkObject(TkObject.point, p, fill="red", r=0.02, outline="")
            self.point(p)
            self.transient_points.append(point)
            self.update_transients()    
        
    def rescale(self):
        
        
        # rescale all all the objects
        objects = self.permanent
        xs = []
        ys = []
        # find the bounds of all objects
        for object in objects:
            xmin,xmax,ymin,ymax = object.extents()
            xs.append(xmin)
            xs.append(xmax)
            ys.append(ymin)
            ys.append(ymax)
        minx = min(xs+[-2])
        maxx = max(xs+[2])
        miny = min(ys+[-2])
        maxy = max(ys+[2])
        
        bbox = [minx,maxx,miny,maxy]
        transform = [-minx, -maxx, (maxx-minx), (maxy-miny)]
        eps = 1e-1
        
        
        
        # if bounding has changed significantly, redraw all objects
        if abs(self.bbox[0]-bbox[0])>eps or abs(self.bbox[1]-bbox[1])>eps or abs(self.bbox[2]-bbox[2])>eps or abs(self.bbox[3]-bbox[3])>eps:
            self.bbox = bbox
            self.transform = transform
            self.object_tk_binding = {}
            
        self.redraw()
            
    
    def redraw(self):
        # redraw all objects        
        if self.tag_point!=self.geom.current_tag_point:
            self.tag_point = self.geom.current_tag_point           
            # draw circle around currently executing point
            if self.tag_circle:
                self.canvas.delete(self.tag_circle)
            if self.geom.current_tag_point:                
                pt = TkObject(TkObject.point, self.geom.current_tag_point, r=0.2, fill="", outline="red")
                pt.transform(self.transform, self.bbox)
                self.tag_circle = self.canvas.create_oval(object.screen_bbox, fill=object.fill, outline=object.outline)
                            
        # first of all generate all objects that aren't drawn already
        objects = self.permanent + self.transient + self.transient_points
        for object in objects:            
            object.set_transform(self.transform, self.bbox)
            
            if not self.object_tk_binding.has_key(object):
                # draw the new objects
                if object.t == TkObject.line:
                    tk_object = self.canvas.create_line(object.screen_bbox, fill=object.fill)
                if object.t == TkObject.inf_line:
                    tk_object = self.canvas.create_line(object.screen_bbox, fill=object.fill)                   
                if object.t == TkObject.oval:
                    tk_object = self.canvas.create_oval(object.screen_bbox, fill=object.fill, outline=object.outline)                    
                if object.t == TkObject.point:
                    tk_object = self.canvas.create_oval(object.screen_bbox, fill=object.fill, outline=object.outline)
                if object.t == TkObject.arc:
                    tk_object = self.canvas.create_arc(object.screen_bbox, start=object.start, extent=object.extent,fill=object.fill, outline=object.outline, style="arc")                                                                    
                self.object_tk_binding[object] = tk_object
        
        # remove all objects that aren't on the lists
        all_tk_objects = list(self.canvas.find_all())        
        for object in self.object_tk_binding.keys():
            tk_object = self.object_tk_binding[object]            
            if tk_object in all_tk_objects:
                all_tk_objects.remove(tk_object)                
        
        for object in all_tk_objects:
            self.canvas.delete(object)
            
        
    # keep updating the screen / executing code
    def update(self):
        #self.redraw()
        self.canvas.update_idletasks()
        if not self.paused or self.step:            
            self.geom.step()
            self.step = False            
        self.root.after(100, self.update)
