# -*- coding: UTF-8 -*-
import subprocess
import urllib2
from datetime import datetime

import pymongo
import requests
from bs4 import BeautifulSoup


class spider:
    start_url = "http://www.jb1000.com/"

    def __init__(self):
        # 初始化数据库连接相关
        # mc = pymongo.MongoClient(mongo_ip, mongo_port)
        print '--初始化数据库连接完成--'

    '''
    爬取最新资料数据（多种方式）
    1. requests爬取
    2. urllib2爬取
    3. curl爬取
    '''
    def run_spider(self):
        # 分析发现 start_url并无法精准的获取资源列表
        url = "http://www.jb1000.com/Resources/ExamPaperDetails.aspx"
        # self.request_spider(url)
        self.urllib2_spider(url)
        # self.curl_spider(url)

    def request_spider(self, url):
        # get/post请求
        req = requests.get(url)
        # r = request.post(url, data = {'key': 'value'})
        html = req.text
        # 使用BeautifulSoup进行解析
        soup = BeautifulSoup(html, 'lxml')
        self.parse_page(soup, url)

    def urllib2_spider(self, url):
        header = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;"}
        request = urllib2.Request(url, headers=header)
        page = urllib2.urlopen(request)
        soup = BeautifulSoup(page.read(), 'lxml')
        self.parse_page(soup, url)

    def curl_spider(self, url):
        # 使用代理ip方式
        proxy_ip = "118.187.58.35:53281 "
        ip_url = proxy_ip + url
        curl_text = subprocess.Popen('curl -x ' + ip_url, shell=True, stdout=subprocess.PIPE)
        soup = BeautifulSoup(curl_text.stdout.read(), 'lxml')
        self.parse_page(soup, url)

    # 进行页面解析判断是否需要获取下一页信息，默认查询从当前日期的三天数据
    def parse_page(self, soup, url, days=3):
        list_body = soup.find('div', class_='list')
        try:
            # 如果超过days时间则不需要解析该数据
            time = str(datetime.now().year) + '-' + list_body.find('span', class_='listtime').get_text().encode(
                "UTF-8").strip()
            res_time = datetime.strptime(time, '%Y-%m-%d')
            # 判断是否需要获取下一页信息
            if (datetime.now() - res_time).days < days:
                # 解析页面中数据并存储
                self.parse_info(url, list_body.findAll('a'), days)
                # 获取下一页url，直到没有最新数据为止
                if soup.find('div', id='paginationzong'):
                    page_change = soup.find('div', id='paginationzong').findAll('a')
                else:
                    page_change = []
                    print 'page change error , no next page'
                for page in page_change:
                    if u'下一页' in page.get_text():
                        next_href = url.split('?')[0] + page['href']
                print 'page index:' + next_href
                self.request_spider(next_href)
        except Exception as e:
            print 'Parse page: An exception occurred! url:' + url + " reason:" + str(e)

# 解析当前页面信息
    def parse_info(self, url, info_body, days):
        for body in info_body:
            href = url.split('/Resources')[0] + body['href'].split('..')[1]
            # 解析资料数据
            html = urllib2.urlopen(href)
            soup = BeautifulSoup(html, 'lxml', from_encoding='utf8')
            body = soup.find('div', id='maincolumn_content')
            try:
                time = body.find('span', id='lblUpdateTime').get_text()
                res_time = datetime.strptime(time, '%Y/%m/%d %H:%M:%S')
                # 判断是否需要进行其他数据解析
                if (datetime.now() - res_time).days > days:
                    return
            except Exception as e:
                print 'Parse time info: An exception occurred! url:' + href + " reason:" + str(e)
            # 解析之前先判断表中是否存在该数据，存在直接跳出
            try:
                res_title = body.find('span', id='lblSoftName').get_text()
                res_class = body.find('span', id='lblApp_grade').get_text()
                res_version = body.find('span', id='lblSoftVersion').get_text()
                res_type = body.find('span', id='lblSoftType').get_text()
                res_downcount = body.find('span', id='lblHits').get_text()
                res_point = body.find('span', id='lblInfoPoint').get_text()
                doc = {
                    'res_date': res_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'res_title': res_title,
                    'res_version': res_version,
                    'res_url': href,
                    'res_point': res_point,
                    'res_downcount': res_downcount,
                    'spider_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'res_type': res_type,
                    'res_class': res_class,
                }
                # 入库操作
                print "save : " + doc["res_url"] + " title : " + doc["res_title"]
            except Exception as e:
                print 'Parse info: An exception occurred! url:' + href + " reason:" + str(e)


if __name__ == '__main__':
    spider = spider()
    spider.run_spider()
