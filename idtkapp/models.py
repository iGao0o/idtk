from django.db import models


# Create your models here.

class DeviceStatus(models.Model):
    flag = models.IntegerField(verbose_name="标志位 16进制转为10进制")
    version = models.IntegerField(verbose_name="设备的版本 16进制转为10进制")
    dev_sn = models.CharField(max_length=50, verbose_name="设备的SN 16进制转为10进制")
    ir_voltage = models.IntegerField(verbose_name="发射设备的电量")
    voltage = models.IntegerField(verbose_name="接受设备的电量")
    get_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ods_cache_status"
        verbose_name = "设备状态表"
        verbose_name_plural = verbose_name


class DeviceData(models.Model):
    focus_status = (
        (1, "正常"),
        (0, "失焦"),
    )
    dev_time = models.DateTimeField()
    focus = models.IntegerField(verbose_name="失焦状态")
    din = models.IntegerField(verbose_name="进入")
    dout = models.IntegerField(verbose_name="离开")
    get_time = models.DateTimeField(verbose_name="获取数据的时间")
    status = models.OneToOneField(DeviceStatus, on_delete=models.CASCADE)

    class Meta:
        db_table = "ods_cache_data"
        verbose_name = "设备数据表"
        verbose_name_plural = verbose_name


class Device(models.Model):
    status_choices = (
        (0, '下线'),
        (1, '上线'),
        (2, "失效"),
    )
    dev_sn = models.CharField(max_length=50, verbose_name="设备SN", primary_key=True)
    name = models.CharField(max_length=50, verbose_name="设备名称")
    site = models.CharField(max_length=100, verbose_name="设备安装地址")
    note = models.CharField(max_length=200, verbose_name="设备的描述")
    status = models.IntegerField(default=1, choices=status_choices, verbose_name="设备的状态")
    create_time = models.DateTimeField(auto_now=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="设备更新时间")
    user = models.IntegerField(verbose_name="添加的用户")

    class Meta:
        db_table = "ods_device"
        verbose_name = "设备配置表"
        verbose_name_plural = verbose_name


class DeviceLogModel(models.Model):
    create_time = models.DateTimeField(auto_created=True, verbose_name="创建时间")
    get_msg = models.CharField(max_length=255, verbose_name="接收到的信息")
    res_msg = models.CharField(max_length=255, verbose_name="返回的信息")

    class Meta:
        db_table = "ods_dev_log"
        verbose_name = "日志表"
        verbose_name_plural = verbose_name
