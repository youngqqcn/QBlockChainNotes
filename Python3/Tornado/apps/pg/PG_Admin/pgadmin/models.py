#!/usr/bin/env python
#-*- coding:utf-8 -*-

#VersionNo: 1.0
#Author: fhh
#DateTime: 2020/5/12 17:36
#Describe:  实现django ORM转数据库 写入
#Function:
#Journal:

import re
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
# Create your models here.
from django.utils.html import format_html
from PG_Admin.settings import g_IS_MAINNET, DEBUG

if DEBUG == False:
    from bitcoin import SelectParams
    from bitcoin.wallet import CBitcoinAddress

    def is_valid_addr(address: str, token_name: str) -> bool:

        try:
            if token_name == 'HTDF' or token_name == 'BTU':
                return len(address) == 43 and  address.startswith('htdf1') and address.islower()
            elif token_name == 'ETH' or token_name == 'USDT':
                return len(address) == 42 and  address.startswith('0x') and  int(address, base=16)
            elif token_name == 'BTC':
                if g_IS_MAINNET:
                    SelectParams('mainnet')
                    addr = CBitcoinAddress(s = address)
                else:
                    SelectParams('testnet')
                    addr = CBitcoinAddress(s = address)

                assert addr is not None , 'addr is None'

                #如果没有抛异常直接返回即可
                return True
            else:
                raise RuntimeError(f"unknow token_name: {token_name}")
        except Exception as e:
            print(f'is_valid_addr() , {address} is invalid address, error:{e}')
            return False

        pass


token_name_choices = (
        ('HTDF', 'HTDF'),
        ('BTC', 'BTC'),
        ('ETH', 'ETH'),
        ('USDT', 'USDT'),
        ('BTU', 'BTU'),
)

class Project(models.Model):
    """
    客户创建
    """

    type_choices = (
        (0, '未激活'),
        (1, '正常 '),
        (2, '已冻结'),
        (3, '已禁用'),

    )

    pro_id = models.AutoField( null=False, primary_key=True, verbose_name='项目方ID')
    pro_name = models.CharField(max_length=50, verbose_name='项目方', null=False, unique=True)
    tel_no = models.CharField(max_length=11,  verbose_name='手机号', null=False)
    email = models.EmailField(max_length=20, null=False,verbose_name='邮箱')
    api_key = models.CharField(max_length=64, verbose_name='API_KEY', null=False)
    account_status = models.IntegerField(verbose_name='状态', choices=type_choices, null=False)
    bip44_account_index = models.IntegerField(verbose_name='BIP44的账户索引', help_text='BIP44的账户索引',  null=False)
    create_time = models.DateTimeField(verbose_name='创建时间', null=False)

    client_sign_key = models.CharField(max_length=100, verbose_name='客户端私钥', null=False, default='')
    client_verify_key = models.CharField(max_length=100, verbose_name='客户端公钥', null=False, default='')
    server_sign_key = models.CharField(max_length=100, verbose_name='服务端私钥', null=False, default='')
    server_verify_key = models.CharField(max_length=100, verbose_name='服务端公钥', null=False, default='')

    last_login = models.DateTimeField(verbose_name='上次登录时间', null=True)
    password = models.CharField(max_length=80, verbose_name='密码',
                                default='d14eda81b9d90dab222b77ce4ed9fa42',
                                null=False)


    def clean(self):
        if self.tel_no is not None:
            mobile = self.tel_no
            mobile_regex = r'^1[34578]\d{9}$'
            p = re.compile(mobile_regex)
            if p.match(mobile):
                return mobile
            else:
                raise ValidationError('Malformed phone number')
        if self.pro_name is not None:
            username = self.pro_name
            if username.isalnum():
                return username
            else:
                raise ValidationError('Malformed pro_name')


    class Meta:
        managed=False
        db_table = 'tb_project'
        verbose_name = "客户"
        verbose_name_plural = "客户管理"

    def __str__(self):
        return self.pro_name #+f"[id:{self.pro_id}]"

class Subaddress(models.Model):
    """
    子地址模块
    """

    address = models.CharField(max_length=100, verbose_name='子地址', primary_key=True , null=False)
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False)
    account_index = models.IntegerField( null=False, verbose_name='账户索引')
    address_index = models.IntegerField( null=False, verbose_name='地址索引')
    create_time = models.DateTimeField(verbose_name='添加时间', null=False)
    pro_id = models.ForeignKey(Project, verbose_name='项目方ID',on_delete=models.CASCADE, db_column="pro_id")

    class Meta:
        managed=False
        db_table = 'tb_address'
        verbose_name = "子地址"
        verbose_name_plural = "子地址"

    def __str__(self):
        return self.token_name

