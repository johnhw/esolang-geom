import Tkinter
        
        
class TkObject:
    oval = 0
    line = 1
    arc = 2
    pt = 3
    
    def __init__(self, t, p1, p2=None, p3=None, start=None, extent=None, transform=[0,0,1,1]):
        self.t = t
        self.bbox = bbox
        self.transform = transform
        self.screen_transform()        
        self.start = start
        self.extent = extent
        
    def extents(self):
        xmin = min(bbox[0], bbox[1])
        xmax = max(bbox[0], bbox[1])
        ymin = min(bbox[2], bbox[3])
        ymax = max(bbox[2], bbox[3])
        return [xmin,xmax,ymin,ymax]        
        
    def screen_transform(self):        
        self.screen_bbox = [self.transform[2] * (self.bbox[0] - self.transform[0]), 
        self.transform[2] * (self.bbox[1] - self.transform[0]), 
        self.transform[3] * (self.bbox[2] - self.transform[1]), 
        self.transform[3] * (self.bbox[3] - self.transform[1])]
        
class TKOutput(object):
    def __init__(self, geom):
        self.geom = geom
        self.root = Tkinter.Tk()
        self.canvas = Tkinter.Canvas(self.root, width=600, height=400, background="White")
        self.permanent = []
        self.transient = []
        self.tk_transient = []
        self.transform = [0,0,0.5,0.5]        
        self.bbox = [-2,2,-2,2]
        self.canvas.pack()
        Tkinter.mainloop()
        
    def point(self, p1):                
        oval = TkObject(TkObject.oval, p1, transform=self.transform)
        self.permanent.append(oval)
        self.canvas.create_oval(oval.screen_bbox, fill="black", outline="")
                                                   
    def circle(self, p1, p2):                   
        oval = TkObject(TkObject.oval, p1, p2, transform=self.transform)
        self.permanent.append(oval)
        self.canvas.create_oval(oval.screen_bbox, fill="")
        
                
    def line(self, p1, p2):           
        oval = TkObject(TkObject.line, p1, p2, transform=self.transform)
        self.permanent.append(oval)
        self.canvas.create_oval(oval.screen_bbox, fill="")
                
    def arc(self, p1, p2, p3):
        l = length(p1, p2)
        v1 = sub(p1, p2)
        v2 = sub(p1, p3)        
        a1 = atan2(v1[1], v1[0])
        a2 = atan2(v2[1], v2[0])
        oval = TkObject(TkObject.arc, p1, p2, p3, transform=self.transform)
        self.permanent.append(oval)
        arc = self.canvas.create_arc(oval.screen_bbox, start=start, extent=extent, fill="")
            
    def update_transients(self):
        if len(self.transient)>2:
            self.transient = self.transient[1:]
            self.canvas.delete(self.tk_transient[0])
            self.tk_transient = self.tk_transient[2:]
        
    def transient_circle(self, p1, p2):
        self.oval = TkObject(TkObject.oval, p1, p2, transform=self.transform)
        self.transient.append(oval)
        circle = self.canvas.create_oval(oval.screen_bbox, fill="", outline="grey")
        self.tk_transient.append(circle)
        self.update_transients()
                
        
    def transient_inf_line(self, p1, p2):
        line = TkObject(TkObject.line, p1, p2, transform=self.transform)
        self.transient.append(line)
        tk_line = self.canvas.create_line(line.screen_bbox, fill="", outline="grey")
        self.update(transients)
                        
        
    def rescale(self):
        # rescale all all the objects
        objects = self.permanent + self.transient
        xs = []
        ys = []
        for object in objects:
            xmin,xmax,ymin,ymax = object.extents
            xs.append(xmin)
            xs.append(xmax)
            ys.append(ymin)
            ys.append(ymax)
        minx = min(xs)
        maxx = max(xs)
        miny = min(ys)
        maxy = max(ys)
        
        bbox = [minx,maxx,miny,maxy]
        transform = [-minx, -maxx, (maxx-minx), (maxy-miny)]
        eps = 1e-1
        
        if abs(self.bbox[0]-bbox[0])>eps or abs(self.bbox[1]-bbox[1])>eps or abs(self.bbox[2]-bbox[2])>eps or abs(self.bbox[3]-bbox[3])>eps:
            self.bbox = bbox
            self.transform = transform
            self.redraw()
            
    
    def redraw(self):
        
        all = self.canvas.find_all()
        self.canvas.delete(all)
        for object in self.permanent:
            if object.t==oval:
                self.canvas.create
    
    def update(self):
        self.geom.step()
        self.root.after(100, self.update())
