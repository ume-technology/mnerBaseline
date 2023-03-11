# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:splitnewnertagdata.py
@Time:2022/12/13 22:43
@Read: 切分新的NER待标注数据; 完成标注后书移动到 alltageddata文件夹中
"""
import pickle

with open('datagiikin/bigfiles/ad_material_data_clean_2ner_clean_with_interest_words.pick', 'rb') as f:
    oricleandata = pickle.load(f)

# 新标注方案下的数据存储路径
# todo  截至20221222；划分的是1000条数据进行标注
with open('tagdata2ner_new/taged_data/waittotagdata.txt', 'w+', encoding='utf-8') as f:
    for i in oricleandata[:1000]:
        for _ in list(i):
            f.write(_ + '\t\n')
        f.write('\n')

# 老标注方案下的数据存储路径
pass
