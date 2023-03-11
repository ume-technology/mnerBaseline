# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:ad_material_data_clean_2ner.py
@Time:2022/12/9 10:53
@Read: todo 清洗并生成单纯地可以用来做NER标注的数据; 这个脚本只用来做NER数据标注文件的生成
"""
import os
import re
import pickle
import random
import logging
from zhconv import convert

random.seed(2022)
# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
# logger = logging.getLogger(__name__)

s = "\n\r\t@#$%^&*这样一本书大卖，有点意外，据说已经印了四五十万，排行榜仅次于《希拉里自传》。推荐倒着看。\n\s\r\t"
patternnochn = re.compile(u'[^\u4e00-\u9fa5]')  # 匹配非中文
utl_pat_1 = re.compile(r'\<http.+?\>', re.DOTALL)  # 去除URL
utl_pat_2 = re.compile(r'\<https.+?\>', re.DOTALL)  # 去除URL
jap = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7A3]')  # 去除日文行
patt = '^[a-zA-Z0-9’!"$%&\'()*+,./:;<=>?@，。?、…【】《》？“”‘’！[\\]^_`{|}\s]+'  # 去除特殊字符
patchnend = '[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]'  # 匹配中文和中文标点符号
t = re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]', s)


# print(''.join(t))

def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True


# todo clean data for NER
def readMaterialGiikinADDataCHN():
    clean_text = []
    # todo 读取的这部分数据是material表的中文线路的原始数据
    with open('../bigfiles/newCorrectGiikinGoodsDataSave/台湾', 'rb') as f:
        mate_data = pickle.load(f)
        for i in mate_data.itertuples():
            sale_name = getattr(i, 'sale_name')
            if sale_name is None:
                sale_name = getattr(i, 'product_name')
            if sale_name is None:
                continue
            sale_name = convert(sale_name, 'zh-cn')
            sale_name = re.sub(utl_pat_1, '', sale_name)
            sale_name = re.sub(utl_pat_2, '', sale_name)
            sale_name = re.sub(jap, '', sale_name)
            sale_name = re.sub(patt, '', sale_name)
            sale_name = re.findall(patchnend, sale_name)
            sale_name = ''.join(sale_name)

            ad_slogans = getattr(i, 'ad_slogans')
            if ad_slogans is None:
                continue
            ad_slogans = convert(ad_slogans, 'zh-cn')
            ad_slogans = re.sub(utl_pat_1, '', ad_slogans)
            ad_slogans = re.sub(utl_pat_2, '', ad_slogans)
            ad_slogans = re.sub(jap, '', ad_slogans)
            ad_slogans = re.sub(patt, '', ad_slogans)
            ad_slogans = re.findall(patchnend, ad_slogans)
            ad_slogans = ''.join(ad_slogans)

            interest_words = getattr(i, 'interest_words')
            if interest_words is None:
                clean_text.append(sale_name + '。' + ad_slogans)
                continue
            else:
                interest_words = convert(interest_words, 'zh-cn')
                interest_words = re.sub(utl_pat_1, '', interest_words)
                interest_words = re.sub(utl_pat_2, '', interest_words)
                interest_words = re.sub(jap, '', interest_words)
                interest_words = re.sub(patt, '', interest_words)
                interest_words = re.findall(patchnend, interest_words)
                interest_words = ''.join(interest_words)

                clean_text.append(sale_name + '。' + ad_slogans + '。' + interest_words)
    return clean_text


# def readMaterialGiikinADDataCHN():
#     clean_text = []
#     # todo 读取的这部分数据是material表的中文线路的原始数据
#     with open('../bigfiles/newCorrectGiikinGoodsDataSave/台湾', 'rb') as f:
#         mate_data = pickle.load(f)
#         for i in mate_data.itertuples():
#             sale_name = getattr(i, 'sale_name')
#             if sale_name is None:
#                 sale_name = getattr(i, 'product_name')
#             if sale_name is None:
#                 continue
#             sale_name = convert(sale_name, 'zh-cn')
#             sale_name = re.sub(utl_pat_1, '', sale_name)
#             sale_name = re.sub(utl_pat_2, '', sale_name)
#             sale_name = re.sub(jap, '', sale_name)
#             sale_name = re.sub(patt, '', sale_name)
#             sale_name = re.findall(patchnend, sale_name)
#             sale_name = ''.join(sale_name)
#
#             ad_slogans = getattr(i, 'ad_slogans')
#             if ad_slogans is None:
#                 continue
#             ad_slogans = convert(ad_slogans, 'zh-cn')
#             ad_slogans = re.sub(utl_pat_1, '', ad_slogans)
#             ad_slogans = re.sub(utl_pat_2, '', ad_slogans)
#             ad_slogans = re.sub(jap, '', ad_slogans)
#             ad_slogans = re.sub(patt, '', ad_slogans)
#             ad_slogans = re.findall(patchnend, ad_slogans)
#             ad_slogans = ''.join(ad_slogans)
#
#             interest_words = getattr(i, 'interest_words')
#             if interest_words is None:
#                 clean_text.append(sale_name + '。' + ad_slogans)
#                 continue
#             else:
#                 interest_words = convert(interest_words, 'zh-cn')
#                 interest_words = re.sub(utl_pat_1, '', interest_words)
#                 interest_words = re.sub(utl_pat_2, '', interest_words)
#                 interest_words = re.sub(jap, '', interest_words)
#                 interest_words = re.sub(patt, '', interest_words)
#                 interest_words = re.findall(patchnend, interest_words)
#                 interest_words = ''.join(interest_words)
#
#             clean_text.append(sale_name + '。' + ad_slogans + '。' + interest_words)
#     return clean_text


# todo 借助AliData处理其他线路的商品特征数据
def tempCleanProName(i):
    # todo giikin product name
    giikinProName = getattr(i, 'product_name')
    giikinProName = convert(giikinProName, 'zh-cn')
    cut_idx = 0
    for idx, _ in enumerate(giikinProName):
        if is_all_chinese(_):
            cut_idx = idx
            break
    giikinProName = giikinProName[cut_idx:]
    giikinProName = re.sub(' ', '', giikinProName)

    # todo ali product name
    aliProName = getattr(i, 'ali_product_name')
    if not isinstance(aliProName, str):
        return giikinProName
    else:
        aliProName = convert(aliProName, 'zh-cn')
        aliProName = re.sub(' ', '', aliProName)

    return giikinProName + '。' + aliProName


basePath = '../bigfiles/newConcatAliWithgiikinGoodsData'
lists = ['feilvbin.pick', 'hanguo.pick', 'riben.pick', 'taiwan.pick']
clean_text = []
for i in lists:
    path = os.path.join(basePath, i)
    with open(path, 'rb') as f:
        data = pickle.load(f)
        # 因为中文有可以处理的广告语,因此多了一个广告语的处理
        if i == 'taiwan.pick':
            for i in data.itertuples():
                text = tempCleanProName(i)
                ad_slogans = getattr(i, 'ad_slogans')
                if ad_slogans is None:
                    clean_text.append(text)
                else:
                    ad_slogans = convert(ad_slogans, 'zh-cn')
                    ad_slogans = re.sub(utl_pat_1, '', ad_slogans)
                    ad_slogans = re.sub(utl_pat_2, '', ad_slogans)
                    ad_slogans = re.sub(jap, '', ad_slogans)
                    ad_slogans = re.sub(patt, '', ad_slogans)
                    ad_slogans = re.sub(' ', '', ad_slogans)
                    ad_slogans = re.findall(patchnend, ad_slogans)
                    ad_slogans = ''.join(ad_slogans)
                    text = text + '。' + ad_slogans
                    clean_text.append(text)
        # 其他线路的品就只处理 giikin和ali的 pro name
        else:
            for i in data.itertuples():
                text = tempCleanProName(i)
                clean_text.append(text)

for idx, i in enumerate(clean_text):
    with open('../processData/tagdata2ner_20230301/taged_data/newTags.txt', 'a+', encoding='utf-8') as f:
        for cha in i:
            f.write(cha + ' \n')
        f.write('\n')
