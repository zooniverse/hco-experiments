
from flask import Flask, render_template, jsonify, request
import math

import swaptools.experiments.db.plots as plotsdb


app = Flask(__name__)


@app.route('/data')
def get_data():
    points = plotsdb.get_plot('random-500')

    type_ = request.args.get('type', None)
    max_width = choose_plot(points, type_)

    def get_stats(key):
        max_ = max(points, key=lambda item: item[key])[key]
        min_ = min(points, key=lambda item: item[key])[key]
        middle = (min_ + max_) / 2
        return {
            'min': min_,
            'max': max_,
            'middle': middle
        }

    data = {
        'points': points,
        'purity': get_stats('purity'),
        'completeness': get_stats('completeness'),
        'width': max_width,
        'height': math.ceil(len(points) / max_width)
    }

    return jsonify(data)


def choose_plot(data, type_):
    if type_ == 'regular' or type_ is None:
        return plot_points_reg(data)
    elif type_ == 'sorted':
        return plot_points_sorted(data)


def plot_points_reg(data):
    x = 0
    y = 0
    count = 0
    max_width = 0

    last = data[0]['golds']
    for item in data:
        golds = item['golds']
        if last // 1000 != golds // 1000:
            last = golds
            if y > max_width:
                max_width = y
            y = 0
            x += 1
        item['x'] = x
        item['y'] = y
        item['id'] = count

        y += 1
        count += 1

    return max_width


def plot_points_sorted(data):
    def count(data, key):
        n = 0
        for item in data:
            n += item[key]

        return n

    p_count = count(data, 'purity')
    c_count = count(data, 'completeness')

    def _sort(item):
        p = item['purity'] / p_count
        c = item['completeness'] / c_count
        return p ** 2 + c ** 2

    data = sorted(data, key=_sort)
    width = math.ceil(math.sqrt(len(data)))

    x = 0
    y = 0
    for i, item in enumerate(data):
        if x > width:
            x = 0
            y += 1
        item.update({
            'x': x,
            'y': y,
            'id': i
        })
        x += 1

    return width


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
