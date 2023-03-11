# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:predict.py
@Time:2022/12/9 12:27
@Read: 
"""
# windows
import os
import torch
import math
from collections import defaultdict
from transformers import BertTokenizer
from nercode.src.model_utils import CRFModel
from nercode.src.evaluator import crf_decode, span_decode
from nercode.src.functions_utils import load_model_and_parallel
from nercode.src.processor import cut_sent, fine_grade_tokenize
from prepareData.newCorrectGiikinGoodsData.translate_and_cleanadmaterial import *

# linux
# import pickle
# import os
# import json
# import torch
# import math
# from collections import defaultdict
# from transformers import BertTokenizer
# from .src.model_utils import CRFModel, SpanModel, EnsembleCRFModel, EnsembleSpanModel
# from .src.evaluator import crf_decode, span_decode
# from .src.functions_utils import load_model_and_parallel, ensemble_vote
# from .src.processor import cut_sent, fine_grade_tokenize


MID_DATA_DIR = "../processData/tagdata2ner_new/mid_data_new"
RAW_DATA_DIR = "../processData/tagdata2ner_new/raw_data_new"
SUBMIT_DIR = "./result"
GPU_IDS = "-1"
LAMBDA = 0.3
THRESHOLD = 0.9
MAX_SEQ_LEN = 512
TASK_TYPE = "crf"
VOTE = False

# todo change windows
BERT_DIR = r'F:\PreModels\hflchinese-roberta-wwm-ext'
# todo linux
# BERT_DIR = '/mnt/f/Pictures/premodelfiles/hflchinese-roberta-wwm-ext'
# todo change windows
CKPT_PATH = \
    r'E:\g-core-mytcner\bigfiles\nerCodeBaseLineOutput\giikin_alltageddata_new\roberta_wwm_crf\checkpoint-1236\model.pt'
# todo change linux
# CKPT_PATH = '../outputs/giikin_alltageddata_new/roberta_wwm_crf/checkpoint-1236/model.pt'

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
    # eachtextlabels = {}
    print("return labels: ", labels)
    return labels


base_path = '../datagiikin/bigfiles_new'
# todo important lines_name with platform 划分
for k, v in line_name_lang.items():  # line lang
    if v != 'zh':
        continue
    goods_path = os.path.join(base_path, k)
    with open(goods_path, 'rb') as f:  # 这里已经是具体的线路数据： good_data_in_tar_line
        goodsdata = pickle.load(f)
        print('*' * 50, " : ", goodsdata.shape)

    plat_names = goodsdata.groupby(goodsdata.platfrom).groups
    plats = [i for i in plat_names]

    line_dir = '../outputs/giikin_alltageddata_new'
    target_line_platform_path = os.path.join(line_dir, k)
    if not os.path.exists(target_line_platform_path):
        os.makedirs(target_line_platform_path)
    for each_plat in plats:
        file_name = each_plat + '.pick'
        file_path = os.path.join(target_line_platform_path, file_name)
        goods_with_plat_base_line = goodsdata.loc[goodsdata['platfrom'] == each_plat]
        goods_with_plat_base_line.loc[:, 'cleantext'] = goods_with_plat_base_line.apply(cleantext, axis=1, line_name=k,
                                                                                        from_=v)
        goods_with_plat_base_line.loc[:, 'goodsfeatures'] = goods_with_plat_base_line.apply(mypredict, axis=1)
        with open(file_path, 'wb') as f:
            pickle.dump(goods_with_plat_base_line, f)
        print('---' * 50)

    # todo wait designer
    # designers_list = goodsdata.groupby(goodsdata.designer_id).groups
    # designers = [i for i in designers_list]
    # # todo wait teams
    # team_names = goodsdata.groupby(goodsdata.team_name).groups
    # teams = [i for i in team_names]
    # for key, lineIndex in team_names.items():
    #     goods_with_team_base_line = goodsdata.loc[lineIndex]
