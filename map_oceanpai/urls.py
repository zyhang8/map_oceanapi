"""map_oceanpai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path

from ice_ocean import views as ice_ocean
from ice_mean import views as ice_mean


app_name = 'ice_ocean'


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^ice_ocean/latitude1/(.+)/latitude2/(.+)/longitude1/(.+)/longitude2/(.+)/$', ice_ocean.gen_map, name="ice_oceanapi"),
    url(r'^ice_mean/latitude1/(.+)/latitude2/(.+)/longitude1/(.+)/longitude2/(.+)/$', ice_mean.get_map, name="ice_mean"),
]
