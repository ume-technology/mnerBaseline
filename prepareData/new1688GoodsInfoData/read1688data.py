# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:read1688data.py
@Time:2023/2/17 15:46
@Read: 这个是1688的商品数据信息；读取并存储
"""
from functions import *


def readAliOriginalData():
    """
    todo : 读取的数据有些问题，不要用这个表
    """
    host = 'rm-wz91q7472p7u635u3xo.mysql.rds.aliyuncs.com'
    db = 'scms'
    port = 3306
    user = 'fanzhimin'
    passwd = 'Osm$rhIeLWuvH2ek'
    conn = pymysql.connect(host=host, port=port, user=user, db=db, password=passwd, charset='utf8')

    # cursor = conn.cursor()

    sql = """select pid,name,detail from gk_ali_tags"""
    dataDF = pd.read_sql(sql, conn)
    return dataDF


def readAliOriginalDataFromDW():
    """
    todo 基于DW表中的数据进行读取读取
    """
    sql = """
select product_id,product_name,detail
from (select product_id,product_name,detail
            ,ROW_NUMBER() OVER(PARTITION BY product_id ORDER BY crt_time desc) AS rn 
      from giikin_aliyun.tb_dim_pro_gk_ali_tags_df 
      ) a
where rn = 1
;
    """
    with o.execute_sql(sql).open_reader(tunnel=True) as reader:
        dataDF = reader.to_pandas()

    return dataDF


dataDF = readAliOriginalDataFromDW()

with open('../../bigfiles/new1688GoodsInfoDataSave/ali_tags_dw.pick', 'wb') as f:
    pickle.dump(dataDF, f)

# with open('../../bigfiles/new1688GoodsInfoDataSave/ali_tags.pick', 'rb') as f:
#     aliTagsData = pickle.load(f)


# if __name__ == '__main__':
#     dataDF = readAliOriginalDataFromDW()
#     pass
