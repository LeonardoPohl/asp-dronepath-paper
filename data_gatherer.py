import numpy as np
import gmplot

class point:
    latitude_list = 0.0
    longitude_list = 0.0
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_vec(self,end_point):
        return vector(end_point.x - self.x, end_point.y - self.y)

    def str(self):
        return "("+str(self.x)+", "+str(self.y)+")"

class vector:
    latitude_list = 0.0
    longitude_list = 0.0
    def __init__(self, point_A, point_B):
        self.x = point_B.x - point_A.x
        self.y = point_B.y - point_A.y

    def str(self):
        return "("+str(self.x)+", "+str(self.y)+")"

    def len(self):
        return np.sqrt(self.x**2 + self.y**2)

    def to_point(self, start_point):
        return point((start_point.x + self.x), (start_point.y + self.y))

    def extend(self,v):
        return vector(point(0,0), point(self.x*v,(self.y*v)))

    def rotate(self, alpha):
        x_2 = self.x * np.cos(alpha) - self.y * np.sin(alpha)
        y_2 = self.x * np.sin(alpha) + self.y * np.cos(alpha)
        return vector(point(0,0),point(x_2,y_2))


def regGrid(alpha, start, end,accuracy):
    vec_se = vector(start,end) # SE
    X = []
    Y = []
    coordinates = [] #2-tuple with id (mapping to ) ((x,y,z),id)
    asp_facts = []
    for d in np.arange(vec_se.len()):
        vec_se_for_d = vec_se.extend(d/vec_se.len()) # SE'
        k = d if d < vec_se.len()/2 else vec_se.len()-d
        r_max_d = np.ceil(get_r(alpha,k))
        r_min_d = r_max_d * - 1
        for r in range(int(r_min_d),int(r_max_d)):
            beta = np.arctan(r/d)
            vec_se_rot = vec_se_for_d.rotate(beta)
            vec_se_extend = vec_se_rot.extend(np.sqrt(d**2+r**2)/d)
            point_d = vec_se_extend.to_point(start)
            X.append(point_d.x/accuracy)
            Y.append(point_d.y/accuracy)
            asp_facts.append
    return X, Y

def get_r(alpha, d):
    return np.tan(np.deg2rad(alpha)) * d

accuracy = 2*10**2
start = point(52.408492*accuracy, 12.976237*accuracy) # 52.408492, 12.976237 = golm
end = point(52.393363*accuracy, 13.130655*accuracy) # 52.393363, 13.130655 griebnitzsee
alpha = 40
latitude_list, longitude_list = regGrid(alpha, start, end, accuracy)
start_and_end_lat = []
start_and_end_lon = []
start_and_end_lon.append(start.y / accuracy)
start_and_end_lon.append(end.y / accuracy)
start_and_end_lat.append(start.x / accuracy)
start_and_end_lat.append(end.x / accuracy)

gmap = gmplot.GoogleMapPlotter(min(start_and_end_lat),max(start_and_end_lon), 13)

gmap.scatter(start_and_end_lat, start_and_end_lon, '# 00FF00', size=40, marker=False)
gmap.scatter(latitude_list, longitude_list, '# FF0000', size=40, marker=False)

gmap.apikey = "AIzaSyC-DqNJRWb-abhFcr-rsQmQ00O2sZaL45c"

gmap.draw("./map.htm")
