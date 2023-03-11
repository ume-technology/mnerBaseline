# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:translate_and_cleanadmaterial.py
@Time:2023/2/1 15:42
@Read: 翻译文本同时清洗从 readalldata_new.py 中读取的源数据；
"""
import pickle
import re
import pickle
import json
import pandas as pd
import requests
# import langid
from zhconv import convert


def cleantext(i, line_name, from_):
    utl_pat_1 = re.compile(r'\<http.+?\>', re.DOTALL)  # 去除URL
    utl_pat_2 = re.compile(r'\<https.+?\>', re.DOTALL)  # 去除URL
    jap = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7A3]')  # 去除日文行
    product_name_patt = '^[a-zA-Z0-9’!"$%&\'()*+,./:;<=>?@，。?、…【】《》？“”‘’！[\\]^_`{|}\s]+'  # 去除特殊字符 - 需要去除数据头部的英文和数据标识符
    ad_slogans_patt = '^[’!"$%&\'()*+,./:;<=>?@，。?、…【】《》？“”‘’！[\\]^_`{|}\s]+'  # 去除特殊字符;保留必要的数字和英文
    pattern = re.compile(u'[^\u4e00-\u9fa5]')  # 匹配非中文
    # patchnend = '[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]'  # 匹配中文和中文标点符号
    patchnendwith_math = '[0-9\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]'  # 匹配中文和中文标点符号和数字

    # todo demo 直接匹配中文和中文标点符号
    # res = ''.join(re.findall(
    #     '[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]',
    #     "\n\r\t@#$%^&*这样一本书大卖，有点意外，据说已经印了四五十万，排行榜仅次于《希拉里自传》。推荐倒着看。\n\s\r\t")
    # )

    sale_name_ = None
    sale_name = i['product_name']  # 直接用这个，会少很多翻译工作
    if sale_name is None:
        sale_name_ = i['sale_name']  # sale_name_  是需要翻译的
    if sale_name is None and sale_name_ is None:
        return
    if not isinstance(sale_name, str):
        return
    if sale_name:  # 不需要翻译
        if '-' in sale_name:  # 直接去除product_name的标识符，只保留真正的product_name
            sale_name = sale_name.split('-')[1]
    if sale_name_:  # 需要翻译
        if from_ != 'zh':  # 需要翻译
            data = {"from": from_, "to": "zh", "text": sale_name_}
            try:
                res = requests.post(url='https://gassapi.giikin.cn/fspider/baidu/translate', data=data).json()
                if res['code'] == 0:
                    sale_name = res['data']['trans_result']  # 最后统一到sale_name变量名
                else:
                    # logging   请求超时的情况
                    pass
                    # return  # todo change 这里为了测试程序注释掉；正式上线的时候，这里应该放开，因为这里意味着商品的素材数据是不完整的，不需要再继续执行这条商品数据；
            except:
                # logging   res解析错误的情况
                pass
                # return  # todo change 这里为了测试程序注释掉；正式上线的时候，这里应该放开，因为这里意味着商品的素材数据是不完整的，不需要再继续执行这条商品数据；
        else:
            pass
    # sale_name = '我爱北京天安门'
    sale_name = convert(sale_name, 'zh-cn')
    sale_name = re.sub(utl_pat_1, '', sale_name)
    sale_name = re.sub(utl_pat_2, '', sale_name)
    sale_name = re.findall(patchnendwith_math, sale_name)
    sale_name = ''.join(sale_name)

    ad_slogans = i['ad_slogans']  # ad_slogans
    if ad_slogans is None:
        return
    if from_ != 'zh':  # 需要翻译
        data = {"from": from_, "to": "zh", "text": ad_slogans}
        try:
            res = requests.post(url='https://gassapi.giikin.cn/fspider/baidu/translate', json=data).text
            res = json.loads(res)
            if res['code'] == 0:
                ad_slogans = res['data']['trans_result']  # 最后统一到sale_name变量名
            else:
                # logging：请求超时的情况
                pass
                # return  # todo change 这里为了测试程序注释掉；正式上线的时候，这里应该放开，因为这里意味着商品的素材数据是不完整的，不需要再继续执行这条商品数据；
        except:
            # logging：res解析错误的情况
            pass
            # return  # todo change 这里为了测试程序注释掉；正式上线的时候，这里应该放开，因为这里意味着商品的素材数据是不完整的，不需要再继续执行这条商品数据；
    else:
        pass
    ad_slogans = convert(ad_slogans, 'zh-cn')
    ad_slogans = re.sub(utl_pat_1, '', ad_slogans)
    ad_slogans = re.sub(utl_pat_2, '', ad_slogans)
    # sale_name = re.sub(ad_slogans_patt, '', sale_name)
    ad_slogans = re.findall(patchnendwith_math, ad_slogans)
    ad_slogans = ''.join(ad_slogans)

    interest_words = getattr(i, 'interest_words')
    if interest_words is None:
        cleantext = sale_name + '。' + ad_slogans
        return cleantext
    if from_ != 'zh':  # 需要翻译
        data = {"from": from_, "to": "zh", "text": interest_words}
        try:
            res = requests.post(url='https://gassapi.giikin.cn/fspider/baidu/translate', json=data).text
            res = json.loads(res)
            if res['code'] == 0:
                interest_words = res['data']['trans_result']  # 最后统一到sale_name变量名
            else:
                # logging：请求超时的情况
                pass
                # return  # todo change 这里为了测试程序注释掉；正式上线的时候，这里应该放开，因为这里意味着商品的素材数据是不完整的，不需要再继续执行这条商品数据；
        except:
            # logging：res解析错误的情况
            pass
            # return  # todo change 这里为了测试程序注释掉；正式上线的时候，这里应该放开，因为这里意味着商品的素材数据是不完整的，不需要再继续执行这条商品数据；
    else:
        pass
    interest_words = convert(interest_words, 'zh-cn')
    interest_words = re.sub(utl_pat_1, '', interest_words)
    interest_words = re.sub(utl_pat_2, '', interest_words)
    # interest_words = re.sub(ad_slogans_patt, '', interest_words)  # patchnendwith_math过滤文本就不需要该方案了
    interest_words = re.findall(patchnendwith_math, interest_words)  # 可能存在全英文的情况；最好是等待翻译后的标准数据再处理
    if interest_words:
        interest_words = ''.join(interest_words)
        cleantext = sale_name + '。' + ad_slogans + '。' + interest_words
        return cleantext
    else:
        cleantext = sale_name + '。' + ad_slogans + '。'
        return cleantext


# pass 中国；摩洛哥；澳大利亚；美国；越南；
line_name_lang = {'匈牙利': 'hu', '卡塔尔': 'qa', '香港': 'zh', '台湾': 'zh',
                  '新加坡': 'en', '日本': 'jp', '沙特阿拉伯': 'sa', '波兰': 'pl', '泰国': 'th', '科威特': 'kw',
                  '罗马尼亚': 'ro', '菲律宾': 'en', '阿曼苏丹国': 'unknown', '阿联酋': 'unknown', '韩国': 'kr', '马来西亚': 'my'}

if __name__ == '__main__':
    for k, v in line_name_lang.items():
        if v != 'zh':
            continue
        with open(k, 'rb') as f:  # todo 这里的路径需要修改为 bigfiles/newCorrectGiikinGoodsDataSave路径
            data = pickle.load(f)
            data_ = data.head(1000)
            res = data_.dropna(subset=['product_name'])  #
            # todo data clean: DF的apply方法，在指定axis=1的情况下，已经完成了内部迭代，把整个DF都遍历一遍后再返回结果
            res.loc[:, 'cleantext'] = res.apply(cleantext, axis=1, line_name=k, from_=v)
            end = 'ending'
    pass
