### 首先是tag data的工作的展开
对于正确的Giikin的广告文案的数据的标注的展开：
- ad_material_data_clean_2ner.py: clean material data; 并存储清洗干净的material数据以做NER标注；
    > 在20230301，新增了ali数据以标注，这部分清洗的数据没那么严格，保留了数字等；这部分的数据
      存储在了processData\tagdata2ner_20230301\taged_data\newTags.txt中；且需要注意的是这个数据单独保留，
      因为把这种语料和之前标注的预料融合后的训练如果不能实现很好的效果，那么就单独用这部分数据做训练。

- splitnewnertagdata.py：分割清洗出来的material数据，生成待标注的NER数据；
- 两者的区别在品类是否具体的标注出来；
    - ~~processData/tagdata2ner_new/taged_data/waittotagdata.txt~~  这部分数据没用，标注错了，其实不用标注品类的，否则标签会无穷多。
    - processData/tagdata2ner_new/taged_data/waittotagdata_cp_only_prt.txt中：这个数据是正确的数据；
- 最后需要值得注意的是：
    - processData/tagdata2ner_new/taged_data/2023-1-27-first-tag-data：是完全体的标注，即无论有多少标签在标注的时候都标注上去；
    - processData/tagdata2ner_new/taged_data/2023-1-27-first-tag-data-no-sometags：是为了训练的有效性，删除了一些过少的标签文件；
- checkdatalabels.py：执行标注的数据的标注检查；
- convertstandardtagdata2nertraindata.py：生成myTCNER参与训练的标注格式化数据；通过该脚本后会生成如下数据：
    - mid_data_*\train.json
    - ~~mid_data_*\ner_ent2id.json~~
    - mid_data_*\labels.json
    - mid_data_*\train.json    copy to    raw_data_*\stack.json
- 在raw_data_*\stack.json上执行splittraindata.py：将stack.json进行数据切分以及将数据最终转换为TC要求的标准NER数据；
- 最后执行read_clean2ner_data_to_get_test.py获取一部分test.json数据集