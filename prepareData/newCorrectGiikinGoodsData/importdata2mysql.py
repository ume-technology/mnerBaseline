# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:importdata2mysql.py
@Time:2023/2/9 13:07
@Read: 将存储莫模型预测后的商品标签的数据导入数据库中；
"""
import gc
import pickle
import pymysql
from functions import *

# 标签版本1.0 - 这些标签要存入数据库中；
labels = ["mar图案", "sce预防保护", "cro身体部位", "sce装修制造", "cro男性群体", "cro女性群体", "the胶皮革绒", "the高新技术", "sce户外娱乐",
          "cro工具建材", "cro厨房", "cro浴室", "cro生命元素", "sce吃美食", "sce整理搬运", "prt品类", "tim日常时间", "sce保洁洗漱",
          "sce交通出行", "sce运动健身", "cro居家", "cro弱势群体", "mar高效便捷", "mar风格", "mar舒适触感", "sce御寒保暖", "sce化妆美容", "mar人文宗教",
          "hod节日", "cro职场人群", "cro亲友群体", "the麻线丝棉", "sce购物送礼", "the植物原料", "mar口味", "mar款式", "mar颜色", "sce身体保健",
          "the金银铜铁", "tim秋冬时节", "sce维修检测", "sce乐业", "tim春夏时节", "cro家具设备", "cro有害元素", "cro办公学习", "cro娱乐场所"]

host = '192.168.4.210'
port = 3306
db = 'db'
user = 'zhimin'
passwd = 'uwV3n9bNPzUTf3N7'
sql = """  """
# conn = pymysql.connect(host=host, port=port, user=user, db=db, passwd=passwd, charset='utf-8')
# cursor = conn.cursor()
# data = cursor.fetchall()

# with open('./台湾/facebook.pick', 'rb') as fb:
#     fb_data = pickle.load(fb)
#
# with open('./台湾/google.pick', 'rb') as gg:
#     gg_data = pickle.load(gg)
#
# with open('./台湾/line.pick', 'rb') as line:
#     line_data = pickle.load(line)

with open('../../bigfiles/nerCodeBaseLineOutput/giikin_alltageddata_new/香港/tiktok.pick', 'rb') as tiktok:
    # with open('./台湾/tiktok.pick', 'rb') as tiktok:
    tiktok_data = pickle.load(tiktok)

with open('../../bigfiles/nerCodeBaseLineOutput/giikin_alltageddata_new/香港/google.pick', 'rb') as google:
    # with open('./台湾/google.pick', 'rb') as google:
    google_data = pickle.load(google)

with open('../../bigfiles/nerCodeBaseLineOutput/giikin_alltageddata_new/香港/line.pick', 'rb') as line:
    # with open('./台湾/line.pick', 'rb') as line:
    line_data = pickle.load(line)

with open('../../bigfiles/nerCodeBaseLineOutput/giikin_alltageddata_new/香港/facebook.pick', 'rb') as facebook:
    # with open('./台湾/facebook.pick', 'rb') as facebook:
    facebook_data = pickle.load(facebook)

# allTWData = tiktok_data + google_data + line_data + facebook_data
allTWData = pd.concat([tiktok_data, google_data, line_data, facebook_data], axis=0)
del tiktok
del google_data
del line_data
del facebook_data
gc.collect()

t = allTWData.head(10)


def tidy_goods_features(i):
    """
    首先完成goods tags的去重于分隔符的设定；为进一步的goods tags的切割做第一部的准备
    :param i:
    :return:
    """
    goodsTagsSet = set()
    tagsFromAdText = i['goodsfeatures']
    print(i['cleantext'])
    # print(tagsFromAdText)
    # print('*' * 10)
    goodsTagsList = ''
    for eachTag in tagsFromAdText:
        tagClsKey = eachTag[0]
        tagValue = eachTag[-1]
        tiny = tagClsKey + '-' + tagValue
        goodsTagsSet.add(tiny)
    goodsTagsList = list(goodsTagsSet)
    goodsTagsList2Str = "|".join(goodsTagsList)
    return goodsTagsList2Str


allTWData.loc[:, '整理去重得到商品标签'] = allTWData.apply(tidy_goods_features, axis=1)
# t.loc[:, '整理去重得到商品标签'] = allTWData.apply(tidy_goods_features, axis=1)  # todo change

allTWData = allTWData.drop(['goodsfeatures', 'ad_slogans', 'impressions_cnt', 'clicks_cnt', 'add_cart_cnt',
                            'people_cover_cnt', 'checkout_cnt', 'interest_words', 'order_cnt', 'conversions_rate',
                            '近15天广告成本', '广告成本', '单次展示成本', '单次点击成本', '单次加购成本', '单次支付成本', '千次展示成本'], axis=1)

# tiktok_data.drop(tiktok_data.loc[tiktok_data.index == 'goodsfeatures'].index)
# print(tiktok_data.columns)

# todo df中新增数据列
for lab in labels:
    allTWData.insert(allTWData.shape[1], lab, '0')
    # t.insert(t.shape[1], lab, '0')  # todo change

for index, row in enumerate(allTWData.itertuples()):
    # for index, row in enumerate(t.itertuples()):  # todo change
    value = getattr(row, '整理去重得到商品标签')
    gid = str(getattr(row, 'sale_id')).split('.')[0]
    if gid == '1001941328':
        a = 10
    if value:
        tmpDict = {}
        tags = value.split('|')
        for tag in tags:
            tagCls = tag.split('-')[0]
            tagVal = tag.split('-')[1]
            if tagCls not in tmpDict:
                tmpDict[tagCls] = set()
            tmpDict[tagCls].add(tagVal)

        # todo df修改值
        for k, v in tmpDict.items():
            strTagVal = ' '.join(v)
            d_index = list(allTWData.columns).index(k)
            allTWData.iloc[index, d_index] = strTagVal
        bre = 'continue'

allTWData.to_sql('hkGoods', engine)  # tiktok_data 是表名   using function
# t.to_sql('twGoods', engine)  # tiktok_data 是表名  todo change
# allTWData.to_sql('erp_source',con = engine ,if_exists = 'append',index="False")
a = 'break'
