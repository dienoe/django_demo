import base64
import pickle

from django_redis import get_redis_connection
from rest_framework import response


def merge_cart_cookie_to_redis(request,user,response):
    """
    登陆时合并购物车，将cookie中的数据合并到redis中
    登陆时，cookie中的数据如果存在于redis中相同的商品记录，如何处理的问题
    1.商品数量 以cookie为准
    2.勾选状态
    合并前
    redis_cart={
            '1'；‘20’，
            ‘2’：‘2’，
            ‘3’：‘5’，
            }
    redis_cart_selected=set(1,3)
    cookie_cart={
        1:{
        'count':10,
        'selecte':False
        },
        4:{
        'count':6,
        'selected':True
        }
    }
    合并后
     redis_cart={
            '1'；‘10’，
            ‘2’：‘2’，
            ‘3’：‘5’，
            '4':'6'
            }
    redis_cart_selected=set(3,4)
    :return:
    """
    #获取cookie中的购物车数据
    # cookie_cart
    cookie_cart = request.COOKIES.get('cart')
    if not cookie_cart:
        """表示cookie有购物车数据"""
        return response
        # 解析
    cookie_cart_dict = pickle.loads(base64.b64decode((cookie_cart.encode())))
    # else:
    #     # 表示cookue中没有购物车数据
    #     cookie_cart_dict = {}
    # 获取redis中的购物车商品数量数据 hash
    redis_conn = get_redis_connection('cart')
    redis_cart = redis_conn.hgetall('cart_%s' % user.id)
    # 用来存储redis最终保存的商品数量信息的hash数据
    cart={}
    for sku_id,count in redis_cart.items():
        cart[int(sku_id)]=int(count)
    # 用来记录redis最终操作时,那些sku_id 是需要勾选新增的
    redis_cart_selected_add=[]

    # 用来记录redis最终操作时,那些sku_id 是需要取消勾选删除的
    redis_cart_selected_remove=[]
    # 遍历cookie中的购物车
    for sku_id,count_selected_dict in cookie_cart_dict.items():
    #   处理商品的数量，维护在redis中购物车数据数量的最终字典
        cart[sku_id]=count_selected_dict['count']

        #     cart[sku_id]=count
        #   处理商品的勾选状态
        if count_selected_dict['selected']:
            #  如果cookie指明,勾选
            redis_cart_selected_add.append(sku_id)
        else:
            #  如果cookie指明,不勾选
            redis_cart_selected_remove.append(sku_id)
    if cart:
        # 执行redis操作
        pl=redis_conn.pipeline()
        # 设置hash类型
        # redis_conn.hmset('cart_%s'%user.id,cart)
        pl.hmset('cart_%s'%user.id,cart)
        # 设置set类型
        if redis_cart_selected_remove:
            pl.srem('cart_selected_%s'%user.id,*redis_cart_selected_remove)
        if redis_cart_selected_add:
            pl.sadd('cart_selected_%s'%user.id,*redis_cart_selected_add)
        pl.execute()
    # 删除cookie
    response.delete_cookie('cart')
    return response
