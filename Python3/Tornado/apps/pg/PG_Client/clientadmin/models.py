import re
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import PermissionsMixin, UserManager

# Create your models here.
from django.utils.functional import cached_property

token_name_choices = (
        ('HTDF', 'HTDF'),
        ('BTC', 'BTC'),
        ('ETH', 'ETH'),
        ('USDT', 'USDT'),
    )

class Project(AbstractBaseUser, PermissionsMixin):
    #AbstractBaseUser, PermissionsMixin
    """
    客户创建
    """

    type_choices = (
        (0, '未激活'),
        (1, '正常 '),
        (2, '已冻结'),
        (3, '已禁用'),
    )

    pro_id = models.AutoField(null=False, primary_key=True, verbose_name='pro_id')
    pro_name = models.CharField(max_length=50, verbose_name='项目方', null=False, unique=True)
    tel_no = models.CharField(max_length=11,  verbose_name='username', null=False)
    email = models.EmailField(max_length=20, null=False,verbose_name='邮箱')
    api_key = models.CharField(max_length=64, verbose_name='API_KEY', null=False)
    account_status = models.IntegerField(verbose_name='状态', choices=type_choices, null=False)
    bip44_account_index = models.IntegerField(verbose_name='BIP44的账户索引', help_text='BIP44的账户索引',  null=False)
    create_time = models.DateTimeField(verbose_name='创建时间', null=False)

    client_sign_key = models.CharField(max_length=100, verbose_name='客户端私钥', null=False, default='')
    client_verify_key = models.CharField(max_length=100, verbose_name='客户端公钥', null=False, default='')
    server_sign_key = models.CharField(max_length=100, verbose_name='服务端私钥', null=False, default='')
    server_verify_key = models.CharField(max_length=100, verbose_name='服务端公钥', null=False, default='')


    #TODO:不需要父类带来的各个字段
    username = None
    is_superuser = None
    groups = None
    user_permissions = None

    USERNAME_FIELD = 'pro_id'
    objects = UserManager()

    last_login = models.DateTimeField( verbose_name='上次登录时间', null=True)
    password = models.CharField(max_length=80, verbose_name='密码',help_text='登录密码',
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
        managed=True
        db_table = 'tb_project'
        verbose_name = "客户"
        verbose_name_plural = "客户管理"

    def __str__(self):
        return self.pro_name

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
        managed=True
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
        managed=True
        unique_together = (("token_name", "pro_id"),)
        db_table = 'tb_address_admin'
        verbose_name = "地址管理"
        verbose_name_plural = "地址管理"

    def __str__(self):
        return self.token_name


class WithdrawConfig(models.Model):
    """
    提币配置表
    """

    id = models.AutoField(primary_key=True, )
    pro_id = models.ForeignKey(Project,on_delete=models.CASCADE, db_column="pro_id",verbose_name="项目方ID")
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False, choices=token_name_choices, default=token_name_choices, help_text='币种')
    address = models.CharField(max_length=100, verbose_name='出币地址', null=False, help_text='出币地址')
    min_amount = models.DecimalField(max_digits=28, decimal_places=8, verbose_name='最小提币金额', null=False, help_text='最小提币金额')  # 小于此金额, 不进行提币
    max_amount = models.DecimalField(max_digits=28, decimal_places=8, verbose_name='最大提币金额', null=False, help_text='最大提币金额')  # 大于此金额, 不进行提币
    # 出币地址的余额小于此值时，发送短信进行通知
    balance_threshold_to_sms = models.DecimalField(max_digits=28, decimal_places=8, verbose_name='短信通知阈值' , null=False, help_text='短信通知阈值')
    is_open = models.BooleanField(verbose_name='提币通道开启状态',null=False, default=True)

    def clean(self):
        try:
            if self.min_amount < 0.00001 or self.min_amount <= 0 or self.max_amount <= 0 or self.balance_threshold_to_sms < 0 :
                raise ValidationError('The amount does not match')

        except Exception as e:
            raise ValidationError(e)

    class Meta:
        unique_together = (("token_name", "pro_id"),)
        managed = True
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
        managed = True
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
        managed = True
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
    complete_time = models.DateTimeField( verbose_name='完成时间',null=True)
    remark = models.CharField(max_length=250, verbose_name='备注(remark)', null=True)


    class Meta:
        managed = True
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
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False,choices=token_name_choices, default=token_name_choices, help_text='币种')
    collection_dst_addr = models.CharField(max_length=100, verbose_name='归集目的地址', null=False, help_text='归集目的地址')
    min_amount_to_collect = models.DecimalField(max_digits=28,decimal_places=8,null=False, verbose_name='最小归集金额', help_text='最小归集金额')  #小于此金额, 不进行归集

    class Meta:
        managed=True
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
    }

    id = models.AutoField(primary_key=True)
    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id",verbose_name="项目方ID")
    token_name = models.CharField(max_length=20, verbose_name='币种', null=False,choices=token_name_choices, default=token_name_choices)
    address = models.CharField(max_length=100, verbose_name='手续费地址', null=False)



    class Meta:
        managed=True
        unique_together = (("token_name", "pro_id"),)
        db_table = 'tb_collection_fee_config'
        verbose_name = "手续费"
        verbose_name_plural = "手续费配置 ( 当USDT归集时,被归集ETH的余额不够，该地址用来补手续费 )"

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

    class Meta:
        managed=True
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
        managed=True
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
    update_time = models.DateTimeField( verbose_name='最后更新时间',auto_now=True, null=False)

    class Meta:
        managed=True
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
    operation_time = models.DateTimeField( verbose_name='操作时间', auto_now=True, null=False)
    function_name = models.CharField(max_length=50, verbose_name='功能名称', null=False)
    operation_type = models.CharField(max_length=20, verbose_name='操作类型', null=False, choices=operation_type_choices)
    update_before_value = models.CharField(max_length=100, verbose_name='修改前的值', null=False, default='')
    last_after_value = models.CharField(max_length=100, verbose_name='修改后的值', null=False, default='')
    operation_status = models.CharField(max_length=20, verbose_name='操作状态',choices=operation_status_choices, null=False)

    class Meta:
        managed=True
        db_table = 'tb_user_operation_log'
        verbose_name = "用户操作日志"
        verbose_name_plural = "用户操作日志"

    def __str__(self):
        return ''

class GoogleCode(models.Model):
    pro_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column="pro_id", verbose_name="项目方ID")
    key = models.CharField(max_length=50, verbose_name='密钥', null=False)
    logined = models.IntegerField(verbose_name='是否已登录过(项目方)', null=True)
    is_superuser = models.IntegerField(verbose_name='是否是管理员', null=True)

    class Meta:
        managed = False
        db_table = 'tb_google_code'