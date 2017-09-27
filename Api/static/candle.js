$(function() {
    var pathname = location.pathname.split('/');

    params = { asset: pathname[2], segment: pathname[3], code: pathname[4], period: 'day' }

    $.post('/hq/data/', params, createchart)
        // set the allowed units for data grouping
    console.log(pathname)
})

function createchart(data, status) {
    var ohlc = [],
        volume = [],
        openInt = [],
        index = data.index,
        values = data.data,
        dataLength = 0,
        i = 0;

    dataLength = index.length;
    // set the allowed units for data grouping
    var groupingUnits = [
        [
            'week', // unit name
            [1] // allowed multiples
        ],
        [
            'month', [1, 2, 3, 4, 6]
        ]
    ];

    for (i; i < dataLength; i += 1) {
        ohlc.push([
            index[i], // the date
            values[i][0], // open
            values[i][1], // high
            values[i][2], // low
            values[i][3] // close
        ]);
        volume.push([
            index[i], // the date
            values[i][5] // the volume
        ]);
        openInt.push([
            index[i], // the date
            values[i][4] // the openInt
        ]);
    }
    // create the chart
    $('#candle').highcharts('StockChart', {
        rangeSelector: {
            selected: 1,
            inputDateFormat: '%Y-%m-%d'
        },
        title: {
            text: $("title").text()
        },
        xAxis: {
            dateTimeLabelFormats: {
                millisecond: '%H:%M:%S.%L',
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%m-%d',
                week: '%m-%d',
                month: '%y-%m',
                year: '%Y'
            }
        },
        yAxis: [{
            labels: {
                align: 'right',
                x: -3
            },
            title: {
                text: '股价'
            },
            height: '60%',
            lineWidth: 2
        }, {
            labels: {
                align: 'right',
                x: -3
            },
            title: {
                text: '成交量'
            },
            top: '65%',
            height: '35%',
            offset: 0,
            lineWidth: 2
        }],
        series: [{
            type: 'candlestick',
            name: $("title").text(),
            color: 'green',
            lineColor: 'green',
            upColor: 'red',
            upLineColor: 'red',
            tooltip: {},
            data: ohlc,
            dataGrouping: {
                units: groupingUnits
            }
        }, {
            type: 'column',
            name: 'Volume',
            data: volume,
            yAxis: 1,
            dataGrouping: {
                units: groupingUnits
            }
        }, {
            name: 'OpenInt',
            data: openInt,
            yAxis: 1,
            dataGrouping: {
                units: groupingUnits
            }
        }]
    });
}