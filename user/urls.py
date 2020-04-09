from django.conf.urls import url
from user import views

urlpatterns = [
    url(r'^login$', views.LoginView.as_view(), name='login'),  # 登陆
    url(r'^logout$', views.LogOutView.as_view(), name='logout'),  # 登陆
]