class Address(models.Model):
    """
    地址管理模块
    """

    id = models.AutoField(primary_key=True)
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False)
    address_nums = models.IntegerField( null=False, verbose_name='地址总数', default=0)
    uncharged_address_nums = models.IntegerField( null=False, verbose_name='未充值地址数', default=0)
    update_time = models.DateTimeField(verbose_name='最后更新时间', auto_now=True, null=False)
    pro_id = models.ForeignKey(Project, verbose_name='项目方ID',on_delete=models.CASCADE, db_column="pro_id")

    class Meta:
        managed=False
        unique_together = (("token_name", "pro_id"),)
        db_table = 'tb_address_admin'
        verbose_name = "地址管理"
        verbose_name_plural = "地址管理"

    def __str__(self):
        return self.token_name


class AddAddressOrder(models.Model):
    """
    地址审核模块
    """

    audit_status_choices = (
        ('PENDING', '待审核'),
        ('REJECTED', '已拒绝'),
        ('PASSED', '已通过'),
    )
    generate_status_choices = (
        ('NOTYET', '未生成'),
        ('SUCCESS', '生成完成'),
    )
    order_status_choices = (
        ('PROCESSING', '处理中'),
        ('SUCCESS', '成功'),
        ('FAIL', '失败'),
    )

    active_status_choices = (
        ('NO', '未启用'),
        ('YES', '已启用'),
    )

    order_id = models.CharField(max_length=30, verbose_name='订单号', primary_key=True, null=False)
    token_name = models.CharField(max_length=20, verbose_name='币种',null=False)
    apply_times = models.IntegerField(verbose_name='申请次数', null=False)
    count = models.IntegerField( verbose_name='申请数量', null=False)
    start_addr_index = models.IntegerField(verbose_name='本次生成,起始地址索引', null=False)
    end_addr_index = models.IntegerField(verbose_name='本次生成,结束地址索引', null=False)
    audit_status = models.CharField(max_length=20, verbose_name='审核状态', choices=audit_status_choices)
    generate_status = models.CharField(max_length=20, verbose_name='地址生成状态', choices=generate_status_choices)
    order_create_time = models.DateTimeField(verbose_name='订单生成时间', null=True)
    audit_complete_time = models.DateTimeField(verbose_name='审核完成时间', auto_now=True)
    order_complete_time = models.DateTimeField(verbose_name='订单完成时间', null=True)
    order_status = models.CharField(max_length=20, verbose_name='订单状态',choices=order_status_choices, null=False)
    remark = models.CharField(max_length=250, verbose_name='备注(remark)', null=True)
    #注意:  地址生成后需要, 刷新到redis地址池中, 才能进行充币监控   by yqq
    active_status = models.CharField(max_length=10, verbose_name='启用状态', choices=active_status_choices, null=False)
    pro_id = models.ForeignKey(Project, null=False, verbose_name='项目方ID', on_delete=models.CASCADE, db_column="pro_id")


    class Meta:
        managed=False
        db_table = 'tb_add_address_order'
        verbose_name = "审核"
        verbose_name_plural = "地址审核"

    def __str__(self):
        return self.token_name


class WithdrawConfig(models.Model):
    """
    提币配置表
    """

    id = models.AutoField(primary_key=True)
    pro_id = models.ForeignKey(Project,on_delete=models.CASCADE, db_column="pro_id",verbose_name="项目方ID")
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False, choices=token_name_choices, default=token_name_choices)
    address = models.CharField(max_length=100, verbose_name='出币地址', null=False)
    min_amount = models.DecimalField(max_digits=28, decimal_places=8, verbose_name='最小提币金额', null=False)  # 小于此金额, 不进行提币
    max_amount = models.DecimalField(max_digits=28, decimal_places=8, verbose_name='最大提币金额', null=False)  # 大于此金额, 不进行提币
    # 出币地址的余额小于此值时，发送短信进行通知
    balance_threshold_to_sms = models.DecimalField(max_digits=28, decimal_places=8, verbose_name='短信通知阈值' , null=False)
    is_open = models.BooleanField(verbose_name='提币通道开启状态',null=False, default=True)


    def clean(self):
        try:
            if self.min_amount < 0.00001 or self.min_amount <= 0 or self.max_amount <= 0 or self.balance_threshold_to_sms < 0 :
                raise ValidationError('The amount does not match')

        except Exception as e:
            raise ValidationError(e)

    class Meta:
        unique_together = (("token_name", "pro_id"),)
        managed = False
        db_table = 'tb_withdraw_config'
        verbose_name = "提币配置"
        verbose_name_plural = "提币配置"

    def __str__(self):
        return ''


