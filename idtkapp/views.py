from django.views.generic import View
from django.core.cache import cache
from idtkapp import models
from user import models as user_model
from django_redis import get_redis_connection
from django.http import JsonResponse, HttpRequest
from django.db.models import Q
from datetime import datetime, timedelta
import random
import json
# Create your views here.

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


# 添加设备
# /idtkapp/adddev
class AddDev(View):

    def post(self, request: HttpRequest):
        token = request.headers.get("token")
        if token is None:
            return JsonResponse({"status": 1, "msg": "没有登陆"})
        user = cache.get("user:token:%s" % token)
        if user is None:
            return JsonResponse({"status": 1, "msg": "登陆已过期"})
        user = json.loads(user)
        if user_model.Permission.permission_choices['dev:add'][1] not in user['permission']:
            return JsonResponse({"status": 3, "msg": "没有权限"})
        obj = json.loads(request.body.decode("utf-8"))
        dev_sn = obj.get("dev_sn")
        name = obj.get("name")
        site = obj.get("site")
        note = obj.get("note")
        if not all([name, site, dev_sn]):
            return JsonResponse({"status": 5, "msg": "请正确填写设备的名称和位置"})
        dev = models.Device.objects.filter(Q(dev_sn=dev_sn) | Q(name=name))
        if dev.count() != 0:
            return JsonResponse({"status": 6, "msg": "设备名或者设备id重复"})

        device = models.Device(dev_sn=dev_sn, name=name, site=site, note=note,
                               status=1, user=user['id'])
        device.save()
        return JsonResponse({"status": 0, "msg": "添加成功"})
