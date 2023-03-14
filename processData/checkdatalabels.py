# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@Blog: https://www.umeai.top/
@File: checkdatalabels.py
@Time: 2022/10/21 15:36
@ReadMe: 如果完成了Train data的数据标注，在这里检测标注的标签是否有错误信息
"""
# # version = 1.0.0 除了标签过少暂时不处理的11个标签：带上 o；一共48个在处理的标签；如果不带o；一共【47】个标签 * BIES = 188个标签；
# todo bigfiles\nerCodeBaseLineOutput\giikin_alltageddata_new\roberta_wwm_crf\checkpoint-1236 使用的标签体系
standard_tags = ['prt品类', 'tim日常时间', 'tim春夏时节', 'tim秋冬时节', 'hod节日', 'sce装修制造', 'sce预防保护', 'sce购物送礼', 'sce乐业', 'sce交通出行', 'sce维修检测', 'sce保洁洗漱',
                 'sce整理搬运', 'sce御寒保暖', 'sce吃美食', 'sce户外娱乐', 'sce身体保健', 'sce运动健身', 'sce化妆美容', 'the胶皮革绒', 'the金银铜铁', 'the麻线丝棉', 'the植物原料',
                 'the高新技术', 'cro弱势群体', 'cro女性群体', 'cro男性群体', 'cro职场人群', 'cro亲友群体', 'cro居家', 'cro厨房', 'cro浴室', 'cro娱乐场所', 'cro办公学习', 'cro工具建材',
                 'cro家具设备', 'cro生命元素', 'cro有害元素', 'cro身体部位', 'mar口味', 'mar颜色', 'mar图案', 'mar高效便捷', 'mar舒适触感', 'mar风格', 'mar款式', 'mar人文宗教', 'o']
print(len(standard_tags))

# todo 20230309 新的标签不带 o 一共 59个；# version = 2.0.1
standard_tags = ['cro家具设备', 'sce睡觉休息', 'sce整理搬运', 'mar舒适触感', 'cro办公学习', 'sce运动健身', 'mar图案', 'sce身体保健', 'sce乐业', 'cro弱势群体', 'sce工作学习',
                 'cro娱乐场所', 'cro肥胖群体', 'the高新技术', 'cro有害元素', 'mar款式', 'sce交通出行', 'sce吃美食', 'cro懒人群体', 'sce预防保护', 'sce购物送礼', 'sce保洁洗漱',
                 'cro美容产品', 'mar性状', 'prt商品', 'mar高效便捷', 'tim秋冬时节', 'sce装修制造', 'tim日常时间', 'hod节日', 'cro男性群体', 'cro浴室', 'cro生命元素',
                 'cro亲友群体', 'cro瘦人群体', 'cro厨房', 'mar口味', 'cro食物', 'mar人文宗教', 'mar颜色', 'cro居家', 'cro动植物群体', 'mar风格', 'the麻线丝棉', 'sce御寒保暖',
                 'the胶皮革绒', 'cro服装装饰', 'sce化妆美容', 'the植物原料', 'tim雨雪天气', 'cro工具建材', 'tim春夏时节', 'sce维修检测', 'the金银铜铁', 'sce户外娱乐', 'tim产后恢复',
                 'cro职场人群', 'cro身体部位', 'cro女性群体', 'o']

allTags = set()
with open('tagdata2ner_20230301/taged_data/20230309Concat.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for idx, line in enumerate(lines):
        if line == '\n':
            continue
        if line.strip() == '母 b-hod节日':
            a = 1
        else:
            cha_tag = line.split()
            if 'o' != cha_tag[1].strip():
                prefixTag = cha_tag[1].split('-')[0]
                tag = cha_tag[1].split('-')[1]
                namePrefix = ['b', 'i', 'e', 's']
                if prefixTag.strip() not in namePrefix:
                    a = 1
                if tag == 'sce户外娱':
                    bre = 'break'
                allTags.add(tag)
a = 1

with open('tagdata2ner_20230301/taged_data/20230309Concat.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    labset = set()
    onlytags = set()
    try:
        for idx, line in enumerate(lines):
            if line == '\n':
                continue
            # if len(line.strip()) == 1:
            #     print(idx, '   =====')
            #     print(line, '   =====')
            lab = line.split()[-1]
            labset.add(lab)
            if lab.startswith('o-'):
                print(idx)
                print(line)
            if lab == 'o':
                onlytags.add(lab)
            else:
                onlytags.add(lab.split('-')[-1])
    except:
        print(idx)
        print(line)

chacoll = []
for i in onlytags:
    if i not in standard_tags:
        chacoll.append(i)
