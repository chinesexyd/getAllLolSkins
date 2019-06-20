import requests
import re
import json
import os
import time

'''
每个英雄的皮肤id
https://ossweb-img.qq.com/images/lol/web201310/skin/big266001.jpg 剑魔
https://ossweb-img.qq.com/images/lol/web201310/skin/big103002.jpg 阿狸

每个英雄的英雄id
https://lol.qq.com/data/info-defail.shtml?id=Ahri 阿狸
https://lol.qq.com/data/info-defail.shtml?id=Aatrox 剑魔

每个英雄的所有皮肤id
https://lol.qq.com/biz/hero/Ahri.js

所有英雄的id
https://lol.qq.com/biz/hero/champion.js
'''


# 模式：面向对象
class Spider(object):
    def __init__(self):
        self.count = dict()
        self.not_ok = ['/', '\\', '|', '<', '>', '*', ':', '?', '"']

    # 1.找到所有英雄的英文名
    def start_request(self):
        text = requests.get("https://lol.qq.com/biz/hero/champion.js").text
        data = re.findall(r'LOLherojs.champion=(.+?);', text)[0]
        heros_name_id = json.loads(data)
        heros_name = heros_name_id['keys'].values()
        self.next_request(heros_name)

    # 2.取英雄皮肤id
    def next_request(self, heros_name):
        for hero_name in heros_name:
            text = requests.get("https://lol.qq.com/biz/hero/{}.js".format(hero_name)).text
            data = re.findall(r'LOLherojs.champion.{}=(.+?);'.format(hero_name), text)[0]
            hero_skins_other = json.loads(data)
            hero_data = hero_skins_other['data']
            englishname = hero_data['id']
            name = hero_data['name']
            title = hero_data['title']
            allname = "{}-{}-{}".format(name, title, englishname)

            self.count['英雄数量'] = self.count.get('英雄数量', 0) + 1  # 对英雄数量进行累计

            for skin in hero_data['skins']:
                skin_id = skin['id']
                skin_name = skin['name']
                if skin_name == 'default':
                    skin_name_list = allname.split('-')[:-1]
                    skin_name = ''.join(skin_name_list) + '默认皮肤'
                self.getlink_skins(skin_id, allname, skin_name)
                self.count['皮肤数量'] = self.count.get('皮肤数量', 0) + 1  # 对皮肤数量进行累加
                self.count[allname] = self.count.get(allname, 0) + 1  # 对每个英雄的皮肤数量进行累加
        self.getcount()

    # 3.拼接皮肤链接
    def getlink_skins(self, skin_id, allname, skin_name):
        img = requests.get('https://ossweb-img.qq.com/images/lol/web201310/skin/big{}.jpg'.format(skin_id)).content
        self.download_img(img, allname, skin_name)

    # 4.下载、保存皮肤
    def download_img(self, img, allname, skin_name):
        # 创建每个英雄的文件夹
        filename = "C:\\我的文档\\picture\\英雄联盟全皮肤\\{}".format(allname)
        if not os.path.exists(filename):
            os.makedirs(filename)
            print('新建文件夹{}'.format(filename))
        # 判断图片名称是否存在非法字符
        for n in self.not_ok:
            if n in skin_name:
                skin_name = skin_name.replace(n, '')
        with open("{}\\{}.jpg".format(filename, skin_name), 'wb') as f:
            f.write(img)
            print("{}.jpg已经保存".format(skin_name))
            time.sleep(1)

    # 5.英雄数据统计
    def getcount(self):
        with open("C:\\我的文档\\picture\\英雄联盟全皮肤\\英雄数据.txt", 'w', encoding='utf-8') as fi:
            for key, value in self.count.items():
                fi.writelines("{}-{}{}".format(key, value, '\n'))


spider = Spider()
spider.start_request()
