
var message_box = function(node) {
    var self = this;

    var init = function(node) {
        var element = $(document.createElement('div'))
            .addClass('message-box')
            .append($(document.createElement('h3')).text('CONSOLE'));
        node.append(element);

        self.node = element;
    }

    self.message = function(msg) {
        var element = $(document.createElement('div'));

        element.addClass('message').text(msg);
        self.node.append(element);
    };

    init(node);
}


var aligned_plot_4d = function(node) {
    var self = this;
    self.container = node;

    (function() {
        var element = $(document.createElement('div'))
            .attr('id', 'console')
            .addClass('graph-item');
        node.append(element);

        console.log(element)
        self.messages = new message_box(element);
    })();

    console.log(44, self.messages);


    var margin = {
        'left': 20,
        'right': 20,
        'top': 20,
        'bottom': 20
    };
    var radius = 20;
    var legend_dimens = {
        'width': 20,
        'tick_margin': 40,
        'offset': 10
    }

    var legend_count = 0;
    var colormaps = {
        'purity': 'viridis_r',
        'p': 'viridis',
        'completeness': 'viridis'
    }

    var dimens = {
        'height': null,
        'width': null
    }

    self.plot = function(data) {
        var chart = d3.select(self.container.get(0));
        var svg = init_svg(chart, data);
        add_gradients(svg, data);
        add_points(svg, data);

        add_legend(svg, data, data.left);
        add_legend(svg, data, data.right);
    };

    var tip_text = function(d) {

        var html = function(element) {
            return $('<div/>').append(element).html();
        }

        var value_span = function(text) {
            return html($('<span/>', {
                class: 'tip-detail',
                text: text
            }));
        };

        var title_block = function(id) {
            var elements = [];

            var text = '';
            for (var key in id) {
                var value = id[key];
                text = text + ' ' + key + ' ' + value_span(value);
            }
            text = $('<div>' + text + '</div>');
            text.attr('id', 'title').addClass('tip-line tip-values');
            // console.log(html(text))

            return html(text);
        }

        var value_line = function(name, values) {
            var values = values.slice();
            for (var n in values)
                values[n] = parseFloat(values[n]).toFixed(3);

            var text = [
                $('<span/>', {id: 'name', text: name}),
                $('<span/>', {id: 'value', class: 'tip-value tip-detail', text: values[0]}),
                $('<span/>', {id: 'norm', class: 'tip-value tip-detail', text: values[1]})
            ];

            text = $('<div/>', {class: 'tip-line '}).append(text);

            return html(text);
        }

        var text = '';
        text += title_block(d.id);
        text += value_line('Purity', d.values.purity);
        text += value_line('Completeness', d.values.completeness);

        out = $('<div/>').append($(text))
        return out.html()
    }

    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function(d) {
            return tip_text(d);
    });

    var legend_width = function() {
        d = legend_dimens;
        return d.width + d.tick_margin + d.offset
    };

    var genColorScale = function(stats, color) {
        var colors = genColorMap(color)

        console.log(stats, color)
        var colorScale = d3.scaleLinear()
            .domain(linspace(stats.min, stats.max, colors.length))
            .range(colors)
        return colorScale;
    }

    var init_svg = function(chart, data) {
        // Compute svg dimensions
        var height = data.height * radius;
        var full_height = height + margin.top + margin.bottom;

        var width = (data.width * 20);
        var full_width = width + (2 * legend_width()) 
            + margin.left + margin.right;

        self.dimens = {
            'width': width,
            'height': height
        }

        // Create svg handle
        var svg = chart.select('svg#graph-svg')
            .attr('width', full_width + 'px')
            .attr('height', full_height + 'px')
            .call(tip);

        return svg;
    };

    var add_gradients = function(svg, data) {
        var scales = {
            'left': genColorScale(data.left.stats, colormaps[data.left.name]),
            'right': genColorScale(data.right.stats, colormaps[data.right.name])
        };

        grads = svg.append('defs').selectAll('linearGradient')
            .data(data.points)
            .enter()
            .append('linearGradient')
            .attr('id', function(d) {return 'grad' + d.pos.id})
            .attr("x1", "100%")
            .attr("x2", "0%")
            .attr("y1", "0%")
            .attr("y2", "0%")
        grads.append('stop')
            .attr('offset', '50%')
            .style('stop-color', function(d) {return scales.right(d.values[data.right.name][0])})
        grads.append('stop')
            .attr('offset', '50%')
            .style('stop-color', function(d) {return scales.left(d.values[data.left.name][0])})

        console.log(scales.left(.45));
    }

    var add_points = function(svg, data) {
        circles = svg.append('g')
            .attr('transform', 'translate('
                  + margin.left + ', '
                  + margin.top + ')');

        circles.selectAll('circle')
            .data(data.points)
            .enter()
            .append('circle')
            .attr('r', '10' + 'px')
            .attr('cx', function(d) {return d.pos.y * 20 + 10})
            .attr('cy', function(d) {return d.pos.x * 20 + 10})
            .style("stroke-opacity", 0.6)
            .style("fill", function(d) {return 'url(#grad' + d.pos.id})
            .on('click', function(d) {
                console.log(d);
                var text = 'id' + JSON.stringify(d.id)
                    + ' purity: ' + parseFloat(d.values.purity[0]).toFixed(8)
                    + ' completeness: ' + parseFloat(d.values.completeness[0]).toFixed(8);
                self.messages.message(text);
            })
            .on('mouseover', tip.show)
            .on('mouseout', tip.hide);
    };

    var add_legend = function(svg, data, data_info) {
        var offset = {
            'x': margin.left + self.dimens.width + legend_dimens.offset
                 + legend_count * legend_width(),
            'y': margin.top
        }

        var key = data_info.name;
        var stats = data_info.stats;

        var height = self.dimens.height;
        var width = legend_dimens.width;
        var colormap = genColorMap(colormaps[key])
        // console.log(10009, colormap, key)


        var legend = svg.append('g')
            .attr('transform', 'translate('
                + offset.x + ', '
                + offset.y + ')');

        var grad = legend.append('defs').append('linearGradient')
            .attr('id', 'legend-gradient')
            .attr('x1', '0%')
            .attr('y1', '100%')
            .attr('x2', '0%')
            .attr('y2', '0%')
            .attr('spreadMethod', 'pad')

        // Defining color stop spacing
        var pct = linspace(0, 100, colormap.length).map(function(d) {
            return Math.round(d) + '%';
        });

        // Adding gradient stops
        var colourPct = d3.zip(pct, colormap);
        colourPct.forEach(function(d) {
            grad.append('stop')
                .attr('offset', d[0])
                .attr('stop-color', d[1])
                .attr('stop-opacity', 1);
        });

        legend.append('rect')
            .attr('x', 0)
            .attr('y', 0)
            .attr('width', width)
            .attr('height', height)
            .style('fill', 'url(#legend-gradient)');

        var legendScale = d3.scaleLinear()
            .domain([stats.min, stats.max])
            .range([height, 0]);

        var legendAxis = d3.axisRight(legendScale)
            .ticks(5)
            .tickFormat(d3.format(".8f"));


        legend.append("g")
            .attr("class", "legend axis")
            .attr("transform", "translate(" + 25 + ", 0)")
            .call(legendAxis);

        legend_count += 1;
    };

}

