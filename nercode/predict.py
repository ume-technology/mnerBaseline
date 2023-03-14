# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:predict.py
@Time:2022/12/9 12:27
@Read: 
"""
# windows
import re
import os
import torch
import math
import numpy as np
import pandas as pd
from collections import defaultdict
from transformers import BertTokenizer
from nercode.src.model_utils import CRFModel
from nercode.src.evaluator import crf_decode, span_decode
from nercode.src.functions_utils import load_model_and_parallel
from nercode.src.processor import cut_sent, fine_grade_tokenize
from prepareData.newCorrectGiikinGoodsData.translate_and_cleanadmaterial import *

# todo version ner model - 1
MID_DATA_DIR = "../processData/tagdata2ner_new/mid_data_new"
RAW_DATA_DIR = "../processData/tagdata2ner_new/raw_data_new"
# todo change windows
# CKPT_PATH = r'F:\mnerBaseline\bigfiles\nerCodeBaseLineOutput\giikin_alltageddata_new\roberta_wwm_crf\checkpoint-1236\model.pt'
# todo change linux
CKPT_PATH = '../bigfiles/nerCodeBaseLineOutput/giikin_allatgeddata_20230301/roberta_wwm_crf/checkpoint-4598/model.pt'

# todo version ner model - 2
MID_DATA_DIR = "../processData/tagdata2ner_20230301/mid_data"
RAW_DATA_DIR = "../processData/tagdata2ner_20230301/raw_data"
# todo change windows
CKPT_PATH = r'F:\mnerBaseline\bigfiles\nerCodeBaseLineOutput\giikin_allatgeddata_20230301\roberta_wwm_crf\checkpoint-4598\model.pt'
# todo change linux
CKPT_PATH = '../bigfiles/nerCodeBaseLineOutput/giikin_allatgeddata_20230301/roberta_wwm_crf/checkpoint-4598/model.pt'

SUBMIT_DIR = "./result"
GPU_IDS = "0"
LAMBDA = 0.3
THRESHOLD = 0.9
MAX_SEQ_LEN = 512
TASK_TYPE = "crf"
VOTE = False

# BERT_DIR = r'F:\mprtModel\hflchinese-roberta-wwm-ext'  # todo change windows
BERT_DIR = '/mnt/f/mprtModel/hflchinese-roberta-wwm-ext'  # todo linux

with open(os.path.join(MID_DATA_DIR, f'{TASK_TYPE}_ent2id.json'), encoding='utf-8') as f:
    ent2id = json.load(f)
id2ent = {ent2id[key]: key for key in ent2id.keys()}

tokenizer = BertTokenizer(os.path.join(BERT_DIR, 'vocab.txt'))
model = CRFModel(bert_dir=BERT_DIR, num_tags=len(id2ent))
model, device = load_model_and_parallel(model, GPU_IDS, CKPT_PATH)
print('here is model info linux')
print(device)
print('*' * 50)
model.eval()

s = "\n\r\t@#$%^&*这样一本书大卖，有点意外，据说已经印了四五十万，排行榜仅次于《希拉里自传》。推荐倒着看。\n\s\r\t"
t = re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]', s)
patternnochn = re.compile(u'[^\u4e00-\u9fa5]')  # 匹配非中文
patchnend = '[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]'  # 匹配中文和中文标点符号
utl_pat_1 = re.compile(r'\<http.+?\>', re.DOTALL)  # 去除URL
utl_pat_2 = re.compile(r'\<https.+?\>', re.DOTALL)  # 去除URL
jap = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7A3]')  # 去除日文行
# patt = '^[!"$%&\'()*+,./:;<=>?@，。?、…【】《》？“”‘’！[\\]^_`{|}\s]+'  # 去除特殊字符
patt = '^[a-zA-Z0-9’!"$%&\'()*+,./:;<=>?@，。?、…【】《》？“”‘’、！[\\]^_`{|}\s]+'  # 去除特殊字符


def base_predict(model, device, info_dict, ensemble=False, mixed=''):
    labels = defaultdict(list)
    tokenizer = info_dict['tokenizer']
    id2ent = info_dict['id2ent']
    with torch.no_grad():
        for _ex in info_dict['examples']:
            ex_idx = _ex['id']
            raw_text = _ex['text']
            if raw_text is None:
                continue
            if not len(raw_text):
                labels[ex_idx] = []
                print('{}为空'.format(ex_idx))
                continue
            sentences = cut_sent(raw_text, MAX_SEQ_LEN)
            start_index = 0
            for sent in sentences:
                sent_tokens = fine_grade_tokenize(sent, tokenizer)
                encode_dict = tokenizer.encode_plus(text=sent_tokens, max_length=MAX_SEQ_LEN, is_pretokenized=True,
                                                    pad_to_max_length=False, return_tensors='pt',
                                                    return_token_type_ids=True, return_attention_mask=True)
                model_inputs = {'token_ids': encode_dict['input_ids'], 'attention_masks': encode_dict['attention_mask'],
                                'token_type_ids': encode_dict['token_type_ids']}
                for key in model_inputs:
                    model_inputs[key] = model_inputs[key].to(device)
                if ensemble:
                    if TASK_TYPE == 'crf':
                        if VOTE:
                            decode_entities = model.vote_entities(model_inputs, sent, id2ent, THRESHOLD)
                        else:
                            pred_tokens = model.predict(model_inputs)[0]
                            decode_entities = crf_decode(pred_tokens, sent, id2ent)
                    else:
                        if VOTE:
                            decode_entities = model.vote_entities(model_inputs, sent, id2ent, THRESHOLD)
                        else:
                            start_logits, end_logits = model.predict(model_inputs)
                            start_logits = start_logits[0].cpu().numpy()[1:1 + len(sent)]
                            end_logits = end_logits[0].cpu().numpy()[1:1 + len(sent)]
                            decode_entities = span_decode(start_logits, end_logits, sent, id2ent)
                else:
                    if mixed:
                        if mixed == 'crf':
                            pred_tokens = model(**model_inputs)[0][0]
                            decode_entities = crf_decode(pred_tokens, sent, id2ent)
                        else:
                            start_logits, end_logits = model(**model_inputs)
                            start_logits = start_logits[0].cpu().numpy()[1:1 + len(sent)]
                            end_logits = end_logits[0].cpu().numpy()[1:1 + len(sent)]
                            decode_entities = span_decode(start_logits, end_logits, sent, id2ent)
                    else:
                        if TASK_TYPE == 'crf':
                            pred_tokens = model(**model_inputs)[0][0]
                            decode_entities = crf_decode(pred_tokens, sent, id2ent)
                        else:
                            start_logits, end_logits = model(**model_inputs)
                            start_logits = start_logits[0].cpu().numpy()[1:1 + len(sent)]
                            end_logits = end_logits[0].cpu().numpy()[1:1 + len(sent)]
                            decode_entities = span_decode(start_logits, end_logits, sent, id2ent)
                for _ent_type in decode_entities:
                    for _ent in decode_entities[_ent_type]:
                        tmp_start = _ent[1] + start_index
                        tmp_end = tmp_start + len(_ent[0])
                        assert raw_text[tmp_start: tmp_end] == _ent[0]
                        labels[ex_idx].append((_ent_type, tmp_start, tmp_end, _ent[0]))
                start_index += len(sent)
                if not len(labels[ex_idx]):
                    labels[ex_idx] = []
    return labels[ex_idx]


# todo 情形一的预测方法 任务不指定
def mypredictTest(i):
    info_dict = {}
    cleantext_ = getattr(i, 'sizeChart')
    examples = [{'id': int(0), 'text': cleantext_}]
    info_dict['id2ent'] = id2ent
    info_dict['tokenizer'] = tokenizer
    info_dict['examples'] = examples

    labels = base_predict(model, device, info_dict)
    labelsDict = dict()
    for _ in labels:
        tagKey = _[0]
        if tagKey == 'prt商品':
            continue
        tagValue = _[-1]
        if tagKey not in labelsDict.keys():
            labelsDict[tagKey] = set()
        labelsDict[tagKey].add(tagValue)
    print("return labels: ", labelsDict)
    return labelsDict


# todo 情形一：测试新模型时会用到的一些数据清洗方法
def cleantext_(i):
    # sizeChart = getattr(i,'size_chart')
    sale_name = i['size_chart']  # sale_name
    if sale_name is None:
        pass
    if sale_name is None:
        pass
    if not isinstance(sale_name, str):
        pass
    sale_name = convert(sale_name, 'zh-cn')
    sale_name = re.sub(utl_pat_1, '', sale_name)
    sale_name = re.sub(utl_pat_2, '', sale_name)
    sale_name = re.sub(jap, '', sale_name)
    sale_name = re.sub(patt, '', sale_name)
    sale_name = re.findall(patchnend, sale_name)
    sale_name = ''.join(sale_name)
    sizeChart = sale_name
    return sizeChart


# todo 处理三方任务时测试的数据集
# df = pd.read_csv(r'../prepareData/amazonData/amazon_product_20230228103938.csv')
# df = df.dropna(subset=['product_detail', 'size_chart'])
# df.loc[:, 'sizeChart'] = df.apply(cleantext_, axis=1)
# df.drop(columns=['size_chart', 'product_link'], inplace=True)
# df.loc[:, 'goodsfeatures'] = df.apply(mypredictTest, axis=1)


# todo 情形二的预测方法 predict giikin goodsd
def mypredict(goodsdata):
    info_dict = {}
    sale_id = goodsdata['sale_id']
    cleantext = goodsdata['cleantext']
    if math.isnan(sale_id):
        sale_id = 0
    examples = [{'id': int(sale_id), 'text': cleantext}]
    info_dict['id2ent'] = id2ent
    info_dict['tokenizer'] = tokenizer
    info_dict['examples'] = examples

    labels = base_predict(model, device, info_dict)
    labelsDict = dict()
    for _ in labels:
        tagKey = _[0]
        if tagKey == 'prt商品':
            continue
        tagValue = _[-1]
        if tagKey not in labelsDict.keys():
            labelsDict[tagKey] = set()
        labelsDict[tagKey].add(tagValue)
    print("return labels: ", labelsDict)
    return labelsDict


# todo 情形二： 不是情形二时，下面的方法应该取消下面的步骤：giikin Goods Handler

def cleanTextNoCHN(i, axis=1, line_name='', from_=''):
    proName = i['product_name']
    aliName = i['ali_product_name']
    if pd.isnull(aliName):
        sale_name = proName
    else:
        sale_name = proName + '。' + aliName
    sale_name = convert(sale_name, 'zh-cn')
    sale_name = re.sub(utl_pat_1, '', sale_name)
    sale_name = re.sub(utl_pat_2, '', sale_name)
    sale_name = re.sub(jap, '', sale_name)
    sale_name = re.sub(patt, '', sale_name)
    sale_name = re.findall(patchnend, sale_name)
    sale_name = ''.join(sale_name)
    return sale_name


# todo =========================== read Ali and Giikin Goods and concat and do predict

def readAli():
    # todo read ali clean data info
    with open('../bigfiles/new1688GoodsInfoDataSave/clean_ali_tags_dw.pick', 'rb') as f:
        cleanAliGoodsData = pickle.load(f)
        cleanAliGoodsData = cleanAliGoodsData.rename(columns={'product_name': 'ali_product_name'})  # todo 重命名
    return cleanAliGoodsData


def concatGiikinAliGoods(giikinGoods, aliGoods):
    giikinGoods['sale_id'] = giikinGoods['sale_id'].astype('Int64')
    giikinGoods['product_id'] = giikinGoods['product_id'].astype('Int64')
    contextData = giikinGoods.set_index('product_id').join(aliGoods.set_index('product_id'))
    contextData.dropna(axis=0, subset=['product_name'], inplace=True)
    contextData = contextData[~contextData['product_name'].isin(['新增产品', '商城3.0爬虫产品'])]
    # columns = contextData.columns
    contextData.drop(columns=['people_cover_cnt', 'campaign_id', 'ad_group_id', 'impressions_cnt', 'clicks_cnt',
                              'add_cart_cnt', 'checkout_cnt', 'order_cnt', 'conversions_rate', '近15天广告成本', '广告成本',
                              '单次展示成本', '单次点击成本', '单次加购成本', '单次支付成本', '千次展示成本'], inplace=True)
    # samples = np.random.randint(0, len(contextData), size=100)  # todo 随机筛选一些线路上的融合后的数据；
    # newData = contextData.take(samples)
    return contextData


# todo read ali data info
cleanAliGoodsData = readAli()
# todo important lines_name with platform 划分
# pass 中国；摩洛哥；澳大利亚；美国；越南；
line_name_lang = {'匈牙利': 'hu', '卡塔尔': 'qa', '香港': 'zh', '台湾': 'zh',
                  '新加坡': 'en', '沙特阿拉伯': 'sa', '波兰': 'pl', '泰国': 'th', '科威特': 'kw',
                  '日本0-2000000': 'jp', '日本2000000-4000000': 'jp', '日本4000000-6000000': 'jp', '日本6000000-LAST': 'jp',
                  '罗马尼亚': 'ro', '菲律宾': 'en', '阿曼苏丹国': 'unknown', '阿联酋': 'unknown', '韩国': 'kr', '马来西亚': 'my'}

for k, v in line_name_lang.items():  # lineName langName
    if k in ['匈牙利', '卡塔尔', '香港']:
        continue
    base_path = '../bigfiles/newCorrectGiikinGoodsDataSave'
    goods_path = os.path.join(base_path, k)
    with open(goods_path, 'rb') as f:  # todo 这里已经读取具体的线路数据： good_data_in_tar_line
        # goodsdata = pickle.load(f).head(200)
        goodsdata = pickle.load(f)

    contextData = concatGiikinAliGoods(goodsdata, cleanAliGoodsData)

    if v == 'zh':
        contextData.loc[:, 'cleantext'] = contextData.apply(cleantext, axis=1, line_name=k, from_=v)
    else:
        contextData.loc[:, 'cleantext'] = contextData.apply(cleanTextNoCHN, axis=1, line_name=k, from_=v)

    # predict
    contextData.loc[:, 'goodsfeatures'] = contextData.apply(mypredict, axis=1)
    # create line name
    base_path = '../bigfiles/newConcatAliWithgiikinGoodsData'
    target_line_platform_path = os.path.join(base_path, k) + '.pick'
    with open(target_line_platform_path, 'wb') as f:
        pickle.dump(contextData, f)
    print('---' * 50)

    # todo wait designer / line name / teams name
    # team_names = goodsdata.groupby(goodsdata.team_name).groups
    # teams = [i for i in team_names]
    # for key, lineIndex in team_names.items():
    #     goods_with_team_base_line = goodsdata.loc[lineIndex]

# if __name__ == '__main__':
#     pass
