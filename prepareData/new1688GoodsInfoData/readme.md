### 这是数据准备阶段的第一部分：准备并清洗1688数据的过程；

- 在newCorrectGiikinGoodsDat中：读取的数据都是Giikin的广告文案数据；这些数据是不充分的；
- 因此在这里读取1688的商品数据，这些数据比Giikin的广告文案数据的质量高：
    - 1688的数据信息来自库： rm-wz91q7472p7u635u3xo.mysql.rds.aliyuncs.com 这个库里的信息；
    - 数据存储在：new1688GoodsInfoDataSave目录下；
    - 数据保存在度盘：Giikin公司的Ali商品数据集-用来做NER的原始语料 目录下；

> 原来AliTags的数据是从rm-wz91q7472p7u635u3xo.mysql.rds.aliyuncs.com读取的，但是这个库的数据有问题；
> 因此从这个数据从DW上查询：tb_dim_pro_gk_ali_tags_df：存储的数据名称就是 ali_tags_dw.pick；
> 同时可以把这个1688的数据和newCorrectGiikinGoodsDataSave中的数据对标，即明确Giikin的商品和1688的对应关系，以明确产品本质上更多的标签信息；
> 清洗detail字段信息：
- 基于cleanData.py，完成detail字段的格式化拼接，并存储在bigfiles\new1688GoodsInfoDataSave\clean_ali_tags.pick中
- 清洗了ali的 detail 字段的信息后的数据存储在clean_ali_tags_dw.pick 