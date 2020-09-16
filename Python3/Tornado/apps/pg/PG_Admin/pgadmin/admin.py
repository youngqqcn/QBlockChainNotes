#!/usr/bin/env python
#-*- coding:utf-8 -*-

#VersionNo: 1.0
#Author: fhh
#DateTime: 2020/5/12 17:36
#Describe:   实现后台显示
#Function:
#Journal:

import os
import re
import time
import ed25519
import redis as redis
from django.contrib import admin
from django.contrib import messages
from import_export.admin import ExportActionModelAdmin
from import_export.formats.base_formats import CSV, XLSX, XLS
from PG_Admin.settings import g_MNEMONIC, REDIS_HOST, REDIS_PORT, REDIS_API_KEY_DB_NAME, \
    REDIS_API_KEY_DB_NAME_CACHE, g_IS_MAINNET
from lib.log import get_default_logger
from lib.my_bip44.wrapper import gen_bip44_subaddr_from_mnemonic
from lib.seng_mq import send_order_id_to_msq
from datetime import datetime
from pgadmin.models import Project, AddAddressOrder, Subaddress, Deposit, Address \
    , CollectionRecords, WithdrawOrder, WithdrawConfig, CollectionConfig, CollectionFeeConfig, UserAddressBalances, \
    AssetDailyReport, UserTokenBalances, UserOperationLog, DjangoAdminLog
import hashlib
from binascii import hexlify
from django.utils.text import capfirst

logger = get_default_logger()

# Register your models here.

admin.site.site_title = '沙暴管理台'
admin.site.site_header = '沙暴支付网关管理后台'



def add_addr(token_name, account_index, addr_index):

    mnemonic = g_MNEMONIC
    nettype = 'mainnet'
    if not g_IS_MAINNET:
        nettype = 'testnet'

    if token_name == 'USDT':
        token_name = 'ETH'
    elif token_name == 'BTU':
        token_name = 'HTDF'

    return gen_bip44_subaddr_from_mnemonic(mnemonic=mnemonic,
                                            coin_type=token_name,
                                            account_index=account_index,
                                            address_index=addr_index,
                                            nettype=nettype)


def withdrawconfig_safe(comment, request, formsets):
    if comment.token_name == "USDT" or comment.token_name == 'BTU':
        value = str(formsets[3].cleaned_data)
        if comment.token_name == 'USDT':
            token = 'ETH'
        elif comment.token_name == 'BTU':
            token = 'HTDF'
        else:
            token = comment.token_name

        if re.search(token, value):
            pass
        else:
            # messages.error(request, "不可以独立配置USDT")
            raise Exception(f"不可以独立配置{comment.token_name}")

def CollectionConfig_safe(comment, request, formsets):
    if comment.token_name == "USDT" or comment.token_name == 'BTU':
        value = str(formsets[1].cleaned_data)
        if comment.token_name == 'USDT':
            token = 'ETH'
        elif comment.token_name == 'BTU':
            token = 'HTDF'
        else:
            token = comment.token_name

        if re.search(token, value):
            pass
        else:
            is_exits = CollectionConfig.objects.filter(pro_id=comment.pro_id, token_name=token)
            if is_exits:
                pass
            else:
                # messages.error(request, "不可以独立配置USDT")
                raise Exception(f"不可以独立配置{comment.token_name}")

@admin.register(Deposit)
class DepositAdmin(ExportActionModelAdmin):
    """
    充币
    """

    search_fields = ('pro_id__pro_name', 'token_name','from_addr', 'to_addr')

    list_display = ('pro_id', 'token_name','amount',
                   'from_addr', 'to_addr','block_time','tx_confirmations',
                    'block_height','tx_hash','memo',
                    )
    list_per_page = 18
    readonly_fields = ('pro_id', 'tx_hash', 'from_addr', 'to_addr',
                    'memo', 'amount','block_height','block_time','notify_status',
                    'tx_confirmations','token_name')


    list_select_related = False

    DEFAULT_FORMATS = [CSV, XLS, XLSX, ]
    formats = DEFAULT_FORMATS


    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def has_change_permission(self, request, obj=None):
        # 禁用保存按钮
        return False

