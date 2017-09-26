var INSTRUMENTS = {
    "期货": ["主力合约", "商品指数", "大商所", "上期所", "郑商所", "中金所", "期权"],
    "股票": ["沪深A股", "中小板", "创业板", "港股"],
    "债券": ["国债", "金融债", "城投债", "企业债", "可转债", "可交换债"],
    "基金": ["分级基金", "ETF", "LOF", "定增基金", "封闭股基", "封闭债基"]
}

$(function() {
    var navbar_txt = INSTRUMENTS['期货'];
    change_navbar('期货', navbar_txt);

    //根据品种选择改变菜单条和显示列表信息
    $(".dropdown-menu a").click(function() {
        var oldnav_jq = $(".navbar-brand");
        var oldnav_txt = $.trim(oldnav_jq.text());
        var newnav_txt = this.text;

        navbar_txt = INSTRUMENTS[this.text];

        change_navbar(newnav_txt, navbar_txt);

        oldnav_jq.text(newnav_txt);
        oldnav_jq.append('<b class="caret"></b>');
        this.text = oldnav_txt;
    });

    //点击不同的市场分类改变显示信息
    // $("ul.nav>li>a").click(function() {  
    $("ul.nav").on("click", "li>a", function() {
        var brand_txt = $.trim($(".navbar-brand").text());
        var navbar_txt = this.text;
        var activebar = $("ul.navbar-nav>li.active>a");
        var active_txt = activebar.text();

        if (navbar_txt == active_txt) {
            console.log('navbar was actived.');
            return;
        }

        $("ul.nav>li.active").removeClass('active');
        $(this).parent().addClass('active');
        $.post("/segment/", { instrument: brand_txt, segment: navbar_txt }, build_table);

        console.log(brand_txt + ' : ' + navbar_txt + ',' + active_txt);
    });

    //双击行在打开新的页面
    $("tbody").on("click", "tr", function() {
        var contractid = $(this).children("td").eq(2).text(),
            instrument = $.trim($("a.navbar-brand").text()),
            segment = $("li.active").text();

        window.open("/hq/" + instrument + "/" + segment + "/" + contractid);
    });
});

//根据品种选择改变菜单条和显示列表信息
function change_navbar(brand_txt, navbar_txt) {
    var navbar = $(".nav");
    navbar.empty();
    for (x in navbar_txt) {
        if (x == 0) {
            navbar.append('<li class="active"><a href="#">' + navbar_txt[x] + '</a></li>');
            // 取对应的列表，需要发post信息
            $.post("/segment/", { instrument: brand_txt, segment: navbar_txt[x] }, build_table);
            continue;
        }
        navbar.append('<li><a href="#">' + navbar_txt[x] + '</a></li>');
    }
}

//显示信息列表
function build_table(data, status) {
    var head = $('table>thead>tr'),
        tbody = $("tbody");

    head.empty();
    tbody.empty();

    if (data.result != undefined) {
        console.log('result: ' + data.result);
        return;
    }

    var instrument = $.trim($("a.navbar-brand").text()),
        segment = $("li.active").text();

    var tdata = [],
        index = data.index,
        values = data.data,
        i = 0,
        j = 0;

    dataLength = index.length;


    if (instrument == "期货") {
        if (segment == "主力合约" | segment == "商品指数") {
            columns = ["序号", "合约名称", "合约代码", "交易市场"]
            for (x in columns) {
                var th = $('<th>' + columns[x] + '</th>');
                th.appendTo(head);
                console.log(columns[x]);
            }

            for (i; i < dataLength; i += 1) {
                tdata.push([
                    index[i] + 1, // 序号                    
                    values[i][6], // 合约名称
                    values[i][7], // 合约代码
                    values[i][3] // 交易市场
                ]);
            }
        } else if (segment == "大商所") {
            columns = ["序号", "品种", "合约代码", "最后交易日", "交易单位", "最小变动价位", "最后交割日", "开始交易日"]
            for (x in columns) {
                var th = $('<th>' + columns[x] + '</th>');
                th.appendTo(head);
                console.log(columns[x]);
            }

            for (i; i < dataLength; i += 1) {
                tdata.push([
                    index[i] + 1, // 序号   
                    values[i][7], // 品种                  
                    values[i][2], // 合约代码
                    values[i][4], // 最后交易日
                    values[i][6], // 交易单位
                    values[i][1], // 最小变动价位
                    values[i][3], // 最后交割日
                    values[i][0], // 开始交易日
                ]);
            }
        } else if (segment == "期权") {
            columns = ["序号", "品种", "合约代码", "最后交易日", "交易单位", "最小变动价位", "开始交易日"]
            for (x in columns) {
                var th = $('<th>' + columns[x] + '</th>');
                th.appendTo(head);
                console.log(columns[x]);
            }

            for (i; i < dataLength; i += 1) {
                tdata.push([
                    index[i] + 1, // 序号   
                    values[i][6], // 品种                 
                    values[i][2], // 合约代码
                    values[i][3], // 最后交易日
                    values[i][5], // 交易单位
                    values[i][1], // 最小变动价位
                    values[i][0], // 开始交易日
                ]);
            }
        }
    }

    if (tdata.length == 0) {
        console.log(segment + 'data is null!');
        return;
    }

    for (i in tdata) {
        var tr = $('<tr></tr>')
        tr.appendTo(tbody)
        var rowdata = tdata[i]
        for (j in rowdata) {
            var td = $('<td>' + rowdata[j] + '</td>')
            td.appendTo(tr);
        }
    }
}