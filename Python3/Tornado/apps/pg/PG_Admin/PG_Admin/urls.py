"""PG_Admin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
# import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from django.views.generic import RedirectView
from pgadmin.views import ResetPasswd, ResetKey, ResetGoogleCode


urlpatterns = [

    # path(r'favicon.ico', RedirectView.as_view(url=r'static/admin/favicon.ico')),
    path('admin/', admin.site.urls),
    path(r'mdeditor/', include('mdeditor.urls')),
    path('admin/resetpasswd/', ResetPasswd.as_view()),
    path('admin/resetkey/', ResetKey.as_view()),
    path('admin/resetgooglecode/', ResetGoogleCode.as_view()),
    # path('__debug__/', include(debug_toolbar.urls)),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


