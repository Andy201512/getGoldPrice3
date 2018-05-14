# -*- coding: utf-8 -*-
import scrapy, re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from getGoldPrice3.items import GoldpriceItem
from bs4 import BeautifulSoup

class GetgpspiderSpider(CrawlSpider):
    name = 'getGPspider'
    allowed_domains = ['sge.com.cn']
    start_urls = ['http://www.sge.com.cn/sjzx/mrhqsj?p=1']
    
    for i in range(249):
            start_urls.append('http://www.sge.com.cn/sjzx/mrhqsj?p=' + str(i+1))

    rules = (
        Rule(LinkExtractor(allow=('top')), callback='parse_item'),
    )
    
    def parse_item(self, response):

        #初始化黄金价格item
        item = GoldpriceItem()
        
        #页面item数据xpath设置
        it_day_xp = '/html/body/div[6]/div/div[2]/div[2]/div[1]/p/span[2]/text()'
        x_axis = 0
        y_axis = 0
        it_name_xp = ['string(/html/body/div[6]/div/div[2]/div[2]/div[2]/table/tbody/tr[', 'y', ']/td[1])']
        it_price_xp = ['string(/html/body/div[6]/div/div[2]/div[2]/div[2]/table/tbody/tr[', 'y', ']/td[', 'x', '])']

        #页面表行、表头xpath要素列表
        tr_lt_xp = [
                        'string(',
                        'count(',
                        '/html/body/div[6]/div/div[2]/div[2]/div[2]/table/tbody/tr/td[1])',
                        '/html/body/div[6]/div/div[2]/div[2]/div[2]/table/tbody/tr[',
                        ']/td[1])',
                    ]
        th_lt_xp = [
                        'string(',
                        'count(',
                        '/html/body/div[6]/div/div[2]/div[2]/div[2]/table/tbody/tr[1]/td)',
                        '/html/body/div[6]/div/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[',
                        '])',
                    ]
        
        #表行、表头长度获取
        tr_len = int(float(response.selector.xpath(tr_lt_xp[1] + tr_lt_xp[2]).extract()[0]))
        th_len = int(float(response.selector.xpath(th_lt_xp[1] + th_lt_xp[2]).extract()[0]))
        
        #初始化表行、表头信息数组
        tr_list = []
        th_list = []

        #取出表行信息存入数组
        for i in range(tr_len):
            tr_list.append(response.xpath(tr_lt_xp[0] + tr_lt_xp[3] + str(i+1) + tr_lt_xp[4]).extract())

        #表行数组空白字符排空
        for k in range(len(tr_list)):
            tr_list[k] = re.sub('\s','',tr_list[k][0])

        #尝试捕获“Au99.99”行标
        try:
            y_axis=tr_list.index('Au99.99')
        except ValueError:
            try:
                y_axis=tr_list.index('Au9999')
            except ValueError:
                #改用使用BeautifulSoup解析，并存储信息，返回item
                tr_list = []
                th_list = []
                
                soup = BeautifulSoup(response.body, 'html5lib')
                
                for row_str in soup.table.find(text=re.compile('收')).find_parent('tr').find_all(re.compile('td|th')):
                    re_str = re.sub('\s', '', row_str.get_text())
                    
                    if re_str != '' and re_str != '合约' and re_str != '品种' and re_str != '交易品种':
                        tr_list.append(re_str)

                for row_str in soup.table.find(text=re.compile('Au99.99|Au9999')).find_parent('tr').find_all(re.compile('td|th')):
                    re_str = re.sub('\s', '', row_str.get_text())
                    
                    if re_str != '':
                        th_list.append(re_str)
                
                #store item
                d = soup.find('i',text='时间:').parent.get_text()
                item['day'] = re.search(r'\d{4}-\d{2}-\d{2}', d).group()
                item['name'] = th_list[0]
                item['price'] = th_list[tr_list.index('收盘价')+1]
                item['url'] = response.url
                item['selector'] = 'BeautifulSoup'
                
                return item

        #更新name、price的xpath
        it_name_xp[1] = str(y_axis+1)
        it_price_xp[1] = str(y_axis+1)

            
        #取出表头信息存入数组
        for i in range(th_len):
            th_list.append(response.xpath(th_lt_xp[0] + th_lt_xp[3] + str(i+1) + th_lt_xp[4]).extract())

        #表头信息数组空白字符排空
        for k in range(len(th_list)):
            th_list[k] = re.sub('\s','',th_list[k][0])


        #尝试捕获“收盘价”表头列标
        try:
            x_axis = th_list.index('收盘价')
        except ValueError:
            #输出错误信息
            x_axis = th_list.index('Close')#2016年4月12日（http://www.sge.com.cn/sjzx/mrhqsj/537221?top=789398439266459648）
            self.logger.info('表头数组', th_list)

        #更新price的xpath
        it_price_xp[3] = str(x_axis+1)

        self.logger.info('Item page on %s! %s (%s, %s)', re.sub('\s','',response.xpath(it_day_xp).extract()[0]), response.url, x_axis, y_axis)
        
        #store item
        item['day'] = re.sub('\s','',response.xpath(it_day_xp).extract()[0])
        item['name'] = re.sub('\s','',response.xpath(''.join(it_name_xp)).extract()[0])
        item['price'] = re.sub('\s','',response.xpath(''.join(it_price_xp)).extract()[0])
        item['url'] = response.url
        item['selector'] = 'lxml'

        return item
