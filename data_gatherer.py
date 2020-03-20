import json
import os.path

import gmplot
import numpy as np
import requests
from matplotlib import pyplot


class configuration:
    start_str = ""
    end_str = ""

    start_point = ""
    end_point = ""

    accuracy = 0.0
    alpha = 0.0

    def __init__(self, cls_start_str="", cls_end_str=""):
        self.start_str = cls_start_str
        self.end_str = cls_end_str

    def __str__(self):
        out_str = "From " + string_dict.get(self.start_str) + " to " + string_dict.get(self.end_str)
        out_str += " | accuracy = " + str(self.accuracy) + " alpha " + str(self.alpha)
        return out_str


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
        return "point(" + str(self.id[0]) + "," + str(self.id[1]) + "," + str(int(self.height*100)) + ")."


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
            point_d = vec_se_extend.to_point(start, (int(d), r))
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


def filename_to_config(name):
    args = name.split("_")
    start_str = args[0]
    end_str = args[1]
    acc = args[2]
    alph = args[3].split(".")[0]
    con = configuration(start_str, end_str)
    con.accuracy = float(acc)
    con.alpha = float(alph)
    return con


coordinates_dict = {
    "golm": point(52.408492, 12.976237),
    "gns": point(52.393363, 13.130655),
    "ehst": point(52.147293, 14.658077),
    "fstw": point(52.366553, 14.060773),
    "stAnton": point(47.125953, 10.262627),
    "malgolo": point(46.377417, 11.095031)
}

string_dict = {
    "golm": "Golm",
    "gns": "Griebnitzsee",
    "ehst": "Eisenhüttenstadt",
    "fstw": "Fürstenwalde",
    "stAnton": "St. Anton",
    "malgolo": "Malgolo"
}

int_dict = {
    1: "golm",
    2: "gns",
    3: "ehst",
    4: "fstw",
    6: "stAnton",
    7: "malgolo"
}

configurations = []

for filename in os.listdir("./responses"):
    configurations.append(filename_to_config(filename))

print("")
i = 1
for conf in configurations:
    print(str(i) + ". " + str(conf))
    i += 1
print(str(i) + ". Create a new Configuration")

while True:
    conf_select = int(input("Choose a previous configuration or create a new one(" + str(1) + "-" + str(i) + "):"))
    if conf_select >= 1 or conf_select < i:
        break
    else:
        print("[ERROR] Selected Number is out of range")
if i == conf_select:
    config = configuration()
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

    config.start_str = int_dict.get(starting_input)
    print("You selected " + string_dict.get(config.start_str) + " as a starting position\n")
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
    config.end_str = int_dict.get(end_input)
    print("You selected " + string_dict.get(config.end_str) + " as a end position\n")

    while True:
        alpha = int(input("Choose an angle between 1° and 89°:"))
        if alpha >= 1 and alpha <= 89:
            break
        else:
            print("[ERROR] Selected Number is out of range\n")
    config.alpha = alpha

    while True:
        accuracy = int(input("Choose an accuracy (the higher the number, the more accurate the result):"))
        if accuracy >= 1:
            break
        else:
            print("[ERROR] Selected Number must be greater than 0\n")

    config.accuracy = accuracy
else:
    config = configurations[conf_select - 1]

print("___")
print("Finding path from " + string_dict.get(config.start_str) + " to " + string_dict.get(config.end_str) + "...")

start = coordinates_dict.get(config.start_str).extend(config.accuracy)
end = coordinates_dict.get(config.end_str).extend(config.accuracy)

points = []

print("Creating a regular grid with the accuracy " + str(config.accuracy) + " and an inclination of " + str(
    config.alpha) + "°...")
latitude_list, longitude_list, points_res = regGrid(config.alpha, start, end, config.accuracy)

end.id = (int(vector(start, end).len()), 0)
plot_relative_grid = True

start_and_end_lat = [start.x / config.accuracy, end.x / config.accuracy]
start_and_end_lon = [start.y / config.accuracy, end.y / config.accuracy]

file = open("apiKey", "r")
apiKey = file.read()
file.close()

gmap = gmplot.GoogleMapPlotter(min(start_and_end_lat), max(start_and_end_lon), 0)
gmap.zoom = vector(start, end).len() / 2.25

gmap.apikey = apiKey

gmap.scatter(start_and_end_lat, start_and_end_lon, '#00FF00', size=100, marker=True)
gmap.scatter(latitude_list, longitude_list, '#FF0000', size=100, marker=False)

print("Drawing initial Map...")

gmap.draw("./output/map.htm")

points_res.append(start.extend(1 / config.accuracy))
points_res.append(end.extend(1 / config.accuracy))

url_request = point_list_to_request(points_res) + "&key=" + apiKey

file.close()
# --------------------
# File Check / query
path = "responses/" + config.start_str + "_" + config.end_str + "_" + str(int(config.accuracy)) + "_" + str(int(config.alpha)) + ".json"

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
# ------------------
# Plotting
X = []
Y = []
c = []

for fact in facts[:-2]:
    file.write(fact.to_fact_str() + "\n")
    if plot_relative_grid:
        X.append(fact.id[0])
        Y.append(fact.id[1])
        c.append(fact.height)

file.write("start(" + str(int(facts[-2].id[0])) + "," + str(facts[-2].id[1]) + "," + str(int(facts[-2].height*100)) + ")." + "\n")
file.write("start(" + str(int(facts[-1].id[0])) + "," + str(facts[-1].id[1]) + "," + str(int(facts[-1].height*100)) + ")." + "\n")

if plot_relative_grid:
    fig, ax = pyplot.subplots()
    res = ax.scatter(X, Y, c=c, cmap="terrain", vmin=-1000, vmax=4000)
    cbar = pyplot.colorbar(res)
    pyplot.clabel = "Grid from " + config.start_str
    pyplot.show()
file.close()
