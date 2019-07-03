# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from meiduo_mall.libs.captcha.captcha import captcha
from django.shortcuts import render
from django_redis import get_redis_connection

# Create your views here.
from verifications import constants
from verifications.seriailzers import ImageCodeCheckSerializer


class ImageCodeView(APIView):
    """图片验证码"""
    def get(self,request,image_code_id):
        print("xxx")
        # 生成验证码图片
        text,image=captcha.generate_captcha()
        # 保存真实值0
        redis_conn=get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 返回图片
        return HttpResponse(image,content_type='image/jpg')
# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(GenericAPIView):
    """
    短信验证码
    传入参数：
        mobile, image_code_id, text
    """
    serializer_class = ImageCodeCheckSerializer
    def get(self,request,mobile):
        # 校验参数　由序列化器完成
        serializer=self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 生成短信验证码
        # 保存短信验证码　发送记录
        # 发送短信
        # 返回
        pass