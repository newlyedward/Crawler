var chart = null;

$(function() {
    var url = window.location.href;
    // set the allowed units for data grouping
    var groupingUnits = [
        [
            'week', // unit name
            [1] // allowed multiples
        ],
        [
            'month', [1, 2, 3, 4, 6]
        ]
    ]

    chart = new Highcharts.Chart({
        chart: {
            renderTo: 'candle',
            type: 'StockChart',
            events: {
                load: requestData
            }
        },
        rangeSelector: {
            selected: 2,
            inputDateFormat: '%Y-%m-%d'
        },
        title: {
            text: '焦炭主力'
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
            name: '焦炭主力',
            color: 'green',
            lineColor: 'green',
            upColor: 'red',
            upLineColor: 'red',
            tooltip: {},
            data: [],
            dataGrouping: {
                units: groupingUnits
            }
        }, {
            type: 'column',
            name: 'Volume',
            data: [],
            yAxis: 1,
            dataGrouping: {
                units: groupingUnits
            }
        }]
    });
    console.log('main function finished')
})

function requestData() {
    $.post("/data/", { code: 'JL8', period: 'day' },
        function(data) {
            //data is json that says string
            console.log("get k line!")
            var ohlc = [],
                volume = [],
                index = data.index,
                values = data.data,
                dataLength = 0,
                i = 0;
            dataLength = index.length;
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
            }

            chart.update({
                series: [{
                    data: ohlc
                }, {
                    data: volume
                }]
            });
        }, 'json');
}