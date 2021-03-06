# Generated by Django 3.0.7 on 2020-07-15 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('pro_id', models.AutoField(primary_key=True, serialize=False, verbose_name='pro_id')),
                ('pro_name', models.CharField(max_length=50, unique=True, verbose_name='项目方')),
                ('tel_no', models.CharField(max_length=11, verbose_name='username')),
                ('email', models.EmailField(max_length=20, verbose_name='邮箱')),
                ('api_key', models.CharField(max_length=64, verbose_name='API_KEY')),
                ('account_status', models.IntegerField(choices=[(0, '未激活'), (1, '正常 '), (2, '已冻结'), (3, '已禁用')], verbose_name='状态')),
                ('bip44_account_index', models.IntegerField(help_text='BIP44的账户索引', verbose_name='BIP44的账户索引')),
                ('create_time', models.DateTimeField(max_length=0, verbose_name='创建时间')),
                ('client_sign_key', models.CharField(default='', max_length=100, verbose_name='客户端私钥')),
                ('client_verify_key', models.CharField(default='', max_length=100, verbose_name='客户端公钥')),
                ('server_sign_key', models.CharField(default='', max_length=100, verbose_name='服务端私钥')),
                ('server_verify_key', models.CharField(default='', max_length=100, verbose_name='服务端公钥')),
                ('last_login', models.DateTimeField(null=True, verbose_name='上次登录时间')),
                ('password', models.CharField(default='pbkdf2_sha256$180000$IMjsmgBFePIO$lTULfQJfOnZFpDH4y9+81uWBMb05fqBf8qAvH8Mexsk=', help_text='登录密码', max_length=80, verbose_name='密码')),
            ],
            options={
                'verbose_name': '客户',
                'verbose_name_plural': '客户管理',
                'db_table': 'tb_project',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='WithdrawOrder',
            fields=[
                ('serial_id', models.CharField(max_length=30, primary_key=True, serialize=False, verbose_name='流水号')),
                ('order_id', models.CharField(max_length=30, verbose_name='订单号')),
                ('token_name', models.CharField(max_length=20, verbose_name='币种')),
                ('from_addr', models.CharField(max_length=100, verbose_name='源地址')),
                ('to_addr', models.CharField(max_length=100, verbose_name='目的地址')),
                ('memo', models.CharField(max_length=100, null=True, verbose_name='交易备注(memo)')),
                ('amount', models.DecimalField(decimal_places=8, max_digits=28, verbose_name='金额')),
                ('block_height', models.IntegerField(default=0, verbose_name='区块高度')),
                ('tx_hash', models.CharField(max_length=100, verbose_name='交易hash')),
                ('callback_url', models.CharField(max_length=250, verbose_name='回调地址')),
                ('tx_confirmations', models.IntegerField(verbose_name='区块确认数')),
                ('order_status', models.CharField(choices=[('PROCESSING', '处理中'), ('SUCCESS', '成功'), ('FAIL', '失败')], max_length=20, verbose_name='订单状态')),
                ('transaction_status', models.CharField(choices=[('NOTYET', '未汇出'), ('PENDING', '已汇出'), ('FAIL', '交易失败'), ('SUCCESS', '交易成功')], max_length=20, verbose_name='交易状态')),
                ('notify_status', models.CharField(choices=[('NOTYET', '尚未通知'), ('FIRSTSUCCESS', '第一次通知成功'), ('FIRSTFAIL', '第一次通知失败'), ('SECONDSUCCESS', '第二次通知成功'), ('SECONDFAIL', '第二次通知失败')], max_length=20, verbose_name='通知状态(主动通知)')),
                ('notify_times', models.IntegerField(default=0, verbose_name='通知次数')),
                ('block_time', models.DateTimeField(max_length=0, null=True, verbose_name='区块时间')),
                ('complete_time', models.DateTimeField(max_length=0, null=True, verbose_name='完成时间')),
                ('remark', models.CharField(max_length=250, null=True, verbose_name='备注(remark)')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方id')),
            ],
            options={
                'verbose_name': '提币',
                'verbose_name_plural': '提币记录',
                'db_table': 'tb_withdraw_order',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='UserOperationLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('operation_time', models.DateTimeField(max_length=0, verbose_name='操作时间')),
                ('function_name', models.CharField(max_length=50, verbose_name='功能名称')),
                ('operation_type', models.CharField(choices=[('CREAT', '新增'), ('QUERY', '查询'), ('UPDATE', '修改'), ('DELETE', '删除'), ('LOGIN', '登录'), ('LOGIN_NO_GCODE', '登录没有验证码')], max_length=20, verbose_name='操作类型')),
                ('update_before_value', models.CharField(default='', max_length=100, verbose_name='修改前的值')),
                ('last_after_value', models.CharField(default='', max_length=100, verbose_name='修改后的值')),
                ('operation_status', models.CharField(choices=[('SUCCESS', '成功'), ('FAIL', '失败')], max_length=20, verbose_name='操作状态')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '用户操作日志',
                'verbose_name_plural': '用户操作日志',
                'db_table': 'tb_user_operation_log',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Subaddress',
            fields=[
                ('address', models.CharField(max_length=100, primary_key=True, serialize=False, verbose_name='子地址')),
                ('token_name', models.CharField(max_length=20, verbose_name='币种')),
                ('account_index', models.IntegerField(verbose_name='账户索引')),
                ('address_index', models.IntegerField(verbose_name='地址索引')),
                ('create_time', models.DateTimeField(max_length=0, verbose_name='添加时间')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '子地址',
                'verbose_name_plural': '子地址',
                'db_table': 'tb_address',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CollectionRecords',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tx_hash', models.CharField(max_length=100, verbose_name='交易hash')),
                ('complete_time', models.DateTimeField(max_length=0, null=True, verbose_name='归集完成时间')),
                ('amount', models.DecimalField(decimal_places=8, max_digits=28, verbose_name='归集金额')),
                ('token_name', models.CharField(max_length=20, verbose_name='币种')),
                ('from_address', models.CharField(max_length=100, verbose_name='源地址')),
                ('to_address', models.CharField(max_length=100, verbose_name='目的地址')),
                ('block_height', models.BigIntegerField(verbose_name='区块高度')),
                ('block_time', models.DateTimeField(max_length=0, null=True, verbose_name='区块时间')),
                ('tx_confirmations', models.IntegerField(default=0, verbose_name='区块确认数')),
                ('transaction_status', models.CharField(choices=[('NOTYET', '未汇出'), ('PENDING', '已汇出'), ('FAIL', '交易失败'), ('SUCCESS', '交易成功')], max_length=20, verbose_name='交易状态')),
                ('collection_type', models.CharField(choices=[('AUTO', '自动归集'), ('MANUAL', '手动归集'), ('FEE', '补手续费')], max_length=20, verbose_name='操作类型')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '归集记录',
                'verbose_name_plural': '归集记录',
                'db_table': 'tb_collection_records',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AssetDailyReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_name', models.CharField(choices=[('HTDF', 'HTDF'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('USDT', 'USDT')], default=(('HTDF', 'HTDF'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('USDT', 'USDT')), max_length=20, verbose_name='币种')),
                ('deposit_amount', models.DecimalField(decimal_places=8, max_digits=28, verbose_name='当日充币金额')),
                ('withdraw_amount', models.DecimalField(decimal_places=8, max_digits=28, verbose_name='当日提币金额')),
                ('collectionRecords_amount', models.DecimalField(decimal_places=8, max_digits=28, verbose_name='当日归集金额')),
                ('all_balance', models.DecimalField(decimal_places=8, max_digits=28, verbose_name='当前子地址币总资产')),
                ('update_time', models.DateTimeField(max_length=0, verbose_name='最后更新时间')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '日资产报表',
                'verbose_name_plural': '日资产报表',
                'db_table': 'tb_asset_daily_report',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='WithdrawConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('token_name', models.CharField(choices=[('HTDF', 'HTDF'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('USDT', 'USDT')], default=(('HTDF', 'HTDF'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('USDT', 'USDT')), help_text='币种', max_length=20, verbose_name='币种')),
                ('address', models.CharField(help_text='出币地址', max_length=100, verbose_name='出币地址')),
                ('min_amount', models.DecimalField(decimal_places=8, help_text='最小提币金额', max_digits=28, verbose_name='最小提币金额')),
                ('max_amount', models.DecimalField(decimal_places=8, help_text='最大提币金额', max_digits=28, verbose_name='最大提币金额')),
                ('balance_threshold_to_sms', models.DecimalField(decimal_places=8, help_text='短信通知阈值', max_digits=28, verbose_name='短信通知阈值')),
                ('is_open', models.BooleanField(default=True, verbose_name='提币通道开启状态')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '提币配置',
                'verbose_name_plural': '提币配置',
                'db_table': 'tb_withdraw_config',
                'managed': True,
                'unique_together': {('token_name', 'pro_id')},
            },
        ),
        migrations.CreateModel(
            name='UserTokenBalances',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('token_name', models.CharField(choices=[('HTDF', 'HTDF'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('USDT', 'USDT')], default=(('HTDF', 'HTDF'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('USDT', 'USDT')), max_length=20, verbose_name='币种')),
                ('all_balance', models.DecimalField(decimal_places=8, max_digits=28, verbose_name='数量')),
                ('withdraw_address', models.CharField(max_length=100, verbose_name='提币地址')),
                ('withdraw_balance', models.DecimalField(decimal_places=8, max_digits=28, verbose_name='提币地址余额')),
                ('update_time', models.DateTimeField(max_length=0, verbose_name='最后更新时间')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '用户币种资产',
                'verbose_name_plural': '用户币种资产',
                'db_table': 'tb_user_token_balances',
                'managed': True,
                'unique_together': {('pro_id', 'token_name')},
            },
        ),
        migrations.CreateModel(
            name='UserAddressBalances',
            fields=[
                ('token_name', models.CharField(choices=[('HTDF', 'HTDF'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('USDT', 'USDT')], default=(('HTDF', 'HTDF'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('USDT', 'USDT')), max_length=20, verbose_name='币种')),
                ('address', models.CharField(max_length=100, verbose_name='地址')),
                ('balance', models.DecimalField(decimal_places=8, max_digits=28, verbose_name='充币金额')),
                ('update_time', models.DateTimeField(max_length=0, primary_key=True, serialize=False, verbose_name='最后更新时间')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '用户地址资产',
                'verbose_name_plural': '用户地址资产',
                'db_table': 'tb_active_address_balances',
                'managed': True,
                'unique_together': {('token_name', 'address')},
            },
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('token_name', models.CharField(max_length=20, verbose_name='币种')),
                ('tx_hash', models.CharField(max_length=100, verbose_name='交易hash')),
                ('from_addr', models.CharField(max_length=100, verbose_name='源地址')),
                ('to_addr', models.CharField(max_length=100, verbose_name='目的地址')),
                ('memo', models.CharField(max_length=100, null=True, verbose_name='转账备注(memo)')),
                ('amount', models.DecimalField(decimal_places=8, max_digits=28, verbose_name='充币金额')),
                ('block_height', models.BigIntegerField(verbose_name='区块高度')),
                ('block_time', models.DateTimeField(max_length=0, verbose_name='区块时间')),
                ('notify_status', models.IntegerField(default=0, verbose_name='通知状态')),
                ('tx_confirmations', models.IntegerField(verbose_name='区块确认数')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '充币',
                'verbose_name_plural': '充币记录',
                'db_table': 'tb_deposit',
                'managed': True,
                'unique_together': {('pro_id', 'token_name', 'tx_hash', 'to_addr')},
                'index_together': {('pro_id', 'token_name', 'block_time'), ('pro_id', 'token_name', 'block_height')},
            },
        ),
        migrations.CreateModel(
            name='CollectionFeeConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('token_name', models.CharField(choices=[('ERC20FEE', 'ERC20')], default={('ERC20FEE', 'ERC20')}, max_length=20, verbose_name='币种')),
                ('address', models.CharField(max_length=100, verbose_name='手续费地址')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '手续费',
                'verbose_name_plural': '手续费配置 ( 当USDT归集时,被归集ETH的余额不够，该地址用来补手续费 )',
                'db_table': 'tb_collection_fee_config',
                'managed': True,
                'unique_together': {('token_name', 'pro_id')},
            },
        ),
        migrations.CreateModel(
            name='CollectionConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('token_name', models.CharField(choices=[('HTDF', 'HTDF'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('USDT', 'USDT')], default=(('HTDF', 'HTDF'), ('BTC', 'BTC'), ('ETH', 'ETH'), ('USDT', 'USDT')), help_text='币种', max_length=20, verbose_name='币种')),
                ('collection_dst_addr', models.CharField(help_text='归集目的地址', max_length=100, verbose_name='归集目的地址')),
                ('min_amount_to_collect', models.DecimalField(decimal_places=8, help_text='最小归集金额', max_digits=28, verbose_name='最小归集金额')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '归集配置',
                'verbose_name_plural': '归集配置',
                'db_table': 'tb_collection_config',
                'managed': True,
                'unique_together': {('pro_id', 'token_name')},
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('token_name', models.CharField(max_length=20, verbose_name='币种')),
                ('address_nums', models.IntegerField(default=0, verbose_name='地址总数')),
                ('uncharged_address_nums', models.IntegerField(default=0, verbose_name='未充值地址数')),
                ('update_time', models.DateTimeField(max_length=0, verbose_name='最后更新时间')),
                ('pro_id', models.ForeignKey(db_column='pro_id', on_delete=django.db.models.deletion.CASCADE, to='clientadmin.Project', verbose_name='项目方ID')),
            ],
            options={
                'verbose_name': '地址管理',
                'verbose_name_plural': '地址管理',
                'db_table': 'tb_address_admin',
                'managed': True,
                'unique_together': {('token_name', 'pro_id')},
            },
        ),
    ]
