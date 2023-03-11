# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:readOrders.py
@Time:2023/2/24 15:54
@Read: 读取：tb_dwd_ord_gk_order_info_crt_df 订单表数据: 读这个表的目的是为了从订单表中获取一些用户标签信息
"""
import pickle
from functions import *

sql = """
select * from giikin_aliyun.tb_dwd_ord_gk_order_info_crt_df where  pt = '20230224'
"""
with o.execute_sql(sql).open_reader(tunnel=True) as reader:
    df = reader.to_pandas()

# wait 运单号和物流公司是否相关
# todo 头程尾程只有深圳仓发出的才有
# todo is_clone：什么原因发生的克隆: 一些意外情况导致收货人商品重新发送，而导致的重新生成的订单，就是订单克隆
# todo weight/volume 暂时先不保留
# todo transfer_time --- delivery_time 采购时效分析
# todo delivery_time --- finishtime  订单层面的结束时间，是物流把订单送到手的时间，即体现物流的运送时效
# ===========================================================================================================
#      logistics_style_id（运输方式ID）和logistics_name（物流渠道名称）之间有什么区别
#      auto_verify/del_reason_id/del_reason/question_reason_id/question_reason with tb_dim_ord_gk_order_auto_verify_df
#      update_time -- delivery_time：下单到发货的平均周期 -- 再到finishtime订单完成这一步的时间周期
#      remark ?
#      ship_phone2和ship_phone
#      dpe_style(dpe下单类型/货物类型) with logistics_control 直接的匹配关系
#      wait site_type网站类型对于一个地区人群的吸引力:  site_id/site_name
#      wait third_platform_fee 三方平台费用
#      wait operat_cost运营成本是怎么来的
#      wait del_reason_id 这个字段不是特别需要，因为del_season字段也有了
#      wait 只要是海外仓的都叫改派：退货改派，备货改派（先备货到海外仓） wait 关联？表区分备货改派和退货改派
#      wait adtype:广告系列（1:广告系列；2：广告组；3：广告）；指导优化相关工作；
#      wait tag:投放类型（1:商品；2：分类；3：活动；4：站点）；
#      wait order_price: 商品的采购成本的确认对于经营分析的影响；

orders = df.drop(columns=[
    'bill_number', 'order_number', 'waybill_number', 'order_status_id', 'lang_id', 'currency_id', 'line_code',
    'team_code', 'family_name', 'company', 'org_code', 'org_name', 'cust_id', 'site_name', 'logistics_id', 'logistics_full_name',
    'logistics_simple_name', 'track_status', 'resend', 'lowerstatus', 'transfer_status', 'logistics_status_a', 'weight', 'volume',
    'logistics_style_id', 'logistics_style', 'ship_name', 'ship_lastname', 'ship_address', 'ship_zip', 'ship_email', 'ip', 'begroup',
    'flag', 'card_no', 'logistics_update_time', 'del_time', 'order_status_name', 'logistics_fee', 'pay_domain', 'api_create', 'fbclid',
    'import_weight', 'ship_address2', 'show_type', 'show_name', 'recommener', 'is_change', 'logistics_status_id', 'mobile', 'browser', 'os',
    'engine', 'version', 'engineversion', 'site_type', 'payed4', 'finish_status', 'is_unusual_weight', 'is_unusual_freight', 'main_sale_cnt',
    'family_manager', 'logistics_status', 'exclud_apportion_purchase_cost', 'abroad_whl_apportion_cost'
])
orders = orders.drop(columns=['question_reason_id'])
orders = orders.drop(columns=['coupon', 'discount', 'remote_fee', 'consumption_tax'])
orders = orders.drop(columns=['pay_type_id', 'market_id', 'lang_name', 'currency_name', 'currency_lang_id', 'sale_cnt', 'payment_id', 'userid'])
orders = orders.drop(columns=['is_clone', 'ship_country', 'del_reason_id', 'auto_verify', 'update_time', 'verify_time'])
orders = orders.drop(columns=['cart_info', 'service_fee', 'user_agent'])
orders = orders.drop(columns=['is_test_product', 'low_price', 'befrom_old', 'order_amt', 'is_first_journey', 'payed', 'third_platform_fee', 'is_effective_order', 'off_stock_type'])
orders = orders.drop(columns=['freight', 'freight1', 'fee13', 'fee46'])


def saveOrderData(data):
    with open('../../bigfiles/giikinOrderData4UserTags/ordersData.pick', 'wb') as f:
        pickle.dump(data, f)
    print('end')

# if __name__ == '__main__':
#     saveOrderData(orders)