class CollectionRecords(models.Model):
    """
    归集记录
    """
    collection_type_choices = (
        ('AUTO', '自动归集'),
        ('MANUAL', '手动归集'),
        ('FEE', '补手续费'),
    )

    transaction_status_choices = (
        ('NOTYET', '未汇出'),
        ('PENDING', '已汇出'),
        ('FAIL', '交易失败'),
        ('SUCCESS', '交易成功')
    )

    id = models.AutoField(primary_key=True)
    pro_id = models.ForeignKey(Project,on_delete=models.CASCADE, db_column="pro_id", verbose_name="项目方ID")
    tx_hash = models.CharField(max_length=100, verbose_name='交易hash', null=False)
    complete_time = models.DateTimeField(verbose_name='归集完成时间' , null=True)
    amount = models.DecimalField(max_digits=28, decimal_places=8, verbose_name='归集金额', null=False)
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False)
    from_address = models.CharField(max_length=100, verbose_name='源地址', null=False)
    to_address = models.CharField(max_length=100, verbose_name='目的地址', null=False)
    block_height =  models.BigIntegerField(null=False, verbose_name='区块高度')
    block_time = models.DateTimeField(verbose_name='区块时间',null=True)
    tx_confirmations = models.IntegerField(null=False, verbose_name='区块确认数', default=0)
    transaction_status  = models.CharField(max_length=20, verbose_name='交易状态',choices=transaction_status_choices, null=False)
    collection_type =models.CharField(max_length=20, verbose_name='操作类型', choices=collection_type_choices)


    class Meta:
        managed = False
        db_table = 'tb_collection_records'
        verbose_name = "归集记录"
        verbose_name_plural = "归集记录"

    def __str__(self):
        return self.token_name

class Deposit(models.Model):
    """
    充币表
    """
    id = models.AutoField(primary_key=True)
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False,)
    tx_hash = models.CharField(max_length=100, verbose_name='交易hash',null=False)
    from_addr = models.CharField(max_length=100,null=False, verbose_name='源地址')
    to_addr = models.CharField(max_length=100,null=False, verbose_name='目的地址')
    memo = models.CharField(max_length=100, verbose_name='转账备注(memo)', null=True)
    amount = models.DecimalField(max_digits=28,decimal_places=8,null=False, verbose_name='充币金额')
    block_height = models.BigIntegerField(null=False, verbose_name='区块高度')
    block_time = models.DateTimeField(verbose_name='区块时间',null=False)
    notify_status = models.IntegerField(null=False, verbose_name='通知状态',default=0)
    tx_confirmations = models.IntegerField(null=False, verbose_name='区块确认数')
    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id",verbose_name="项目方ID")

    class Meta:
        managed = False
        unique_together = [("pro_id", "token_name", "tx_hash", "to_addr")]
        index_together = [("pro_id","token_name","block_height"),("pro_id","token_name","block_time")]
        db_table = 'tb_deposit'
        verbose_name = "充币"
        verbose_name_plural = "充币记录"

    def __str__(self):
        return self.token_name