@admin.register(WithdrawOrder)
class WithdrawOrderAdmin(ExportActionModelAdmin):
    """
    提币
    """

    search_fields = ('pro_id__pro_name', 'serial_id', 'order_id', 'token_name',)

    list_display = ('pro_id', 'serial_id', 'order_id','token_name', 'amount',
                    'order_status','transaction_status','notify_status','notify_times',
                    'block_height','tx_confirmations','from_addr', 'to_addr', 'tx_hash',
                    'block_time','complete_time','memo','remark',)
    list_per_page = 18

    readonly_fields = ('pro_id', 'serial_id', 'order_id', 'tx_hash',
                    'from_addr', 'to_addr', 'memo','amount','block_height',
                    'tx_confirmations','token_name','order_status',
                    'transaction_status','notify_status','notify_times'
                    ,'block_time','complete_time','remark','callback_url')
    ordering = ('-serial_id',)
    list_select_related = False


    DEFAULT_FORMATS = [CSV, XLS, XLSX, ]
    formats = DEFAULT_FORMATS

    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def has_change_permission(self, request, obj=None):
        # 禁用保存按钮
        return False

@admin.register(CollectionRecords)
class CollectionRecordsAdmin(ExportActionModelAdmin):
    """
    归集记录
    """

    search_fields = ('pro_id__pro_name', 'token_name', 'amount', 'from_address', 'to_address',)

    list_display = ('pro_id', 'token_name' ,  'amount','collection_type',
                    'complete_time','transaction_status',
                    'from_address', 'to_address', 'block_height','tx_confirmations' ,'tx_hash','block_time')
    list_per_page = 18

    readonly_fields = ('pro_id', 'complete_time', 'amount',
                    'from_address', 'token_name' ,'to_address', 'tx_hash',
                    'block_height', 'transaction_status', 'collection_type','tx_confirmations','block_time')
    ordering = ('-complete_time',)
    list_select_related = False


    DEFAULT_FORMATS = [CSV, XLS, XLSX, ]
    formats = DEFAULT_FORMATS

    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def has_change_permission(self, request, obj=None):
        # 禁用保存按钮
        return False

class CollectionConfigInline(admin.TabularInline):
    """
    归集配置列表
    """

    model = CollectionConfig
    max_num = 0
    readonly_fields = ('token_name', 'collection_dst_addr', 'min_amount_to_collect')
    can_delete = False

class CollectionConfigAddInline(admin.TabularInline):
    """
    归集配置增加
    """

    model = CollectionConfig
    extra = 0
    readonly_fields = ()
    can_delete = False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return  queryset.none()

class WithdrawConfigInline(admin.TabularInline):
    """
    提币配置
    """

    model = WithdrawConfig
    extra = 0
    readonly_fields = ('address','is_open',)
    can_delete = False

