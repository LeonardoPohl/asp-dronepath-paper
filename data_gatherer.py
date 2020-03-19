import json
import os.path

import gmplot
import numpy as np
import requests
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
    fac, fac_old = 0, 0
    for d in np.arange(vec_se.len()):
        fac = int(10000 * d / vec_se.len()) / 100
        if (fac - fac_old > 1):
            fac_old = fac
            print(str(fac) + " \t100.00", end="%s\r")
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
            points.append(point_d.extend(1 / accuracy))
    return X, Y, points


def point_list_to_request(points):
    url_request = 'https://maps.googleapis.com/maps/api/elevation/json?locations='
    for point in points:
        url_request += str(point.x) + "," + str(point.y) + "|"

    return url_request[:-1]


def get_r(alpha_tmp, d):
    return np.tan(np.deg2rad(alpha_tmp)) * d


def find_point(point_list, lat, lng, digit=4):
    global found_point
    count = 0

    for itr_point in point_list:
        if round(itr_point.x, digit) == round(lat, digit) and round(itr_point.y, digit) == round(lng, digit):
            found_point = itr_point
            count += 1

    if (count == 1):
        return found_point
    elif (count == 0):
        return find_point(point_list, lat, lng, digit - 1)
    else:
        return find_point(point_list, lat, lng, digit + 1)


coordinates_dict = {
    "golm": point(52.408492, 12.976237),
    "gns": point(52.393363, 13.130655),
    "ehst": point(52.147293, 14.658077),
    "fstw": point(52.366553, 14.060773),
    "wlgt": point(-41.326396, 174.836648),
    "stAnton": point(47.125953, 10.262627),
    "malgolo": point(46.377417, 11.095031)
}

string_dict = {
    "golm": "Golm",
    "gns": "Griebnitzsee",
    "ehst": "Eisenhüttenstadt",
    "fstw": "Fürstenwalde",
    "wlgt": "Wellington",
    "stAnton": "St. Anton",
    "malgolo": "Malgolo"
}

int_dict = {
    1: "golm",
    2: "gns",
    3: "ehst",
    4: "fstw",
    5: "wlgt",
    6: "stAnton",
    7: "malgolo"
}

accuracy = 2 * 10 ** 2
alpha = 30
i = 1
print("Saved locations:")
for loc in string_dict:
    print(str(i) + ". " + string_dict.get(loc))
    i += 1

while True:
    starting_input = int(input("Choose starting point (" + str(1) + "-" + str(i) + "):"))
    if starting_input >= 1 or starting_input <= i:
        break
    else:
        print("[ERROR] Selected Number is out of range")

start_str = int_dict.get(starting_input)
print("You selected " + string_dict.get(start_str) + " as a starting position\n")
print("Select one of the following Locations")

i = 1
for loc in string_dict:
    prt_str = str(i) + ". " + string_dict.get(loc)
    if i == starting_input:
        prt_str = "-------------"
    print(prt_str)
    i += 1

while True:
    end_input = int(input("Choose an end point (" + str(1) + "-" + str(i) + "):"))
    if (end_input >= 1 or end_input <= i) and end_input != starting_input:
        break
    else:
        print("[ERROR] Selected Number is out of range or equal to the starting position")

end_str = int_dict.get(end_input)
print("You selected " + string_dict.get(end_str) + " as a end position\n")

while True:
    alpha = int(input("Choose an angle between 1° and 89°:"))
    if alpha >= 1 and alpha <= 89:
        break
    else:
        print("[ERROR] Selected Number is out of range\n")

while True:
    accuracy = int(input("Choose an accuracy (the higher the number, the more accurate the result):"))
    if accuracy >= 1:
        break
    else:
        print("[ERROR] Selected Number must be greater than 0\n")

print("___")
print("Finding path from " + string_dict.get(start_str) + " to " + string_dict.get(end_str) + "...")

start = coordinates_dict.get(start_str).extend(accuracy)
end = coordinates_dict.get(end_str).extend(accuracy)

points = []

print("Creating a regular grid with the accuracy " + str(accuracy) + " and an inclination of " + str(alpha) + "°...")
latitude_list, longitude_list, points_res = regGrid(alpha, start, end, accuracy)
X, Y = [], []

end.id = (int(vector(start, end).len()), 0)
plot_relative_grid = True

if plot_relative_grid:
    print("Plotting regular grid...")
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

file = open("apiKey", "r")
apiKey = file.read()
file.close()

gmap = gmplot.GoogleMapPlotter(min(start_and_end_lat), max(start_and_end_lon), 0)
gmap.zoom = vector(start, end).len() / 2.25

gmap.apikey = apiKey

gmap.scatter(start_and_end_lat, start_and_end_lon, '#00FF00', size=100, marker=True)
gmap.scatter(latitude_list, longitude_list, '#FF0000', size=100, marker=False)

print("Drawing initial Map...")

gmap.draw("./map.htm")

points_res.append(start.extend(1 / accuracy))
points_res.append(end.extend(1 / accuracy))

url_request = point_list_to_request(points_res) + "&key=" + apiKey

file.close()

path = "responses/" + start_str + "_to_" + end_str + "_grid_acc:" + str(accuracy) + "_alpha:" + str(alpha) + ".json"

if os.path.exists(path):
    file = open(path, "r")
    print("The grid was already requested, file will be used...")
    response = []
    for line in file:
        response.append(json.loads(line.strip()))
else:
    print("No File found starting request with the following URL:")
    print(url_request)
    response = requests.get(url_request).json().get("results")
    file = open(path, "w+")
    for s in response:
        file.write(str(s).replace("'", "\"") + "\n")
    file.close()

facts = []
print("Creating ASP facts...")
for i in response:
    location = i.get("location")
    tmp_point = find_point(points_res, location.get("lat"), location.get("lng"))
    tmp_point.height = i.get("elevation")
    facts.append(tmp_point)
file = open("asp/input.lp", "w+")
for fact in facts:
    file.write(fact.to_fact_str() + "\n")
file.close()
