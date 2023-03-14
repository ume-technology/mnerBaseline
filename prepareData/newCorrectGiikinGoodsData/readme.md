### 这是准备数据的第二部分：读取的是Giikin的商品信息的过程；

- readalldata_new.py 读取的是 giikin_aliyun.tb_rp_mar_ad_material_df 表的数据作为商品数据；这个表的数据更正确且更加全面；
- 这部分的数据按照线路存储在bigfiles/newCorrectGiikinGoodsDaraSave目录下；
- 同时这些线路上的商品的源文件数据保存在云盘：newCorrectGiikinGoodsDataSave(是读取的线路上的广告语的原始数据集)
- ~~这里只保存了一个台湾地区的数据。~~
> 在这部分数据中，还有一个地方需要注意：
- 上面存储的是各个线路的原始数据集；但是有一个问题是在于存储的这些原始数据是要被用来标识标签的，这部分代码在模型的predict.py文件中：
- 首先直接 apply cleantext() 完成对newCorrectGiikinGoodsDataSave路径中的原始数据文件的读取与清洗工作；
- 然后执行了对清洗后的数据 apply predict() 完成对于数据的预测；
  ``` python
  所有这部分Giikin广告文案的数据是没有清洗后的中间数据存档的，
  是直接存储了 predict() 之后的数据，模型的预测文件就保存在相应的模型目录之下。```
- 更进一步的，当模型预测完毕后，要做的是对于预测后的数据的入库工作：这部分存储入库的工作在：importdata2mysql.py中完成。

> 因此我们只需要记住这部分的GiikinGoods的数据是最原始的数据库中的数据就可以了，其他的操作都要在这个数据集上做进一步的处理。
