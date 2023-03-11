# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:readFaster.py
@Time:2023/3/1 11:58
@Read: 
"""
from functions import *

sql = """
select product_id,max(product_name) as product_name, max(detail) as detail
from giikin_aliyun.tb_dim_pro_gk_ali_tags_df 
group by product_id
;
"""
with o.execute_sql(sql).open_reader(tunnel=True) as reader:
    dataDF = reader.to_pandas()
