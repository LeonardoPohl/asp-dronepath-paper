import sys

import numpy as np
import gmplot
import requests
from progress.bar import IncrementalBar
from matplotlib import pyplot


class point:
    x = 0.0
    y = 0.0

    id = (0.0, 0.0)
    height = 0.0

    def __init__(self, x, y, x_rel=0, y_rel=0):
        self.x = x
        self.y = y
        self.id = (x_rel, y_rel)

    def to_vec(self, end_point):
        return vector(end_point.x - self.x, end_point.y - self.y)

    def str(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def extend(self, factor):
        return point((self.x * factor), (self.y * factor), self.id[0], self.id[1])

    def to_fact_str(self):
        return "point(" + str(self.id[0]) + "," + str(self.id[1]) + "," + str(self.height) + ")."

class vector:
    x = 0.0
    y = 0.0

    def __init__(self, point_A, point_B):
        self.x = point_B.x - point_A.x
        self.y = point_B.y - point_A.y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def len(self):
        return np.sqrt(self.x ** 2 + self.y ** 2)

    def to_point(self, start_point, id):
        return point(start_point.x + self.x, start_point.y + self.y, id[0], id[1])

    def extend(self, v):
        return vector(point(0, 0), point(self.x * v, self.y * v, 0, 0))

    def rotate(self, alpha):
        x_2 = self.x * np.cos(alpha) - self.y * np.sin(alpha)
        y_2 = self.x * np.sin(alpha) + self.y * np.cos(alpha)
        return vector(point(0, 0), point(x_2, y_2))


def regGrid(alpha, start, end, accuracy):
    vec_se = vector(start, end)  # SE
    X = []
    Y = []
    points = []
    bar = IncrementalBar('Processing', max=vec_se.len())
    fac = 0
    for d in np.arange(vec_se.len()):
        bar.next()
        fac_old = fac
        fac = int(10000 * d / vec_se.len()) / 100
        if (fac - fac_old <= 0.1):
            print(str(fac) + " \t100.00\r")
        vec_se_for_d = vec_se.extend(d / vec_se.len())  # SE'
        k = d if d < vec_se.len() / 2 else vec_se.len() - d
        r_max_d = np.ceil(get_r(alpha, k))
        r_min_d = r_max_d * - 1
        for r in range(int(r_min_d), int(r_max_d)):
            beta = np.arctan(r / d)
            vec_se_rot = vec_se_for_d.rotate(beta)
            vec_se_extend = vec_se_rot.extend(np.sqrt(d ** 2 + r ** 2) / d)
            point_d = vec_se_extend.to_point(start, (d, r))
            X.append(point_d.x / accuracy)
            Y.append(point_d.y / accuracy)
            points.append(point_d.extend(1/accuracy))
    bar.finish()
    return X, Y, points


def point_list_to_request(points):
    url_request = 'https://maps.googleapis.com/maps/api/elevation/json?locations='
    for point in points:
        url_request += str(point.x) + "," + str(point.y) + "|"

    return url_request[:-1]


def get_r(alpha, d):
    return np.tan(np.deg2rad(alpha)) * d


coordinates_dict = {
    "golm": point(52.408492, 12.976237),
    "gns": point(52.393363, 13.130655),
    "ehst": point(52.147293, 14.658077),
    "fstw": point(52.366553, 14.060773),
    "wlgt": point(-41.326396, 174.836648),
    "stAnton": point(47.125953, 10.262627),
    "malgolo": point(46.377417, 11.095031)
}

accuracy = 2 * 10 ** 1
alpha = 30

start_str = "stAnton"
end_str = "malgolo"

start = coordinates_dict.get(start_str).extend(accuracy)
end = coordinates_dict.get(end_str).extend(accuracy)

points = []

latitude_list, longitude_list, points_res = regGrid(alpha, start, end, accuracy)
X, Y = [], []

end.id = (vector(start, end).len(), 0)

X.append(start.id[0])
X.append(end.id[0])
Y.append(start.id[1])
Y.append((end.id[1]))

for point_tmp in points_res:
    X.append(point_tmp.id[0])
    Y.append(point_tmp.id[1])

fig, ax = pyplot.subplots()
ax.scatter(X, Y)
pyplot.show()

start_and_end_lat = [start.x / accuracy, end.x / accuracy]
start_and_end_lon = [start.y / accuracy, end.y / accuracy]

gmap = gmplot.GoogleMapPlotter(min(start_and_end_lat), max(start_and_end_lon), 0)
gmap.zoom = vector(start, end).len() / 2.25

gmap.scatter(start_and_end_lat, start_and_end_lon, '#00FF00', size=500, marker=True)
gmap.scatter(latitude_list, longitude_list, '#FF0000', size=500, marker=False)

gmap.draw("./map.htm")

points_res.append(start.extend(1/accuracy))
points_res.append(end.extend(1/accuracy))

url_request = point_list_to_request(points_res) + "&key="

response = requests.get(url_request)
print(url_request)

print(response.json())
