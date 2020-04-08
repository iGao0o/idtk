from django.views.generic import View
from django.core.cache import cache
from idtkapp.models import Device, DeviceStatus, DeviceData, DeviceLogModel
from django_redis import get_redis_connection
from django.http import JsonResponse, HttpRequest
from django.contrib.auth.models import User, Permission
from datetime import datetime, timedelta
from django.core import signing

import random
import json


# Create your views here.
# /idtkapp/login
class LoginView(View):

    def post(self, request: HttpRequest):
        data = json.loads(request.body)
        print(data)
        user = {"id": random.randint(1, 10000), "name": data['username']}
        token = signing.dumps(user)
        cache.set("user:%s" % token, json.dumps(user))
        data = {"status": 0, "data": "1234567"}
        return JsonResponse(data)


# /idtkapp/logout
class LogOutView(View):

    def get(self, request):
        pass


# 获取所有的列表
# /idtkapp/getalldev
class GetAllDevView(View):

    def get(self, request):
        dev_data = []
        for i in range(100):
            dev = {
                "name": "dev_%s" % i,
                "dev_sn": "dev_sn_%s" % i,
                "site": "门口_%s" % i,
                "note": "",
                "status": random.randint(1, 2),
                "create_user": "user_%s" % i,
                "create_time": datetime.now().strftime("%Y-%m-%d %X"),
                "update_time": datetime.now().strftime("%Y-%m-%d %X")
            }
        data = {"status": 0, "data": dev_data}
        return JsonResponse(data)


# 获取用户默认的设备信息
# /idtkapp/getdefdev
class GetDefDevView(View):

    def getData(self):
        start_time = datetime.now()
        start_time = start_time.replace(hour=9, minute=0, second=0)
        end_time = datetime.now()
        time_data = []
        time_in = []
        time_out = []
        while start_time < end_time:
            time_data.append(start_time.strftime("%X"))
            time_in.append(random.randint(20, 50))
            time_out.append(random.randint(10, 30))
            start_time = start_time + timedelta(hours=1)

        data = {
            "din": 300,  # 当天全部进入
            "dout": 200,  # 当天全部离开
            "dhin": 100,  # 当前小时进入
            "dhout": 50,  # 当前小时离开
            "time": time_data,  # 时间
            "timeIn": time_in,  # 指定时间的进入
            "timeOut": time_out  # 指定时间的离开
        }
        return data

    def get(self, request: HttpRequest):
        data = {
            "status": 0,
            "data": self.getData()
        }
        return JsonResponse(data)


# 获取指定设备的信息
# /idtkapp/getdev/devsn
class GetDevData(View):
    def get(self, request, dev_sn):
        print("dev sn = ", dev_sn)
        dev_sn = int(dev_sn, 16)
        dev_data = {
            "time": [],
            "timeIn": [],
            "timeOut": []
        }
        data = {"status": 0, "data": dev_data}
        return JsonResponse(data)