var genColorMap = function(key) {
    colors = {
        'viridis': [
            '#440154', '#481567', '#482677', '#453781', '#404788',
            '#39568c', '#33638d', '#2d708e', '#287d7e', '#238a8d',
            '#1f968b', '#20a387', '#29af7f', '#3cbb75', '#55c667',
            '#73d055', '#95d840', '#b8de29', '#dce319', '#fde725'
        ],
        'bw': ['#000000', '#aaaaaa']
    }

    var viridis_r = colors['viridis'].slice();
    colors['viridis_r'] = viridis_r;
    viridis_r.reverse();

    return colors[key]
}

var genColorScale = function(stats, color) {
    var range = genColorMap(color)

    console.log(stats, range)
    var colorScale = d3.scaleLinear()
        .domain(linspace(stats.min, stats.max, range.length))
        .range(range)
    return colorScale;
}

var get_data = function(callback, experiment, type) {
    var url = new URI(window.location.href);
    var experiment = url.segment(1);
    var type = url.segment(2);

    var url = URI('/data')
        .query({experiment: experiment, type: type});
    console.log(url.toString());

    $.get('/data', {
        type: type,
        experiment: experiment
    }, function(data, status) {
        if (status == 'success' && data != null) {
            // console.log('data: ' + data.points.purity);
            console.log('status: ' + status);
            console.log(data)

            callback(data)
        }
    });
};

var defstep = function(start, end, n) {
    return (end - start) / n
}

var linspace = function(start, end, n) {
    var out = [];
    var delta = (end - start) / (n - 1);

    var i = 0;
    while(i < (n - 1)) {
        out.push(start + (i * delta));
        i++;
    }

    out.push(end);
    // console.log(out)
    return out;
};

var run = function() {
    console.log(10)
    var data = [4, 8, 15, 16, 23, 42];
    var plotter = new aligned_plot_4d($('div#chart'));
    get_data(plotter.plot, 'random-500-p', 'sorted');

    plotter.messages.message('test');
}


$(document).ready(function() {
    run()
})