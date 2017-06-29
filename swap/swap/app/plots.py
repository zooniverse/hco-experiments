
from flask import Flask, render_template, jsonify, request
import math

import swaptools.experiments.db.plots as plotsdb


app = Flask(__name__)


@app.route('/data')
def get_data():

    type_ = request.args.get('type', None)
    experiment = request.args.get('experiment', None)

    points = plotsdb.get_plot(experiment)

    max_width, data = choose_plot(points, type_)

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
        'points': data,
        'left': {
            'name': 'purity',
            'stats': get_stats('purity'),
        },
        'right': {
            'name': 'completeness',
            'stats': get_stats('completeness')
        },
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
    elif type_ == 'square':
        return plot_points_square(data)


def plot(func):

    def wrapper(data):

        def normalize(key):
            max_ = max(data, key=lambda item: item[key])[key]
            min_ = min(data, key=lambda item: item[key])[key]

            new_key = '%s_n' % key
            for item in data:
                value = item[key]
                if max_ != min_:
                    item[new_key] = (value - min_) / (max_ - min_)
                else:
                    item[new_key] = 0

        normalize('purity')
        normalize('completeness')

        width, data = func(data)
        output = []
        for item in data:
            new_item = {
                'id': {'golds': item['golds'], 'n': item['n']},
                'values': {
                    'purity': [item['purity'], item['purity_n']],
                    'completeness':
                        [item['completeness'], item['completeness_n']]
                },
                'pos': {
                    'x': item['x'],
                    'y': item['y'],
                    'id': item['id']
                }
            }
            output.append(new_item)

        return width, output

    return wrapper


@plot
def plot_points_square(data):
    x = 0
    y = 0
    width = math.ceil(math.sqrt(len(data)))

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

    return width, data


@plot
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

    return max_width, data


@plot
def plot_points_sorted(data):

    def _sort(item):
        p = 1 - item['purity_n']
        c = item['completeness_n']
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

    return width, data


@app.route("/plots/<experiment>/<type>")
def index(experiment, type):
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
