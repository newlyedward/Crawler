大连商品交易所
=
商品合约信息
-
### 1、爬取路径
    http://www.dce.com.cn/  玉米    
        xpath：/html/body/div[3]/div/div[1]/div/div[3]/ul/li[2]/div/div/div[1]/div[1]/ul/li[3]/a
        css：.pzzx_box01 > ul:nth-child(2) > li:nth-child(3) > a:nth-child(1)
    http://www.dce.com.cn/dalianshangpin/sspz/ym/index.html 期货合约
        xpath：/html/body/div[4]/div[2]/div[2]/div[2]/div[2]/div/div[2]/ul/li[1]/a
        css：#\31 1629 > div:nth-child(2) > ul:nth-child(1) > li:nth-child(1) > a:nth-child(1)
    http://www.dce.com.cn/dalianshangpin/sspz/ym/hyygz/486238/index.html
                         /dalianshangpin/sspz/487477/487481/1500303/index.html        
        xpath：/html/body/div[4]/div/div/div[2]/div[2]/div[2]/table[1]/tbody/tr[1]
              /html/body/div[4]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/table/tbody/tr[1]/td[2]/p/span[1]
              /html/body/div[4]/div/div/div[2]/div[2]/div[2]/table[1]/tbody/tr[1]/td[2]/p
              /html/body/div[4]/div/div/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[2]
              table/tbody/tr[2]/td[1]/p/span[1]
        css：#zoom > table:nth-child(3)
        html body div.container_w div#detail_content.container_inner.column div#12888.portlet div div.detail_inner div#zoom.detail_content div#infoContent div div table.MsoNormalTable tbody tr td
        .MsoNormalTable > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1)
        #zoom > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1)
        
### 日成交持仓排名
    批量下载
    http://www.dce.com.cn/publicweb/quotesdata/exportMemberDealPosiQuotesBatchData.html
    memberDealPosiQuotes.variety=a       不起作用
    memberDealPosiQuotes.trade_type=0
    contract.contract_id=all
    contract.variety_id=a  不起作用
    year=2017              缺省是当天
    month=8                起始月份为0
    day=04
    batchExportFlag=batch
    http://www.dce.com.cn/publicweb/quotesdata/exportMemberDealPosiQuotesData.html
    memberDealPosiQuotes.variety=a
    memberDealPosiQuotes.trade_type=0
    contract.contract_id=all
    contract.variety_id=a
    year=2017
    month=8
    day=04
    exportFlag=txt
        
    