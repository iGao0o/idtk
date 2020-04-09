from django.db import models


# Create your models here.

class Permission(models.Model):
    permission_choices = {
        "user:add": ("添加用户", "100"),
        "user:del": ("删除用户", "101"),
        "dev:add": ("添加设备", "200"),
        "dev:del": ("删除设备", "201"),
    }
    name = models.CharField('name', max_length=255)
    codename = models.CharField('codename', max_length=100, primary_key=True)

    class Meta:
        db_table = "tbl_permission"
        verbose_name = "权限表"
        verbose_name_plural = verbose_name


class Role(models.Model):
    name = models.CharField(max_length=100, verbose_name="角色名称")
    permissions = models.ManyToManyField(
        Permission,
        verbose_name='permissions',
        blank=True,
    )

    class Meta:
        db_table = "tbl_role"
        verbose_name = "角色表"
        verbose_name_plural = verbose_name


class Group(models.Model):
    name = models.CharField(max_length=150, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name='permissions',
        blank=True,
    )

    class Meta:
        db_table = "tbl_group"
        verbose_name = "部门表"
        verbose_name_plural = verbose_name


class User(models.Model):
    username = models.CharField(max_length=20, verbose_name="用户名")
    password = models.CharField(max_length=50, verbose_name="密码")
    realname = models.CharField(max_length=20, verbose_name="真实姓名")
    telephone = models.CharField(max_length=50, verbose_name="手机号")
    email = models.EmailField(verbose_name="邮箱")
    default_dev = models.IntegerField(verbose_name="默认设备", null=True)
    create_time = models.DateTimeField(auto_now=True, auto_created=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    last_login = models.DateTimeField(auto_now=True, verbose_name="最近一次登陆时间")
    groups = models.ManyToManyField(Group, related_name="user_set",
                                    related_query_name="user", verbose_name="部门")
    role = models.ManyToManyField(Role, related_name="user_set",
                                  related_query_name="user", verbose_name="角色")

    class Meta:
        db_table = "tbl_user"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name
