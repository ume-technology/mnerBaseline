### version = 2.0.1

- newTags.txt: 这个是从随机的几个主要线路中随机抽取出来的NER格数据，以做标注进行NER；
- processData\tagdata2ner_20230301\taged_data\20230309AllNewTagsData.txt: 在newTags.txt文件上做了一些标注（Giikin+1688融合的数据的标注文件）
- processData\tagdata2ner_20230301\taged_data\cp-2023-1-27-first-tag-data-to-split-prt-to-prtSce: 之前版本NER的标注，但是做了一些改变；
- processData\tagdata2ner_20230301\taged_data\20230309Concat.txt：融合了数据
    - 全新标注（20230309AllNewTagsData.txt）
    - 老的NER标注数据（并不是原封不动，做了一些改动，然后融合在了一起以训练一个新的NER模型）