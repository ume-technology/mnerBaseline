# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@Blog: https://www.umeai.top/
@File:modelApi.py
@Time:2023/2/21 16:22
@ReadMe: 
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
import flask
from flask import Flask
from flask import Flask, jsonify, request

app = Flask(__name__)

MID_DATA_DIR = "../processData/tagdata2ner_new/mid_data_new"
RAW_DATA_DIR = "../processData/tagdata2ner_new/raw_data_new"
# SUBMIT_DIR = "./result"
GPU_IDS = "-1"
LAMBDA = 0.3
THRESHOLD = 0.9
MAX_SEQ_LEN = 512
TASK_TYPE = "crf"
VOTE = False

# BERT_DIR = r'F:\PreModels\hflchinese-roberta-wwm-ext'  # todo change windows
BERT_DIR = '/home/fzm/premodelfiles/hflchinese-roberta-wwm-ext'  # todo change linux

# todo change windows
# CKPT_PATH = \
#     r'E:\g-core-mytcner\bigfiles\nerCodeBaseLineOutput\giikin_alltageddata_new\roberta_wwm_crf\checkpoint-1236\model.pt'
# todo change linux
CKPT_PATH = '/home/fzm/mnerBaseline/bigfiles/nerCodeBaseLineOutput/giikin_alltageddata_new/roberta_wwm_crf/checkpoint-1236/model.pt'
CKPT_PATH = '/home/fzm/mnerBaseline/bigfiles/nerCodeBaseLineOutput/giikin_allatgeddata_20230301/roberta_wwm_crf/checkpoint-1236/model.pt'

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


@app.route('/goodsInfo', methods=['GET'])
def mypredict():
    goodsId = request.args.get('goodsId')
    goodsTitle = request.args.get('goodsTitle')

    # todo
    # re goodsTitle

    info_dict = {}
    examples = [{'id': int(goodsId), 'text': goodsTitle}]
    info_dict['id2ent'] = id2ent
    info_dict['tokenizer'] = tokenizer
    info_dict['examples'] = examples

    labels = base_predict(model, device, info_dict)
    print("return labels: ", labels)

    # todo save to mysql
    pass

    print('---' * 50)

    return labels


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', debug=True, port=5003)
    # app.run(host='127.0.0.1', debug=True, port=5000)
    # app.run(debug=False, port=5000)
