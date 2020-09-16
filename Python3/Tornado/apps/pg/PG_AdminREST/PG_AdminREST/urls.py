"""PG_AdminREST URL Configuration

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
from django.urls import include
from django.urls import path
from rest_framework import routers
from restapi import views
from restapi.views import Reset, ResetKey, ResetGoogleCode, AdminReset

router = routers.DefaultRouter()
router.register(r'Users', views.UsersViewSet, basename="Users")
router.register(r'WithdrawConfig', views.WithdrawConfigViewSet, basename="WithdrawConfig")
router.register(r'CollectionFeeConfig', views.CollectionFeeConfigViewSet, basename="CollectionFeeConfig")
router.register(r'CollectionConfig', views.CollectionConfigViewSet, basename="CollectionConfig")
router.register(r'WithdrawOrder', views.WithdrawOrderViewSet, basename="WithdrawOrder")
router.register(r'Deposit', views.DepositViewSet, basename="Deposit")
router.register(r'CollectionRecords', views.CollectionRecordsViewSet, basename="CollectionRecords")
router.register(r'Address', views.AddressViewSet, basename="Address")
router.register(r'Subaddress', views.SubaddressViewSet, basename="Subaddress")
router.register(r'UserAddressBalances', views.UserAddressBalancesViewSet, basename="UserAddressBalances")
router.register(r'UserTokenBalances', views.UserTokenBalancesViewSet, basename="UserTokenBalances")
router.register(r'AssetDailyReport', views.AssetDailyReportViewSet, basename="AssetDailyReport")
router.register(r'UserOperationLog', views.UserOperationLogViewSet, basename="UserOperationLog")
#内部管理台新增
router.register(r'AddAddressOrder', views.AddAddressOrderViewSet, basename="AddAddressOrder")
router.register(r'AdminOperationLog', views.AdminOperationLogViewSet, basename="AdminOperationLog")

urlpatterns = [
    path('adminrest/', include(router.urls)),
    path('adminrest/refresh/', views.Refresh_jwt_token),
    path('adminrest/login/', views.obtain_jwt_token),
    path('adminrest/reset/', Reset.as_view()),
    path('adminrest/resetkey/', ResetKey.as_view()),
    path('adminrest/resetgooglecode/', ResetGoogleCode.as_view()),
    path('adminrest/adminreset/', AdminReset.as_view()),

    # re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    # path('adminrest/docs/', include_docs_urls(title='文档')),
    # path('admin/', admin.site.urls),
]