class WithdrawOrder(models.Model):
    """
    提币表
    """

    order_status_choices = (
        ('PROCESSING', '处理中'),
        ('SUCCESS', '成功'),
        ('FAIL', '失败'),
    )

    transaction_status_choices = (
        ('NOTYET', '未汇出'),
        ('PENDING', '已汇出'),
        ('FAIL', '交易失败'),
        ('SUCCESS', '交易成功')
    )

    notify_status_choices = (
        ("NOTYET", "尚未通知"),
        ("FIRSTSUCCESS", "第一次通知成功"),
        ("FIRSTFAIL", "第一次通知失败"),
        ("SECONDSUCCESS", "第二次通知成功"),
        ("SECONDFAIL", "第二次通知失败")
    )

    serial_id = models.CharField(max_length=30, verbose_name='流水号' ,null=False, primary_key=True)
    order_id = models.CharField(max_length=30, verbose_name='订单号' ,null=False)
    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id",verbose_name='项目方id')
    token_name = models.CharField(max_length=20, verbose_name='币种' ,null=False)
    from_addr = models.CharField(max_length=100, verbose_name='源地址' ,null=False)
    to_addr = models.CharField(max_length=100, verbose_name='目的地址', null=False)
    memo = models.CharField(max_length=100, verbose_name='交易备注(memo)', null=True)
    amount = models.DecimalField(max_digits=28,decimal_places=8,null=False, verbose_name='金额')
    block_height = models.IntegerField(null=False, verbose_name='区块高度', default=0)
    tx_hash = models.CharField(max_length=100, verbose_name='交易hash', null=False)
    callback_url = models.CharField(max_length=250, verbose_name='回调地址', null=False)
    tx_confirmations = models.IntegerField(null=False, verbose_name='区块确认数')
    order_status = models.CharField(max_length=20, verbose_name='订单状态',choices=order_status_choices, null=False)
    transaction_status = models.CharField(max_length=20, verbose_name='交易状态',null=False ,choices=transaction_status_choices)
    notify_status = models.CharField(max_length=20, verbose_name='通知状态(主动通知)',null=False, choices=notify_status_choices)
    notify_times = models.IntegerField(null=False, verbose_name='通知次数', default=0)
    block_time = models.DateTimeField(verbose_name='区块时间',null=True)
    complete_time = models.DateTimeField(verbose_name='完成时间',null=True)
    remark = models.CharField(max_length=250, verbose_name='备注(remark)', null=True)


    class Meta:
        managed = False
        db_table = 'tb_withdraw_order'
        verbose_name = "提币"
        verbose_name_plural = "提币记录"

    def __str__(self):
        return self.token_name

class CollectionConfig(models.Model):
    """
    #归集配置表
    """

    id = models.AutoField(primary_key=True)
    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id",verbose_name="项目方ID")
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False,choices=token_name_choices, default=token_name_choices)
    collection_dst_addr = models.CharField(max_length=100, verbose_name='归集目的地址', null=False)
    min_amount_to_collect = models.DecimalField(max_digits=28,decimal_places=8,null=False, verbose_name='最小归集金额')  #小于此金额, 不进行归集

    def clean(self):
        try:
            if DEBUG == False:
                if not is_valid_addr(token_name=self.token_name, address=self.collection_dst_addr):
                    raise ValidationError(f'token name {self.token_name} address format error or lenght error')

            if self.min_amount_to_collect < 0.0001 or self.min_amount_to_collect <= 0:
                raise ValidationError('The amount does not match')

        except Exception as e:
            raise ValidationError(e)



    class Meta:
        managed=False
        unique_together = (("pro_id", "token_name"),)
        db_table = 'tb_collection_config'
        verbose_name = "归集配置"
        verbose_name_plural = "归集配置"

    def __str__(self):
        return ''

class CollectionFeeConfig(models.Model):
    """
    手续费配置表
    """
    token_name_choices = {
        ('ERC20FEE', 'ERC20'),
        ('HRC20FEE', 'HRC20'),
    }

    id = models.AutoField(primary_key=True)
    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id",verbose_name="项目方ID")
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False,choices=token_name_choices, default=token_name_choices)
    address = models.CharField(max_length=100, verbose_name='手续费地址', null=False)



    class Meta:
        managed=False
        unique_together = (("token_name", "pro_id"),)
        db_table = 'tb_collection_fee_config'
        verbose_name = "手续费"
        verbose_name_plural = "手续费配置 （当ERC20及HRC20归集时，被归集的主链币余额不足时，该地址用来补手续费）"

    def __str__(self):
        return ''

class UserAddressBalances(models.Model):
    """
    用户地址资产
    """

    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id",verbose_name="项目方ID")
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False,choices=token_name_choices, default=token_name_choices)
    address = models.CharField(max_length=100, verbose_name='地址', null=False)
    balance = models.DecimalField(max_digits=28,decimal_places=8,null=False, verbose_name='充币金额')
    update_time = models.DateTimeField(verbose_name='最后更新时间',null=False, primary_key=True)

    def address_rewrite(self):
        return format_html(
            f'<a style="font-weight: 500; color: black;">{self.address}</a>',
        )
    address_rewrite.short_description = '地址'

    class Meta:
        managed=False
        unique_together = (("token_name", "address"),)
        db_table = 'tb_active_address_balances'
        verbose_name = "用户地址资产"
        verbose_name_plural = "用户地址资产"

    def __str__(self):
        return ''


