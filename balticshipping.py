#! /usr/bin/env python3
# -*- encoding:utf-8 -*-

import csv
import json
import requests
from time import localtime
from urllib.parse import urlencode
# from requests.packages.urllib3.exceptions import InsecureRequestWarning # 禁用安全请求警告
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# from pymongo import MongoClient
# from pyquery import PyQuery as pq

# Total=208916
DATAFILE = './data.csv'
MAX_PAGE = 3 # 23213
PAGESIZE = 16 # 9
URL = 'https://www.balticshipping.com/'


headers = {
    'Host': 'www.balticshipping.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'zh,zh-CN;q=0.8,zh-TW;q=0.6,zh-HK;q=0.4,en-US;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.balticshipping.com/vessels',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Access-Token': '',
    'Content-Length': '741',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Cookie': 'id=null; key=null; level=null'
}
contry_dic = {}
vessel_dic = {}
engine_dic = {}

# TODO: Save to MongoDB
# client = MongoClient()
# db = client['ship']
# collection = db['ship'] 
# def save_to_mongo(result):
#     if collection.insert(result):
#         print('Saved to Mongo')

def get_dic():
    global contry_dic, vessel_dic, engine_dic
    req = 'dictionary[]=countrys:0&dictionary[]=vessel_types:0&dictionary[]=engine_types:0'
    try:
        response = requests.post(URL, req, headers=headers, verify=False)
        if response.status_code == 200:
            dictionary = response.json()['data']['dictionary']
            contry_dic = {item['id']:item['name'] for item in dictionary['countrys']['array']}
            vessel_dic = {item['id']:item['name'] for item in dictionary['vessel_types']['array']}
            engine_dic = {item['id']:item['name'] for item in dictionary['engine_types']['array']}
            # print(json.dumps(contry_dic, indent=2, separators=(',', ':')))
    except requests.ConnectionError as e:
        print('Error', e.args)


def get_info(page):
    # Request Body:
    # [{
    #     'module': 'ships',
    #     'action': 'list',
    #     'id': 0,
    #     'data': [{
    #         'name': 'search_id',
    #         'value': 0
    #     }, {
    #         'name': 'name',
    #         'value': ''
    #     }, {
    #         'name': 'imo',
    #         'value': ''
    #     }, {
    #     }, {
    #         'name': 'page',
    #         'value': page
    #     }],
    #     'sort': '',
    #     'limit': 9,
    #     'stamp': 0
    # }, {
    #     'module': 'top_stat',
    #     'action': 'list',
    #     'id': 0,
    #     'data': '',
    #     'sort': '',
    #     'limit': '',
    #     'stamp': 0
    # }]
    # req = {
    #     'request[0][module]': 'ships',
    #     'request[0][action]': 'list',
    #     'request[0][id]': '0',
    #     'request[0][data][0][name]': 'search_id',
    #     'request[0][data][0][value]': '0',
    #     'request[0][data][1][name]': 'name',
    #     'request[0][data][1][value]': '',
    #     'request[0][data][2][name]': 'imo',
    #     'request[0][data][2][value]': '',
    #     'request[0][data][3][name]': 'page',
    #     'request[0][data][3][value]': page,
    #     'request[0][sort]': '',
    #     'request[0][limit]': '1',
    #     'request[0][stamp]': '0',
    #     'request[1][module]': 'top_stat',
    #     'request[1][action]': 'list',
    #     'request[1][id]': '0',
    #     'request[1][data]': '',
    #     'request[1][sort]': '',
    #     'request[1][limit]': '',
    #     'request[1][stamp]': '0'
    # }
    req = {
        'request[0][limit]': PAGESIZE,
        'request[0][module]': 'ships',
        'request[0][action]': 'list',
        'request[0][data][3][name]': 'page',
        'request[0][data][3][value]': page
    }
    try:
        print(f'Getting {page} Page info..', end='')
        data=urlencode(req)
        # print(data)
        response = requests.post(URL, data, headers=headers, verify=False)
        if response.status_code == 200:
            resp = response.json()
            # print(json.dumps(resp, indent=2, separators=(',', ':')))
            return resp['data']['request'][0]['ships'], page
    except requests.ConnectionError as e:
        print('Error', e.args)

# def save_to_csv(result: list):
#     with open(DATAFILE, 'w+') as data:
#         writer = csv.writer(data)
#         writer.writerow(['index', 'IMO', 'MMSI', 'Name', 'Former', 'Vessel', 'Operating', 'Flag', 'Gross_tonnage',
#             'Deadweight', 'Lenght', 'Breadth', 'Engine_type', 'Engine_model', 'Engine_power',
#             'Build_year', 'Builder', 'Class_society', 'Home_port', 'Owner', 'Manager'])
#         writer.writerow(result)

def parse_data(ships: list, page: int):
    for i, ship in enumerate(ships):
        res = ship['data']
        result = [
            '%d-%d'%(page, i+1),
            res.get('imo'),
            res.get('mmsi'),
            res.get('name'),
            ';'.join([
                item['name']+'(%s, %s)'%(
                    item.get('year_until', '???'),
                    '???' if item.get('flag_id') is None else contry_dic[int(item['flag_id'])]
                ) for item in res.get('former_names', [])
                ]),
            vessel_dic[res.get('type')],
            res.get('operating_status'),
            contry_dic[res.get('type')],
            res.get('gt'),
            res.get('dwt'),
            res.get('length_'),
            res.get('breadth'),
            engine_dic[res.get('engine_type')],
            res.get('engine_model_name'),
            res.get('kw', '???')+'KW',
            '???' if not res.get('year_build') else localtime(int(res['year_build'])).tm_year,
            res.get('builder'),
            res.get('class_society'),
            res.get('home_port'),
            res.get('owner_name'),
            res.get('manager_name')
        ]
        print('/', end='')
        yield result

def main():
    get_dic()
    with open(DATAFILE, 'w+') as data:
        writer = csv.writer(data)
        writer.writerow(['index', 'IMO', 'MMSI', 'Name', 'Former', 'Vessel', 'Operating', 'Flag', 'Gross_tonnage',
            'Deadweight', 'Lenght', 'Breadth', 'Engine_type', 'Engine_model', 'Engine_power',
            'Build_year', 'Builder', 'Class_society', 'Home_port', 'Owner', 'Manager'])
        for page in range(1, MAX_PAGE + 1):
            json = get_info(page)
            results = parse_data(*json)
            for result in results:
                writer.writerow(result)

if __name__ == '__main__':
    main()
