# -*- coding: UTF-8 -*-
import json
import urllib2
from datetime import datetime

import pymongo
from bs4 import BeautifulSoup


class get_jb1000_res():
    now_time = datetime.now()
    provinces = [u'北京', u'天津', u'河北', u'山西', u'内蒙古', u'辽宁', u'吉林', u'黑龙江', u'上海', u'江苏', u'浙江', u'安徽', u'福建', u'江西',
                 u'山东', u'河南', u'湖北', u'湖南', u'广东', u'广西', u'海南', u'重庆', u'四川', u'贵州', u'云南', u'西藏', u'陕西', u'甘肃',
                 u'青海', u'宁夏', u'新疆', u'台湾', u'香港', u'澳门', u'其他']
    type_name = [u'试题试卷', u'学案/导学案', u'课件', u'教案', u'备课综合', u'素材', u'视频']
    base_subjects = [u'语文', u'数学', u'英语', u'物理', u'化学', u'生物', u'历史', u'地理', u'政治', u'思想品德', u'科学', u'音乐', u'美术',
                     u'信息技术',
                     u'历史与社会', u'体育与健康', u'劳动技术', u'综合', u'其他']
    classes = [u'高一', u'高二', u'高三', u'初一', u'初二', u'初三', u'七年级', u'八年级', u'九年级', u'六年级',
               u'五年级', u'四年级', u'三年级', u'二年级', u'一年级']
    versions = [u'人教版', u'苏教版', u'北师大版']

    def __init__(self):
        mc = pymongo.MongoClient(conf.mongo_ip, conf.mongo_port)
        self.db = mc['']
        self.collection = self.db[''] # mongo库

    # 获取url--科目/类型--学段（数据基本为固定的在一次查询出来后直接赋值给url_info_list减少消耗，长时间后可重新获取）
    def get_default_url_list(self):
        # 获取页面中年级栏的所有span标签
        map_url = "http://www.jb1000.com/Service/Map.html"
        url_subject_grade_list = []
        page = urllib2.urlopen(map_url)
        soup = BeautifulSoup(page, 'lxml', from_encoding='utf8')
        main_body = soup.find('div', id='main')
        # 解析高中部分的相关信息（url -- 科目/类型 -- 学段）
        res_child_list = main_body.find('div', class_='main_xueduan').findAll('div', class_='ziyuanzileiname')
        for res_child in res_child_list:
            res_a = res_child.findAll('a')
            for res in res_a:
                url_subject_grade_list.append(res['href'] + '--' + res.get_text() + '--' + u'高中')

        # 解析初中部分的相关信息（url -- 科目/类型 -- 学段）
        res_child_list = main_body.find('div', class_='main_xueduan1').findAll('div', class_='ziyuanzilei1')
        for res_child in res_child_list:
            res_a = res_child.findAll('a')
            for res in res_a:
                url_subject_grade_list.append(res['href'] + '--' + res.get_text() + '--' + u'初中')

        # 解析小学部分的相关信息（url -- 科目/类型 -- 学段）
        res_child_list = main_body.find('div', class_='main_xueduan2').findAll('div', class_='ziyuanzilei1')
        for res_child in res_child_list:
            res_a = res_child.findAll('a')
            for res in res_a:
                url_subject_grade_list.append(res['href'] + '--' + res.get_text() + '--' + u'小学')
        print json.dumps(url_subject_grade_list).decode("unicode-escape")
        return url_subject_grade_list

    # 解析页面中是信息并判断执行次数（是否继续解析下一页）
    def parse_page(self, url, info, days):
        html = urllib2.urlopen(url)
        soup = BeautifulSoup(html, 'lxml', from_encoding='utf8')
        list_body = soup.find('div', class_='list')
        try:
            time = str(datetime.now().year) + '-' + list_body.find('span', class_='listtime').get_text().encode("UTF-8").strip()
            res_time = datetime.strptime(time, '%Y-%m-%d')
            # 判断是否需要获取下一页信息
            if (self.now_time - res_time).days < days:
                # 解析页面中数据并存储
                self.parse_info(info, list_body.findAll('a'), days)
                # 获取下一页url，直到没有最新数据为止
                if soup.find('div', id='paginationzong'):
                    page_change = soup.find('div', id='paginationzong').findAll('a')
                elif soup.find('div', id='paginationgreen'):
                    page_change = soup.find('div', id='paginationgreen').findAll('a')
                elif soup.find('div', id='pagination'):
                    page_change = soup.find('div', id='pagination').findAll('a')
                elif soup.find('div', id='paginationblue'):
                    page_change = soup.find('div', id='paginationblue').findAll('a')
                else:
                    page_change = []
                    print 'page change error , no next page'
                for page in page_change:
                    if u'下一页'in page.get_text():
                        next_href = url.split('?')[0] + page['href']
                self.parse_page(next_href, info, days)
        except Exception as e:
            print 'Parse page: An exception occurred! url:' + url + " reason:" + str(e)

    # 解析当前页面信息
    def parse_info(self, info, info_body, days):
        for body in info_body:
            href = info.split('/Resources')[0] + body['href'].split('..')[1]
            # 解析资料数据
            html = urllib2.urlopen(href)
            soup = BeautifulSoup(html, 'lxml', from_encoding='utf8')
            body = soup.find('div', id='maincolumn_content')
            try:
                time = body.find('span', id='lblUpdateTime').get_text()
                res_time = datetime.strptime(time, '%Y/%m/%d %H:%M:%S')
                # 判断是否需要进行其他数据解析
                if (self.now_time - res_time).days > days:
                    return
            except Exception as e:
                print 'Parse time info: An exception occurred! url:' + href + " reason:" + str(e)
            # 解析之前先判断表中是否存在该数据，存在直接跳出
            if int(self.collection.find({'res_url': href}).count()) == 0:
                try:
                    res_title = body.find('span', id='lblSoftName').get_text()
                    # 通过标题解析省份
                    province = [x for x in self.provinces if x in res_title]
                    if len(province) > 0:
                        res_province = province[0]
                    else:
                        res_province = u"全国"
                    # 解析科目
                    subject = [x for x in self.base_subjects if x.encode("UTF-8") in info.split("--")[1]]
                    if len(subject) > 0:
                        res_subject = subject[0]
                    else:
                        res_subject = ''
                    # 解析年级
                    re_class = [x for x in self.classes if x in body.find('span', id='lblApp_grade').get_text()]
                    if len(re_class) > 0:
                        res_class = re_class[0]
                    else:
                        res_class = u'其他'
                    # 解析版本
                    version = [x for x in self.versions if x in body.find('span', id='lblSoftVersion').get_text()]
                    if len(version) > 0:
                        res_version = version[0]
                    else:
                        res_version = u'其他'
                    # 解析类型
                    retype = [x for x in self.type_name if x in body.find('span', id='lblSoftType').get_text()]
                    if len(retype) > 0:
                        res_type = retype[0]
                    else:
                        res_type = u"其他"
                    # 解析初高中
                    grade = [x for x in [u"小学", u"初中", u"高中"] if x.encode("UTF-8") in info.split("--")[2]]
                    if len(grade) > 0:
                        res_grade = grade[0]
                    else:
                        res_grade = u"其他"
                    res_downcount = body.find('span', id='lblHits').get_text()
                    res_point = body.find('span', id='lblInfoPoint').get_text()
                    doc = {
                        'res_date': res_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'res_title': res_title,
                        'res_version': res_version,
                        'res_subject': res_subject,
                        'res_url': href,
                        'res_point': res_point,
                        'res_downcount': res_downcount,
                        'res_grade': res_grade,
                        'spider_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'res_type': res_type,
                        'res_class': res_class,
                        'res_intro': '',
                        'res_province': res_province,
                        'site_id': 'jb1000'
                    }

                    # 入库操作
                    self.collection.insert(doc)
                    self.db.res.save(doc)
                    print "save : " + doc['res_url']
                except Exception as e:
                    print 'Parse info: An exception occurred! url:' + href + " reason:" + str(e)

    def run(self, days):
        for info in self.url_info_list:
            url = info.split("--")[0]
            self.parse_page(url, info, days)


if __name__ == '__main__':
    get_jb1000_res = get_jb1000_res()
    get_jb1000_res.run(3)
