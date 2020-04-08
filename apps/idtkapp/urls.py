from django.conf.urls import url
from idtkapp import views
from idtkapp import idtk_view

urlpatterns = [
    # url(r'^/dataport.aspx$', idtk_view.IndexView.as_view(), name='dataport'),  # 红外接受
    # url(r'^/idtkapp/getdefdev$', views.GetDefDevView.as_view(), name='getdefdev'),  # 获取用户默认的设备数据
    # url(r"^/idtkapp/getalldev", views.GetAllDevView.as_view(), name="getalldev"),  # 获取所有的设备信息
    # url(r"^/idtkapp/getdev/(?P<dev_sn>.+)", views.GetDevData.as_view(), name="getalldev"),  # 获取所有的设备信息
]
