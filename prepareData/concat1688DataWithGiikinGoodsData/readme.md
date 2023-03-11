### 这是 Giikin 和 1688数据结合的第三个部分：融合两者的数据

- 读取了aliTag的标签信息；这个数据是以产品类别为基准的；
- 然后读取了Giikin的各个线路上的数据信息，然后清洗这部分的数据信息；
- 并对每个线路的数据按照线路存储在bigfiles\newCorrectGiikinGoodsDataSave\cleanOriginalAdsData
  > 因此要注意的是：bigfiles\nerCodeBaseLineOutput\giikin_alltageddata_new存储的都是在model predict.py的过程中清洗并预测的结果文件；
- 然后进一步融合两者数据，目标：可以拿到不同线路上，非中文数据对应的商品标签:
    - 为文案生成提供中文标签；
    - 可以实现所有产品的标签查询；
    - 商品标签用来支撑实现更多的其他业务；