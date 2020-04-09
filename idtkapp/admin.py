from django.contrib import admin
from idtkapp.models import Device, DeviceStatus, DeviceData


# Register your models here.


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''新增或更新表中的数据时调用'''
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        '''删除表中的数据时调用'''
        super().delete_model(request, obj)


class DeviceAdmin(BaseModelAdmin):
    pass


class DeviceStatusAdmin(BaseModelAdmin):
    pass


class DeviceDataAdmin(BaseModelAdmin):
    pass


admin.site.register(Device, DeviceAdmin)
admin.site.register(DeviceStatus, DeviceStatusAdmin)
admin.site.register(DeviceData, DeviceDataAdmin)