class CollectionFeeConfigInline(admin.TabularInline):
    """
    手续费配置
    """

    model = CollectionFeeConfig
    extra = 1
    max_num = 1
    readonly_fields = ('address',)
    # exclude = ('token_name',)
    can_delete = False
    classes = ('collapsed')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    项目方
    """
    search_fields = ('pro_id', 'pro_name', 'tel_no', 'email',)
    list_display = ('pro_id', 'pro_name', 'tel_no', 'email', 'create_time', 'account_status')
    list_per_page = 18
    exclude = ('bip44_account_index',)
    readonly_fields = (
    'api_key', 'client_sign_key', 'client_verify_key', 'server_sign_key', 'server_verify_key', 'pro_id')
    ordering = ('-pro_id',)

    inlines = [CollectionConfigInline, CollectionConfigAddInline, CollectionFeeConfigInline, WithdrawConfigInline]

    fieldsets = [
        ('项目方信息', {'fields': ('pro_id', 'pro_name', 'tel_no', 'email', 'account_status')}),
        ('密钥', {
            'fields': ('api_key', 'client_sign_key', 'server_verify_key'),
            'classes': ('collapse collapsed',),

        }),
    ]

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    ##################  重置密钥  ########################

    def resetkey(self, request, queryset):
        pass

    resetkey.style = 'color:grey;'
    resetkey.short_description = '重置密钥！'
    resetkey.action_type = 1
    resetkey.action_url = f'/admin/resetkey/'

    #####################################################

    ##################  重置密码  ########################

    def resetpasswd(self, request, queryset):
        pass

    resetpasswd.style = 'color:grey;'
    resetpasswd.short_description = '修改密码！'
    resetpasswd.action_type = 1
    resetpasswd.action_url = f'/admin/resetpasswd/'

    #####################################################

    ###############  重置谷歌验证码  #####################

    def resetgooglecode(self, request, queryset):
        pass

    resetgooglecode.style = 'color:grey;'
    resetgooglecode.short_description = '重置谷歌验证码！'
    resetgooglecode.action_type = 1
    resetgooglecode.action_url = f'/admin/resetgooglecode/'
    ######################################################

    # 增加自定义按钮
    actions = ['resetkey', 'resetpasswd', 'resetgooglecode']

    def save_related(self, request, form, formsets, change):
        """
        重写 提笔配置,归集配置,手续费配置
        :param request:
        :param form:
        :param formsets:
        :param change:
        :return:
        """

        try:
            if change == True:

                # 修改保存内容
                print(f"change save_related")

                rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME_CACHE,
                                  decode_responses=True)
                is_cache = rds.get('/*@_admin_Project_frequency_$*/')
                if is_cache:
                    messages.error(request, '重复提交!')
                    return False
                else:
                    rds.set('/*@_admin_Project_frequency_$*/', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    rds.expire('/*@_admin_Project_frequency_$*/', 3)
                    print(f'project_admin cache save as redis')

                for formset in formsets:
                    list_comment = formset.save(commit=False)

                    for comment in list_comment:

                        # 只有数据有变动才会进来,否则list_commet为空
                        if isinstance(comment, WithdrawConfig):
                            if comment.id == None:
                                withdrawconfig_safe(comment, request, formsets)
                                account_index = int(str(comment.pro_id_id))
                                comment.address = add_addr(comment.token_name, account_index, 0)
                                print('withdrawconfing创建行为!')
                                print(f'创建提币地址')
                            else:
                                select_withdrawconfig = WithdrawConfig.objects.filter(address=comment.address, token_name=comment.token_name).first()
                                if not select_withdrawconfig:
                                    raise Exception(f"不可以更改已有币种:{comment.token_name}")

                        if isinstance(comment, CollectionConfig):
                            CollectionConfig_safe(comment, request, formsets)
                            if comment.token_name == 'BTU':
                                print('BTU collectionconfing 创建行为!')
                                account_index = int(str(comment.pro_id_id))
                                address = add_addr(comment.token_name, account_index, 100000000)
                                CollectionFeeConfig.objects.create(pro_id=comment.pro_id, token_name='HRC20FEE', address=address)

                        if isinstance(comment, CollectionFeeConfig):
                            raise Exception(f"手续费币种和地址不可更改!")

                        # if isinstance(comment, CollectionConfig):
                        #     if comment.id != None:
                        #         for j in formset.initial_forms:
                        #             if j.initial["token_name"] == comment.token_name:
                        #                 old_addr = j.initial["collection_dst_addr"]
                        #                 break
                        #
                        #         if comment.collection_dst_addr != old_addr:
                        #             comment.collection_dst_addr = old_addr
                        #             messages.error(request, f'危险!! {comment.token_name} 归集地址不可更改, 地址已回退, 归集金额修改成功,请联系管理员!')

                return super().save_related(request, form, formsets, change)

            select_rst = Project.objects.all().order_by('-pro_id').first()
            account_index = select_rst.pro_id
            print(f'account_index{account_index}')
            print(f'creat save_related')
            for formset in formsets:
                list_comment = formset.save(commit=False)

                for comment in list_comment:

                    if isinstance(comment, WithdrawConfig):
                        #检测USDT独立配置问题!!!
                        withdrawconfig_safe(comment, request, formsets)
                        comment.address = add_addr(comment.token_name, account_index, 0)
                        print('WithdrawConfig 创建行为!')

                    if isinstance(comment, CollectionFeeConfig):
                        if comment.token_name == 'ERC20FEE':
                            comment.address = gen_bip44_subaddr_from_mnemonic(mnemonic=g_MNEMONIC,
                                                                              coin_type='ETH',
                                                                              account_index=account_index,
                                                                              address_index=100000000)
                        else:
                            raise Exception('手续费币种错误!')

                    if isinstance(comment, CollectionConfig):
                        CollectionConfig_safe(comment, request, formsets)
                        if comment.token_name == 'BTU':
                            print('BTU WithdrawConfig 创建行为!')
                            account_index = int(str(comment.pro_id_id))
                            address = add_addr(comment.token_name, account_index, 100000000)
                            CollectionFeeConfig.objects.create(pro_id=comment.pro_id, token_name='HRC20FEE',
                                                               address=address)



        except Exception as e:
            messages.error(request, f'{e}')
            print(f'save_related :{e}')
            raise Exception

        return super().save_related(request, form, formsets, change)

    def save_model(self, request, obj, form, change):
        """
        重写 客户保存
        :param request:
        :param obj:
        :param form:
        :param change:
        :return:
        """
        try:
            if change == False:

                select_rst = Project.objects.all().order_by('-pro_id').first()
                # 保证id不为0
                if select_rst is None:
                    obj.pro_id = 1
                    obj.bip44_account_index = obj.pro_id
                else:
                    obj.pro_id = select_rst.pro_id + 1
                    obj.bip44_account_index = obj.pro_id

                obj.create_time = datetime.now()
                # 创建apikey
                obj.api_key = hexlify(os.urandom(32)).decode('utf8')

                # 创建公私钥
                client_sign_key, client_verify_key = ed25519.create_keypair()
                server_sign_key, server_verify_key = ed25519.create_keypair()

                # 公私钥写入
                obj.client_sign_key = client_sign_key.to_ascii(encoding='hex').decode('utf8')
                obj.client_verify_key = client_verify_key.to_ascii(encoding="hex").decode('utf8')
                obj.server_sign_key = server_sign_key.to_ascii(encoding='hex').decode('utf8')
                obj.server_verify_key = server_verify_key.to_ascii(encoding="hex").decode('utf8')

                # redis写入
                rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME, decode_responses=True)
                url = obj.client_verify_key + ',' + str(obj.pro_id)
                rds.set(obj.api_key, url)

                msgbytes = hashlib.md5(str(obj.tel_no).encode('utf8')).digest()
                obj.password = hexlify(msgbytes).decode('latin1')
                print(obj.password)

            super().save_model(request, obj, form, change)
        except Exception as e:
            messages.error(request, f' 故障性错误: {e}')
            print(f'save_model 故障性错误: {e}')

@admin.register(UserOperationLog)
class UserOperationLogAdmin(ExportActionModelAdmin):
    """
    用户日志
    """

    search_fields = ('function_name', 'operation_time', 'pro_id__pro_name', 'operation_time')
    list_display = ('pro_id', 'operation_time', 'function_name', 'operation_type',
                    'update_before_value', 'last_after_value', 'operation_status')
    list_per_page = 18
    ordering = ('-operation_time',)
    list_select_related = False

    DEFAULT_FORMATS = [CSV, XLS, XLSX, ]
    formats = DEFAULT_FORMATS

    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def has_change_permission(self, request, obj=None):
        # 禁用保存按钮
        return False

@admin.register(UserAddressBalances)
class UserAddressBalancesAdmin(ExportActionModelAdmin):
    """
    用户地址资产
    """

    search_fields = ('address','token_name','pro_id__pro_name')
    list_display = ('address_rewrite', 'pro_id', 'token_name', 'balance', 'update_time')
    readonly_fields = ('address', 'pro_id', 'token_name', 'balance', 'update_time')
    list_per_page = 18
    ordering = ('-update_time',)
    list_select_related = False

    DEFAULT_FORMATS = [CSV,XLS,XLSX,]
    formats = DEFAULT_FORMATS


    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def has_change_permission(self, request, obj=None):
        # 禁用保存按钮
        return False

@admin.register(UserTokenBalances)
class UserTokenBalancesAdmin(ExportActionModelAdmin):
    """
    用户币种资产
    """

    search_fields = ('withdraw_address','token_name','pro_id__pro_name')
    list_display = ('pro_id', 'token_name', 'all_balance', 'withdraw_address', 'withdraw_balance', 'update_time')
    readonly_fields = ('pro_id', 'token_name', 'all_balance', 'withdraw_address', 'withdraw_balance', 'update_time')
    list_per_page = 18
    ordering = ('-update_time',)
    list_select_related = False

    DEFAULT_FORMATS = [CSV,XLS,XLSX,]
    formats = DEFAULT_FORMATS


    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def has_change_permission(self, request, obj=None):
        # 禁用保存按钮
        return False

@admin.register(Subaddress)
class SubaddressAdmin(ExportActionModelAdmin):
    """
    子地址
    """

    search_fields = ('address','token_name','pro_id__pro_name')
    list_display = ('address', 'pro_id', 'token_name', 'create_time',)
    readonly_fields = ('address', 'pro_id', 'token_name','account_index', 'address_index','create_time',)
    list_per_page = 18
    ordering = ('-create_time',)
    list_select_related = False


    DEFAULT_FORMATS = [CSV,XLS,XLSX,]
    formats = DEFAULT_FORMATS


    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def has_change_permission(self, request, obj=None):
        # 禁用保存按钮
        return False

@admin.register(Address)
class AddressAdmin(ExportActionModelAdmin):
    """
    地址管理
    """

    search_fields = ('token_name','update_time','pro_id__pro_name')
    list_display = ('pro_id', 'token_name', 'address_nums', 'uncharged_address_nums', 'update_time',)
    readonly_fields = ('pro_id', 'token_name', 'address_nums', 'uncharged_address_nums', 'update_time')
    list_per_page = 18
    ordering = ('-update_time',)
    list_select_related = False


    DEFAULT_FORMATS = [CSV,XLS,XLSX,]
    formats = DEFAULT_FORMATS


    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def has_change_permission(self, request, obj=None):
        # 禁用保存按钮
        return False

@admin.register(AddAddressOrder)
class AddAddressOrderAdmin(ExportActionModelAdmin):
    """
    地址审核
    """
    search_fields = ('pro_id__pro_name', 'token_name', 'order_id')

    list_display = ('pro_id',  'token_name', 'order_id', 'count', 'audit_status',
                    'generate_status','order_create_time', 'audit_complete_time',
                    'order_complete_time','order_status','remark','active_status')
    list_per_page = 18
    readonly_fields = ('pro_id',  'token_name', 'order_id', 'count', 'start_addr_index',
                    'end_addr_index', 'generate_status','apply_times',
                    'order_create_time', 'audit_complete_time', 'order_complete_time',
                    'order_status','active_status')


    list_select_related = False
    DEFAULT_FORMATS = [CSV, XLS, XLSX, ]
    formats = DEFAULT_FORMATS

    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        重写 更新状态 :通过和失败  只能保存一次
        :param request:
        :param object_id:
        :param form_url:
        :param extra_context:
        :return:
        """
        try:
            select_rst = AddAddressOrder.objects.filter(order_id=object_id).values()
            logger.info(f'select_rst : {select_rst}')
            extra_context = {}
            extra_context['show_save_and_continue'] = False

            if request.method == 'POST':

                # print('这是我的重写change_view  POST, 然后高点其他的事情。。。。。。')
                if select_rst[0]["audit_status"] == 'PASSED' or select_rst[0]["audit_status"] == 'REJECTED':
                    time.sleep(0.3)
                    extra_context['show_save'] = False
                    return False

                # # 判断是否是审核通过
                if request.POST["audit_status"] == 'PASSED':
                    update_rst = AddAddressOrder.objects.filter(order_id=object_id).first()
                    update_rst.audit_status = 'PASSED'
                    update_rst.save()

                    data ={"order_id":object_id, "audit_complete_time": int(datetime.now().timestamp()) }
                    logger.info(f'data : {data}')
                    send_order_id_to_msq(data)
                    logger.info(f'send_order_msq : success')

                if request.POST["audit_status"] == 'REJECTED':
                    update_rst = AddAddressOrder.objects.filter(order_id=object_id).first()
                    update_rst.order_complete_time = datetime.now()
                    update_rst.order_status = 'FAIL'
                    update_rst.save()


            if request.method == 'GET':
                if select_rst[0]["audit_status"] == 'PASSED' or select_rst[0]["audit_status"] == 'REJECTED':
                    extra_context['show_save'] = False

            return self.changeform_view(request, object_id, form_url, extra_context)
        except Exception as e:
            messages.error(request, f'{e}')
            print(f'change_view: {e}')

