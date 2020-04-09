from django.shortcuts import render
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
import json
from django.core import signing
from user import models
from datetime import datetime
from django.core.cache import cache
from django_redis import get_redis_connection
from collections import namedtuple

# Create your views here.
# /idtkapp/login
class LoginView(View):
    def get_user_data(self, user):
        user_data = {
            "id": user.id,
            "username": user.username,
            "realname": user.realname,
            "telephone": user.telephone,
            "email": user.email,
            "create_time": user.create_time.strftime("%Y-%m-%d %X"),
            "update_time": user.update_time.strftime("%Y-%m-%d %X"),
            "last_login": user.last_login.strftime("%Y-%m-%d %X"),
            "groups": [g.id for g in user.groups.all()],
            "role": [r.id for r in user.role.all()],
            "permission": set(),
        }
        for g in user.groups.all():
            user_data['permission'] = user_data['permission'].union({p.codename for p in g.permissions.all()})
        for r in user.role.all():
            user_data['permission'] = user_data['permission'].union({p.codename for p in r.permissions.all()})
        user_data['permission'] = list(user_data['permission'])
        return user_data

    def post(self, request: HttpRequest):
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        try:
            user = models.User.objects.get(username=username, password=password)
        except Exception as e:
            data = {"status": 1, "msg": "登陆失败"}
            return JsonResponse(data)
        user.last_login = datetime.now()
        user.save()
        user_data = self.get_user_data(user)
        token = signing.dumps(user_data)
        # 设置token
        cache.set("user:token:%s" % token, json.dumps(user_data), timeout=60 * 5)
        data = {"status": 0, "msg": "登陆成功", "data": token}
        return JsonResponse(data)


# /idtkapp/adduser
class AddUser(View):

    def check_three(self, group, role, permission):
        """
        检查权限三要素
        :param group:
        :param role:
        :param permission:
        :return:
        """
        # 不能为空 且必须为list类型
        if not all([group, role, permission]) or not all([isinstance(group, list),
                                                          isinstance(role, list),
                                                          isinstance(permission, list)]):
            return None
        getGroup = [models.Group.objects.get(id=g) for g in group]
        getRole = [models.Role.objects.get(id=r) for r in role]
        getPer = {models.Permission.objects.get(id=p) for p in permission}
        # 获取部门下的基础权限
        for g in getGroup:
            getPer = getPer.union(g.permissions.all())
        # 获取角色下的基础权限
        for r in getRole:
            getPer = getPer.union(r.permissions.all())
        result = namedtuple("resule", ['group', 'role', 'permission'])
        return result(group=getGroup, role=getRole, permission=getPer)

    def post(self, request: HttpRequest):
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password", "123456")
        default_password = password == "123456"
        realname = data.get("realname")
        telephone = data.get("telephone")
        email = data.get("email")
        if not all([username, realname, telephone]):
            return JsonResponse({"status": 1, "msg": "请设置正确的用户信息"})
        try:
            models.User.objects.get(username=username)
        except Exception as e:
            return JsonResponse({"status": 2, "msg": "请设置正确的用户信息"})
        group = data.get("group")
        role = data.get("role")
        permission = data.get("permission")
        # 角色 部门 权限 都不嫩为空 如果不存在需要新建
        check = self.check_three(group, role, permission)
        if check is None:
            return JsonResponse({"status": 3, "msg": "权限设置错误"})
        # 创建用户
        user = models.User(username=username, password=password, realname=realname, telephone=telephone, email=email)
        user.groups = check.group
        user.role = check.role
        user.permissions = check.permission
        user.save()
        return JsonResponse({"status": 0, "msg": "添加成功" + " 已成功设置默认密码" if default_password else ""})


# /user/logout
class LogOutView(View):

    def get(self, request: HttpRequest):
        token = request.headers.get("token")
        print("token = ", token)
        cache.delete_pattern("user:token:%s" % token)
        return JsonResponse({"status": 0, "msg": "登出成功"})
