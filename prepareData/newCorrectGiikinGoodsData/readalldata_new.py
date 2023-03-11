# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:restartreadgoodsmaterial.py
@Time:2023/2/1 9:30
@Read: 是对于 restartreadgoodsmaterial.py 读取商品广告素材表方案的完善，按照线路去读取数据
"""
import pickle
from functions import *

# wait 年龄范围区间过大;
# wait 投放时间和商品/线路的关系
# wait checkout_cnt(支付次数)和order_cnt(订单量)之间的差异;
# wait conversions_rate(转化率)如何计算;
# wait spend_amt(广告成本)：是如何计算出来的，是基于广告系列还是广告组计算的;
# wait last_ad_time该字段是什么意思
# sql = """ select * from giikin_aliyun.tb_rp_mar_ad_material_df where pt='20230129'"""
sql = """ -- 这个sql直接读取了所有数据太大了，没办法读取
select platfrom,line_name,designer_id,opt_id,product_id,category_lvl1_name,sale_id,    -- base info
       country,genders,age_range,media_type,last_ad_time,    -- features - 1
       product_name,sale_name,ad_slogans,interest_words,people_cover_cnt,    -- features - 2
       campaign_id,ad_group_id,impressions_cnt,clicks_cnt,add_cart_cnt,checkout_cnt,order_cnt,conversions_rate,-- ad result
       spend_amt_15d as "近15天广告成本", spend_amt as "广告成本",single_impressions_amt as "单次展示成本",single_clicks_amt as "单次点击成本",
       single_cart_amt as "单次加购成本", single_checkout_amt as "单次支付成本",kiloimpressions_amt as "千次展示成本"     -- ad cost
from giikin_aliyun.tb_rp_mar_ad_material_df where pt='20230129' and line_name = '{}';
"""

# todo 首先确定了所有的线路:line_name      # line_name_lang = {'菲律宾': 'en', '泰国': 'th'}
# pass：澳大利亚；摩洛哥；
line_names = ['澳大利亚', '摩洛哥', '菲律宾', '泰国', '台湾', '沙特阿拉伯', '越南', '匈牙利',
              '阿曼苏丹国', '中国', '韩国', '阿联酋', '罗马尼亚', '新加坡', '科威特', '香港', '马来西亚', '波兰', '卡塔尔', '日本', '美国']

# todo 为了读取本地的日本线路数据，且下面的giikin广告数据也已经读取完毕，就注释掉了这部分的代码也是没问题的
# 线路上的商品数量的计数
# line_goods_count = {'澳大利亚': 0, '摩洛哥': 0, '菲律宾': 3173707}
# for idx, i in enumerate(line_names):
#     if idx == 0 or idx == 1 or idx == 2:
#         continue
#     if idx != 19:
#         continue
#     with o.execute_sql(sql.format(i)).open_reader(tunnel=True) as reader:
#         all_top_apt = reader.to_pandas()
#     with open(i, 'wb') as f:
#         pickle.dump(all_top_apt, f)
#     line_goods_count[i] = all_top_apt.shape[0]

# todo 日本的数据在本地读
host = '192.168.4.51'
port = 4000
user = 'fanzhimin'
passwd = 'tit3hSCVwp82'
db = 'workflow_mc'
sql = """ select * from gk_ad_material where line_name = '日本' limit 1000"""
sql = """ select count(*) from gk_ad_material where line_name = '日本'"""
sql = """ select platform,line_name,sale_id,product_id,category_lvl1_name,product_name, interest_words from gk_ad_material where line_name = '日本' limit 1000000"""
sql = """ select platform,line_name,sale_id,product_id,category_lvl1_name,product_name, interest_words from gk_ad_material 
where line_name = '日本' ORDER BY unique_md5_code limit 6000000,5000000"""

conn = pymysql.connect(host=host, port=port, user=user, db=db, password=passwd, charset='utf8')

# cursor = conn.cursor()
# count_ = cursor.execute(sql)
# print(count_)

dataDF = pd.read_sql(sql, conn)

with open('../../bigfiles/newCorrectGiikinGoodsDataSave/日本6000000-LAST', 'wb') as f:
    pickle.dump(dataDF, f)
