# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:concat1688DataWithGiikinData.py
@Time:2023/2/25 14:17
@Read: todo 融合1688和Giikin的商品，为所有商品提供标签信息
"""
import gc
import os
import pickle
import requests
import numpy as np
from zhconv import convert
from prepareData.new1688GoodsInfoData.cleanData import *
from prepareData.newCorrectGiikinGoodsData.translate_and_cleanadmaterial import line_name_lang


def cleantext(i, line_name, from_):
    utl_pat_1 = re.compile(r'\<http.+?\>', re.DOTALL)  # 去除URL
    utl_pat_2 = re.compile(r'\<https.+?\>', re.DOTALL)  # 去除URL
    jap = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7A3]')  # 去除日文行
    product_name_patt = '^[a-zA-Z0-9’!"$%&\'()*+,./:;<=>?@，。?、…【】《》？“”‘’！[\\]^_`{|}\s]+'  # 去除特殊字符 - 需要去除数据头部的英文和数据标识符
    ad_slogans_patt = '^[’!"$%&\'()*+,./:;<=>?@，。?、…【】《》？“”‘’！[\\]^_`{|}\s]+'  # 去除特殊字符;保留必要的数字和英文
    pattern = re.compile(u'[^\u4e00-\u9fa5]')  # 匹配非中文
    patchnend = '[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]'  # 匹配中文和中文标点符号
    patchnendwith_math = '[0-9\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]'  # 匹配中文和中文标点符号和数字

    sale_name = i['product_name']
    if sale_name is None:
        return
    if not isinstance(sale_name, str):
        return
    if sale_name:  # 不需要翻译
        if '-' in sale_name:  # 直接去除product_name的标识符，只保留真正的product_name
            sale_name = sale_name.split('-')[1]
    # sale_name = '我爱北京天安门'
    sale_name = convert(sale_name, 'zh-cn')
    sale_name = re.sub(utl_pat_1, '', sale_name)
    sale_name = re.sub(utl_pat_2, '', sale_name)
    sale_name = re.findall(patchnendwith_math, sale_name)
    sale_name = ''.join(sale_name)
    return sale_name


def processGiikinGoodsData():
    """
    # todo 对Giikin商品表的原始商品数据进行初步的处理，比如这里就是把原始商品信息按照线路分开存储下来，没有做更多的额外处理
           将Giikin的商品数据按照线路进行分割并分开存储；其实这个线路的分割操作没什么很明显的意义
    """
    base_path = '../../bigfiles/newCorrectGiikinGoodsDataSave'
    for k, v in line_name_lang.items():  # line lang
        if v == 'zh':
            continue
        # wait 这里日本的线路不是日本名，需要着重处理
        # if '日本' in k:
        #     continue
        # if k in ['匈牙利', '卡塔尔', '新加坡', '沙特阿拉伯', '波兰', '泰国', '科威特', '罗马尼亚', '菲律宾', '阿曼苏丹国', '阿联酋', '韩国']:
        #     continue

        goods_path = os.path.join(base_path, k)
        with open(goods_path, 'rb') as f:  # 这里已经是具体的线路数据： good_data_in_tar_line
            goodsdata = pickle.load(f)
            print('*' * 50, " : ", goodsdata.shape)

        # columns = goodsdata.columns
        goodsdata = goodsdata.drop(
            columns=['近15天广告成本', '广告成本', '单次展示成本', '单次点击成本', '单次加购成本', '单次支付成本', '千次展示成本',
                     'people_cover_cnt', 'campaign_id', 'ad_group_id', 'impressions_cnt', 'clicks_cnt', 'add_cart_cnt', 'checkout_cnt',
                     'order_cnt', 'conversions_rate']
        )

        # todo 线路数据分平台存储
        # plat_names = goodsdata.groupby(goodsdata.platfrom).groups
        # plats = [i for i in plat_names]
        # line_dir = '../../bigfiles/newCorrectGiikinGoodsDataSave/cleanOriginalAdsData'
        # target_line_platform_path = os.path.join(line_dir, k)
        # if not os.path.exists(target_line_platform_path):
        #     os.makedirs(target_line_platform_path)
        # for each_plat in plats:
        #     file_name = each_plat + '.pick'
        #     file_path = os.path.join(target_line_platform_path, file_name)
        #     goods_with_plat_base_line = goodsdata.loc[goodsdata['platfrom'] == each_plat]
        #     goods_with_plat_base_line.loc[:, 'cleantext'] = \
        #         goods_with_plat_base_line.apply(cleantext, axis=1, line_name=k, from_=v)
        #     # goods_with_plat_base_line.loc[:, 'goodsfeatures'] = goods_with_plat_base_line.apply(mypredict, axis=1)
        #     with open(file_path, 'wb') as f:
        #         pickle.dump(goods_with_plat_base_line, f)
        #     print('---' * 50)


# todo start concat Data =================================================================================================

# todo pass giikin goods demo
# with open('../../bigfiles/newCorrectGiikinGoodsDataSave/cleanOriginalAdsData/匈牙利/facebook.pick', 'rb') as f:
#     demoData = pickle.load(f).head(10)

# todo read ali clean data info
with open('../../bigfiles/new1688GoodsInfoDataSave/clean_ali_tags_dw.pick', 'rb') as f:
    cleanAliGoodsData = pickle.load(f)

# todo 重命名
cleanAliGoodsData = cleanAliGoodsData.rename(columns={'product_name': 'ali_product_name'})


def sampleGiikinGoodsDataWithAiData():
    """ todo 拼接Giikin和1688的数据信息; 并存储在 bigfiles\newConcatAliWithgiikinGoodsData 中
        wait 目前这里只有如下的几个主要线路的数据 """
    # ===========================================
    # todo 拼接 giikin-日本 with ali goods information
    with open('../../bigfiles/newCorrectGiikinGoodsDataSave/日本0-2000000', 'rb') as f:
        japan0_200W = pickle.load(f)
        japan0_200W['sale_id'] = japan0_200W['sale_id'].astype('Int64')
        japan0_200W['product_id'] = japan0_200W['product_id'].astype('Int64')

    # name:ali name; goodsAttributes: ali attrs
    # columns = ['name', 'goodsAttributes', 'platform', 'line_name', 'sale_id', 'category_lvl1_name', 'product_name', 'interest_words']
    # contextJapan0_200W = cleanAliGoodsData.set_index('pid').join(japan0_200W.set_index('product_id'))
    contextJapan0_200W = japan0_200W.set_index('product_id').join(cleanAliGoodsData.set_index('product_id'))

    # data processing
    contextJapan0_200W.dropna(axis=0, subset=['product_name'], inplace=True)
    contextJapan0_200W = contextJapan0_200W[~contextJapan0_200W['product_name'].isin(['新增产品', '商城3.0爬虫产品'])]
    contextJapan0_200W.drop(columns=['interest_words'], inplace=True)

    samples = np.random.randint(0, len(contextJapan0_200W), size=100)
    newJapan = contextJapan0_200W.take(samples)

    # ===========================================
    # todo 拼接 giikin-Taiwan with ali goods information
    with open('../../bigfiles/newCorrectGiikinGoodsDataSave/台湾', 'rb') as f:
        twGoodsData = pickle.load(f)
        twGoodsData['sale_id'] = twGoodsData['sale_id'].astype('Int64')
        twGoodsData['product_id'] = twGoodsData['product_id'].astype('Int64')
    contextTWData = twGoodsData.set_index('product_id').join(cleanAliGoodsData.set_index('product_id'))

    contextTWData.dropna(axis=0, subset=['product_name'], inplace=True)
    contextTWData = contextTWData[~contextTWData['product_name'].isin(['新增产品', '商城3.0爬虫产品'])]
    contextTWData.drop(columns=['interest_words'], inplace=True)

    samples = np.random.randint(0, len(contextTWData), size=100)  # todo 随机筛选一些线路上的融合后的数据；
    newTW = contextTWData.take(samples)

    # ===========================================
    # todo 拼接 giikin-韩国 with ali goods information
    with open('../../bigfiles/newCorrectGiikinGoodsDataSave/韩国', 'rb') as f:
        hgGoodsData = pickle.load(f)
        hgGoodsData['sale_id'] = hgGoodsData['sale_id'].astype('Int64')
        hgGoodsData['product_id'] = hgGoodsData['product_id'].astype('Int64')
    contextHGData = hgGoodsData.set_index('product_id').join(cleanAliGoodsData.set_index('product_id'))

    contextHGData.dropna(axis=0, subset=['product_name'], inplace=True)
    contextHGData = contextHGData[~contextHGData['product_name'].isin(['新增产品', '商城3.0爬虫产品'])]
    contextHGData.drop(columns=['interest_words'], inplace=True)

    samples = np.random.randint(0, len(contextHGData), size=100)
    newHG = contextHGData.take(samples)

    # ===========================================
    # todo 拼接 giikin-菲律宾 with ali goods information
    with open('../../bigfiles/newCorrectGiikinGoodsDataSave/菲律宾', 'rb') as f:
        flbGoodsData = pickle.load(f)
        flbGoodsData['sale_id'] = flbGoodsData['sale_id'].astype('Int64')
        flbGoodsData['product_id'] = flbGoodsData['product_id'].astype('Int64')
    contextFLBData = flbGoodsData.set_index('product_id').join(cleanAliGoodsData.set_index('product_id'))

    contextFLBData.dropna(axis=0, subset=['product_name'], inplace=True)
    contextFLBData = contextFLBData[~contextFLBData['product_name'].isin(['新增产品', '商城3.0爬虫产品'])]
    contextFLBData.drop(columns=['interest_words'], inplace=True)
    samples = np.random.randint(0, len(contextFLBData), size=100)
    newFLB = contextFLBData.take(samples)

    with open('../../bigfiles/newConcatAliWithgiikinGoodsData/feilvbin.pick', 'wb') as f:
        pickle.dump(newFLB, f)
