# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:restartreadgoodsmaterial.py
@Time:2023/2/1 9:30
@Read: 因此在这个文件中，重新尝试读取更全的goods数据；只是这个不能完全读出来；
       因此有了readalldata_new.py分线路去读取数据；
       todo 因此这个文件不用了，只用 readalldata_new.py 文件就可以完成源数据读取的功能；
"""
from functions import *

# sql = """
# select platfrom,line_name,designer_id,opt_id,product_id,product_name,sale_id,sale_name,category_lvl1_name,
#     country,genders,,age_range,media_type,last_ad_time,
#     ad_slogans,interest_words,people_cover_cnt,
#     campaign_id,ad_group_id,impressions_cnt,clicks_cnt,add_cart_cnt,checkout_cnt,order_cnt,conversions_rate,
#     spend_amt_15d as 近15天广告成本, spend_amt as 广告成本, single_impressions_amt as 单次展示成本,single_clicks_amt as 单次点击成本,
#     single_cart_amt as 单次加购成本, single_checkout_amt as 单次支付成本,kiloimpressions_amt as 千次展示成本
#     from giikin_aliyun.tb_rp_mar_ad_material_df where pt='20230129' limit 1000;
# """
sql = """
select
    platfrom,line_name,designer_id,opt_id,product_id,category_lvl1_name,sale_id,    -- base info
    country,genders,age_range,media_type,last_ad_time,    -- features - 1
    product_name,sale_name,ad_slogans,interest_words,people_cover_cnt,    -- features - 2
    campaign_id,ad_group_id,impressions_cnt,clicks_cnt,add_cart_cnt,checkout_cnt,order_cnt,conversions_rate,-- ad result
    spend_amt_15d as "近15天广告成本", spend_amt as "广告成本",single_impressions_amt as "单次展示成本",single_clicks_amt as "单次点击成本",
    single_cart_amt as "单次加购成本", single_checkout_amt as "单次支付成本",kiloimpressions_amt as "千次展示成本"     -- ad cost
from giikin_aliyun.tb_rp_mar_ad_material_df where pt='20230129';
"""
# sql_demo = """ select * from giikin_aliyun.tb_rp_mar_ad_material_df where pt='20230129' limit 1000"""
# with o.execute_sql(sql_demo).open_reader(tunnel=True) as reader:
#     demo = reader.to_pandas()
with o.execute_sql(sql).open_reader(tunnel=True) as reader:
    all_top_apt = reader.to_pandas()
