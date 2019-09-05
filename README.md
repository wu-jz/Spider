# Spider
爬虫脚本

根据目标站进行分析，可通过导航地图或者根据url进行数据精准获取
在爬取中ip容易被封禁，需要使用代理ip进行爬取，可以使用一下几种方式进行代理获取：
urllib2:
proxy = {"http" : "118.187.58.35:53281"}
proxy_support = urllib2.ProxyHandler()
opener = urllib2.build_opener(proxy_support)
urllib2.install_opener(opener):
html = urllib2.urlopen("指定网址").read()

curl:
 curl在python中可直接通过curl_text = subprocess.Popen('curl -x ' + ip + url, shell=True, stdout=subprocess.PIPE)进行获取
