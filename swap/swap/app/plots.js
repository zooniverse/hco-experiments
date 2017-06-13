
var aligned_plot = new function() {
    var self = this;
    var margin = {
        'left': 50,
        'right': 50,
        'top': 50,
        'bottom': 50
    };
    var radius = 20;
    var legend_dimens = {
        'width': 20,
        'tick_margin': 40,
        'offset': 10
    }

    var legend_count = 0;
    var colormaps = {
        'purity': 'viridis',
        'completeness': 'viridis'
    }

    var tip_text = function(d) {
        var purity = d.purity.toFixed(3);
        var completeness = d.completeness.toFixed(3);

        var detail_span = function(text) {
            return $('<div/>').append($('<span/>', {
                class: 'tip-detail',
                text: text
            })).html();
        };

        text = 'Golds ' + detail_span(d.golds)
            + ' n ' + detail_span(d.n)
            + ' purity ' + detail_span(purity)
            + ' completeness ' + detail_span(completeness);

        node =  $('<div/>', {
            id: 'test',
            text: text
        });
        node.append($('<span/>'));

        out = $('<div/>').append(node)
        console.log(out.html());

        return out.text()
    }

    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function(d) {
            return tip_text(d);
        });

    this.plot = function(data) {
        var chart = d3.select('div#chart');
        var svg = init_svg(chart, data);
        add_gradients(svg, data);
        add_points(svg, data);

        add_legend(svg, data, 'purity');
        add_legend(svg, data, 'completeness');
    };

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
        var svg = chart.append('svg')
            .attr('width', full_width + 'px')
            .attr('height', full_height + 'px')
            .call(tip);

        // var xScale = d3.scaleOrdinal([linspace(0, width, data.width)])
        //     .domain(d3.range(0, data.width, 1));

        // var yScale = d3.scaleOrdinal([linspace(0, height, data.height)])
        //     .domain(d3.range(0, data.height, 1));

        // var xAxis = d3.svg.axis()
        //     .scale(xScale)
        //     .orient('bottom');

        // var yAxis = d3.svg.axis()
        //     .scale(yScale)
        //     .orient('left');

        // var xAxisSvg = svg.append('g')
        //     .attr('class', 'x axis')
        //     .attr('transform', 'translate(0,' + 0 + ')');
        //     .call(xAxis);

        // var yAxisSvg = svg.append('g')
        //     .attr('class', 'y axis');
        //     .call(yAxis);

        return svg;
    };

    var add_gradients = function(svg, data) {
        var scales = {
            'pur': genColorScale(data.purity, colormaps.purity),
            'comp': genColorScale(data.completeness, colormaps.completeness)
        };

        grads = svg.append('defs').selectAll('linearGradient')
            .data(data.points)
            .enter()
            .append('linearGradient')
            .attr('id', function(d) {return 'grad' + d.id})
            .attr("x1", "0%")
            .attr("x2", "100%")
            .attr("y1", "0%")
            .attr("y2", "100%")
        grads.append('stop')
            .attr('offset', '50%')
            .style('stop-color', function(d) {return scales.comp(d.completeness)})
        grads.append('stop')
            .attr('offset', '50%')
            .style('stop-color', function(d) {return scales.pur(d.purity)})

        console.log(scales.pur(.45));
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
            .attr('cx', function(d) {return d.y * 20 + 10})
            .attr('cy', function(d) {return d.x * 20 + 10})
            .style("stroke-opacity", 0.6)
            .style("fill", function(d) {return 'url(#grad' + d.id})
            .on('click', function(d) {console.log(d)})
            .on('mouseover', tip.show)
            .on('mouseout', tip.hide);
    };

    var add_legend = function(svg, data, key) {
        var offset = {
            'x': margin.left + self.dimens.width + legend_dimens.offset
                 + legend_count * legend_width(),
            'y': margin.top
        }

        var stats = data[key]
        var height = self.dimens.height;
        var width = legend_dimens.width;
        var colormap = genColorMap(colormaps[key])
        console.log(10009, colormap, key)


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
            console.log(d)
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
            .tickFormat(d3.format(".2f"));


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

// var add_legend = function(svg, offset, colormap, stats) {
//     var height = offset.y
//     var width = 20;

//     var legend = svg.append('g')
//         .attr('transform', 'translate(' + offset.x + (', 0)'))
//     var grad = legend.append('defs').append('linearGradient')
//         .attr('id', 'legend-gradient')
//         .attr('x1', '0%')
//         .attr('y1', '100%')
//         .attr('x2', '0%')
//         .attr('y2', '0%')
//         .attr('spreadMethod', 'pad')

//     var pct = linspace(0, 100, colormap.length).map(function(d) {
//         console.log(d)
//         return Math.round(d) + '%';
//     });

//     var colourPct = d3.zip(pct, colormap);
//     colourPct.forEach(function(d) {
//         grad.append('stop')
//             .attr('offset', d[0])
//             .attr('stop-color', d[1])
//             .attr('stop-opacity', 1);
//     });

//     legend.append('rect')
//         .attr('x', 0)
//         .attr('y', 0)
//         .attr('width', width)
//         .attr('height', height)
//         .style('fill', 'url(#legend-gradient)');

//     var legendScale = d3.scaleLinear()
//         .domain([stats.min, stats.max])
//         .range([height, 0]);

//     var legendAxis = d3.axisRight(legendScale)
//         .ticks(5)
//         .tickFormat(d3.format(".2f"));


//     legend.append("g")
//         .attr("class", "legend axis")
//         .attr("transform", "translate(" + 25 + ", 0)")
//         .call(legendAxis);
// }

// var plot = function(data) {

//     var scale = {
//         'pur': genColorScale(data.purity, 'viridis'),
//         'comp': genColorScale(data.completeness, 'bw')
//     };

//     console.log(scale.pur(10))
//     console.log(scale.pur(.4))
//     console.log(scale.pur(.01))

//     var chart = d3.select('div#chart');
//     var svg = chart.append('svg')
//         .attr('width', '5000px')
//         .attr('height', '5000px');

//     // var xAxis = d3.svg.axis()
//     //     .scale(xScale)
//     //     .orient('bottom');

//     // var yAxis = d3.svg.axis()
//     //     .scale(yScale)
//     //     .orient('left');

//     var xAxisSvg = svg.append('g')
//         .attr('class', 'x axis')
//         .attr('transform', 'translate(0,' + 0 + ')');
//         // .call(xAxis);

//     var yAxisSvg = svg.append('g')
//         .attr('class', 'y axis');
//         // .call(yAxis);

//     grads = svg.append('defs').selectAll('linearGradient')
//         .data(data.points)
//         .enter()
//         .append('linearGradient')
//         .attr('id', function(d) {return 'grad' + d.id})
//         .attr("x1", "0%")
//         .attr("x2", "100%")
//         .attr("y1", "0%")
//         .attr("y2", "100%")
//     grads.append('stop')
//         .attr('offset', '50%')
//         .style('stop-color', function(d) {return scale.comp(d.completeness)})
//     grads.append('stop')
//         .attr('offset', '50%')
//         .style('stop-color', function(d) {return scale.pur(d.purity)})

//     circles = svg.append('g').selectAll('circle')
//         .data(data.points)
//         .enter()
//         .append('circle')
//         .attr('r', '10' + 'px')
//         .attr('cx', function(d) {return d.y * 20 + 10})
//         .attr('cy', function(d) {return d.x * 20 + 10})
//         .style("stroke-opacity", 0.6)
//         .style("fill", function(d) {return 'url(#grad' + d.id})
//         .on('click', function(d) {console.log(d)});

//     add_legend(
//         svg, {'x': (data.width + 1) * 20, 'y': data.height * 20},
//         genColorMap('viridis'), data.purity)
//     add_legend(
//         svg, {'x': (data.width + 3) * 20, 'y': data.height * 20},
//         genColorMap('bw'), data.completeness)
// }

var get_data = function(callback) {
    $.get('/data?type=sorted', null, function(data, status) {
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
    console.log(out)
    return out;
};

var run = function() {
    console.log(10)
    var data = [4, 8, 15, 16, 23, 42];
    get_data(aligned_plot.plot)
}


$(document).ready(function() {
    run()
})