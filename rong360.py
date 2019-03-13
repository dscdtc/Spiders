#!/usr/bin python3
#encoding:utf-8
import csv
# pip install pyquery
from pyquery import PyQuery as pq
PAGE = 100 # 2~1001
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}


data = open('./result.csv', 'w', encoding='utf-8')
writer = csv.writer(data)
writer.writerow(['Url', 'Title', 'Num', 'Content'])

for i in range(1, PAGE):
    print('\r\nPhrase page %d'%i)
    c = pq(url='https://bbs.rong360.com/forum-129-%d.html'%i, headers=headers)
    urls = c('.s.xst')
    for url in urls.items():
        result = []
        url = url.attr('href')
        content = pq(url='https://bbs.rong360.com/'+url, headers=headers)
        result.append(url)
        result.append(content('#thread_subject').text())  # title
        result.append(content('.hm.ptn span.xi1').text())  # num
        result.append(content('.pcb .t_f:first-child').text().split('\n')[0])  #content
        writer.writerow(result)
        print(url)

data.close()