@admin.register(AssetDailyReport)
class AssetDailyReportAdmin(ExportActionModelAdmin):
    """
    日资产管理
    """

    search_fields = ('token_name','pro_id__pro_name', 'update_time')

    list_display = ('token_name', 'pro_id', 'deposit_amount', 'withdraw_amount',
                    'collectionRecords_amount','all_balance', 'update_time')
    readonly_fields = ('token_name', 'pro_id', 'deposit_amount', 'withdraw_amount',
                    'collectionRecords_amount','all_balance', 'update_time')
    list_per_page = 18
    ordering = ('-update_time',)
    list_select_related = False

    DEFAULT_FORMATS = [CSV,XLS,XLSX,]
    formats = DEFAULT_FORMATS


    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def has_change_permission(self, request, obj=None):
        # 禁用保存按钮
        return False


@admin.register(DjangoAdminLog)
class DjangoAdminLogAdmin(ExportActionModelAdmin):
    """
    管理员操作日志
    """

    search_fields = ('user','object_repr', 'object_id')

    list_display = ('action_time', 'object_id', 'object_repr', 'action_flag',
                    'change_message','user', )

    readonly_fields = ('action_time', 'object_id', 'object_repr', 'action_flag',
                    'change_message','user', 'content_type')
    list_per_page = 18
    ordering = ('-action_time',)
    list_select_related = False

    DEFAULT_FORMATS = [CSV,XLS,XLSX,]
    formats = DEFAULT_FORMATS


    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def has_change_permission(self, request, obj=None):
        # 禁用保存按钮
        return False



def find_model_index(name):
    count = 0
    for model, model_admin in admin.site._registry.items():
        if capfirst(model._meta.verbose_name_plural) == name:
            return count
        else:
            count += 1
    return count

def index_decorator(func):
    def inner(*args, **kwargs):
        templateresponse = func(*args, **kwargs)
        for app in templateresponse.context_data['app_list']:
            app['models'].sort(key=lambda x: find_model_index(x['name']))
        return templateresponse

    return inner

#重写管理台菜单顺序
admin.site.index = index_decorator(admin.site.index)
admin.site.app_index = index_decorator(admin.site.app_index)