class UserTokenBalances(models.Model):
    """
    用户币种资产
    """

    id = models.AutoField(primary_key=True)
    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id",verbose_name="项目方ID")
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False,choices=token_name_choices, default=token_name_choices)
    all_balance = models.DecimalField(max_digits=28, decimal_places=8, null=False, verbose_name='数量')
    withdraw_address = models.CharField(max_length=100, verbose_name='提币地址', null=False)
    withdraw_balance = models.DecimalField(max_digits=28,decimal_places=8,null=False, verbose_name='提币地址余额')
    update_time = models.DateTimeField(verbose_name='最后更新时间', auto_now=True, null=False)

    class Meta:
        managed=False
        unique_together = (("pro_id", "token_name"),)
        db_table = 'tb_user_token_balances'
        verbose_name = "用户币种资产"
        verbose_name_plural = "用户币种资产"

    def __str__(self):
        return ''

class AssetDailyReport(models.Model):
    """
    资产日报表
    """

    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id",verbose_name="项目方ID")
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False,choices=token_name_choices, default=token_name_choices)
    deposit_amount = models.DecimalField(max_digits=28,decimal_places=8,null=False, verbose_name='当日充币金额')
    withdraw_amount = models.DecimalField(max_digits=28,decimal_places=8,null=False, verbose_name='当日提币金额')
    collectionRecords_amount = models.DecimalField(max_digits=28,decimal_places=8,null=False, verbose_name='当日归集金额')
    all_balance = models.DecimalField(max_digits=28,decimal_places=8,null=False, verbose_name='当前子地址币总资产')
    update_time = models.DateTimeField(verbose_name='最后更新时间', auto_now=True, null=False)

    class Meta:
        managed=False
        db_table = 'tb_asset_daily_report'
        verbose_name = "日资产报表"
        verbose_name_plural = "日资产报表"

    def __str__(self):
        return ''


class UserOperationLog(models.Model):
    """
    用户操作日志
    """

    operation_type_choices = (
        ('CREAT', '新增'),
        ('QUERY', '查询'),
        ('UPDATE', '修改'),
        ('DELETE', '删除'),
        ('LOGIN', '登录'),
        ('LOGIN_NO_GCODE', '登录没有验证码'),
    )

    operation_status_choices = (
        ('SUCCESS', '成功'),
        ('FAIL', '失败'),
    )

    id = models.AutoField(primary_key=True)
    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id", verbose_name="项目方ID")
    operation_time = models.DateTimeField(verbose_name='操作时间', auto_now=True, null=False)
    function_name = models.CharField(max_length=50, verbose_name='功能名称', null=False)
    operation_type = models.CharField(max_length=20, verbose_name='操作类型', null=False, choices=operation_type_choices)
    update_before_value = models.CharField(max_length=100, verbose_name='修改前的值', null=False, default='')
    last_after_value = models.CharField(max_length=100, verbose_name='修改后的值', null=False, default='')
    operation_status = models.CharField(max_length=20, verbose_name='操作状态',choices=operation_status_choices, null=False)

    class Meta:
        managed=False
        db_table = 'tb_user_operation_log'
        verbose_name = "用户操作日志"
        verbose_name_plural = "用户操作日志"

    def __str__(self):
        return ''


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)

class DjangoAdminLog(models.Model):
    """
    管理员操作日志
    """
    action_time = models.DateTimeField(help_text='操作时间', verbose_name='操作时间')
    object_id = models.TextField(blank=True, null=True, help_text='被操作用户ID', verbose_name='被操作用户ID')
    object_repr = models.CharField(max_length=200, help_text='被操作用户名', verbose_name='被操作用户名')
    action_flag = models.PositiveSmallIntegerField(help_text='操作状态', verbose_name='操作状态')
    change_message = models.TextField(help_text='操作内容', verbose_name='操作内容')
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True, help_text='操作功能', verbose_name='操作功能')
    user = models.ForeignKey(User, models.DO_NOTHING, help_text='操作者', verbose_name='操作者')

    class Meta:
        managed = False
        db_table = 'django_admin_log'
        verbose_name = "管理员操作日志"
        verbose_name_plural = "管理员操作日志"

class GoogleCode(models.Model):
    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id", verbose_name="项目方ID")
    key = models.CharField(max_length=50, verbose_name='密钥', null=False)
    logined = models.IntegerField(verbose_name='是否已登录过(项目方)', null=True)
    is_superuser = models.IntegerField(verbose_name='是否是管理员', null=True)

    class Meta:
        managed = False
        db_table = 'tb_google_code'

