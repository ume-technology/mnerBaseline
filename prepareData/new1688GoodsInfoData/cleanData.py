# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:cleanData.py
@Time:2023/2/20 9:03
@Read: 清洗Ali原始数据并清洗，进而存储
"""
import re
import json
import pickle

pattern = re.compile(r'<[^>]+>', re.S)
allAttributeName = set()


def goodsAttributes(a):
    """ 添加attribute到目标字段 """
    # newDetail = {}
    attributesSet = set()
    attributesList = ''

    detail = a['detail']
    if detail is None or not detail:
        return 0

    detail = pattern.sub('', detail)
    detail = re.sub('\r', '', detail)
    detail = re.sub('\n', '', detail)
    detail = re.sub('\s+', '', detail)
    # detail = re.sub('\xa0', '', detail)
    detail = detail.replace('&nbsp;', '')
    detail = detail.replace('&mdash;', '')
    detail = detail.replace('&yen;', '')
    # print(type(detail))
    # print(detail)
    try:
        detail = json.loads(detail, strict=False)
    except:
        return 0
    productInfo = detail['productInfo']  # all detail
    attributes = productInfo['attributes']
    for i in attributes:
        attributeName = i['attributeName']
        allAttributeName.add(attributeName)
        attributeValue = i['value']
        attributesSet.add(attributeName + '#' + attributeValue)  # 属性k#v

    attributesList = list(attributesSet)
    attributesList = "-".join(attributesList)  # k#v-k#v-k#v
    description = productInfo['description'].strip()
    attributesList = attributesList + "|" + description  # k#v-k#v-k#v | description
    categoryName = productInfo['categoryName'].strip()
    attributesList = attributesList + "|" + categoryName  # k#v-k#v-k#v | description | categoryName
    return attributesList
    # ============
    # subject = productInfo['subject'].strip()
    # newDetail['attributes'] = attributes
    # newDetail['subject'] = subject
    # newDetail['categoryName'] = categoryName
    # newDetail['description'] = description
    # return newDetail


with open('../../bigfiles/new1688GoodsInfoDataSave/ali_tags_dw.pick', 'rb') as f:
    data = pickle.load(f)
    data.loc[:, 'goodsAttributes'] = data.apply(goodsAttributes, axis=1)
    data = data.drop(columns=['detail'])

    # todo 添加目标字段
    # for i in allAttributeName:
    #     data.insert(data.shape[1], i, 0)
    # for index, row in enumerate(data.intertuples()):
    #     value = getattr(row, 'goodsAttributes')

    with open('../../bigfiles/new1688GoodsInfoDataSave/clean_ali_tags_dw.pick', 'wb') as f:
        pickle.dump(data, f)
