/*
 Navicat Premium Data Transfer

 Source Server         : 192.168.10.29
 Source Server Type    : MySQL
 Source Server Version : 50726
 Source Host           : 192.168.10.29:3306
 Source Schema         : pg_database_pro

 Target Server Type    : MySQL
 Target Server Version : 50726
 File Encoding         : 65001

 Date: 25/05/2020 14:22:01
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_group_permissions_group_id_permission_id_0cd325b0_uniq`(`group_id`, `permission_id`) USING BTREE,
  INDEX `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm`(`permission_id`) USING BTREE,
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_permission_content_type_id_codename_01ab375a_uniq`(`content_type_id`, `codename`) USING BTREE,
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 61 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for auth_user
-- ----------------------------
DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE `auth_user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `last_login` datetime(6) NULL DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `first_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `last_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for auth_user_groups
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_user_groups_user_id_group_id_94350c0c_uniq`(`user_id`, `group_id`) USING BTREE,
  INDEX `auth_user_groups_group_id_97559544_fk_auth_group_id`(`group_id`) USING BTREE,
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for auth_user_user_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE `auth_user_user_permissions`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq`(`user_id`, `permission_id`) USING BTREE,
  INDEX `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm`(`permission_id`) USING BTREE,
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for django_admin_log
-- ----------------------------
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `object_repr` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL,
  `change_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `content_type_id` int(11) NULL DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `django_admin_log_content_type_id_c4bce8eb_fk_django_co`(`content_type_id`) USING BTREE,
  INDEX `django_admin_log_user_id_c564eba6_fk_auth_user_id`(`user_id`) USING BTREE,
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 43 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `django_content_type_app_label_model_76bd3d3b_uniq`(`app_label`, `model`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 16 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 19 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session`  (
  `session_key` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `session_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`) USING BTREE,
  INDEX `django_session_expire_date_a5c62663`(`expire_date`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_active_address_balances
-- ----------------------------
DROP TABLE IF EXISTS `tb_active_address_balances`;
CREATE TABLE `tb_active_address_balances`  (
  `token_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '币种',
  `address` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '地址',
  `balance` decimal(28, 8) NOT NULL COMMENT '充币金额',
  `update_time` datetime(0) NOT NULL COMMENT '最后更新时间',
  `pro_id` int(11) NULL DEFAULT NULL COMMENT '项目方ID',
  PRIMARY KEY (`token_name`, `address`) USING BTREE,
  INDEX `pro_id`(`pro_id`) USING BTREE,
  CONSTRAINT `tb_active_address_balances_ibfk_1` FOREIGN KEY (`pro_id`) REFERENCES `tb_project` (`pro_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_add_address_order
-- ----------------------------
DROP TABLE IF EXISTS `tb_add_address_order`;
CREATE TABLE `tb_add_address_order`  (
  `order_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'order_id',
  `token_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '币种名',
  `apply_times` int(11) NOT NULL COMMENT '本次是第几次申请',
  `count` int(11) NOT NULL COMMENT '申请数量',
  `start_addr_index` int(11) NOT NULL COMMENT '本次生成,起始地址索引',
  `end_addr_index` int(11) NOT NULL COMMENT '本次生成,结束地址索引',
  `audit_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '审核状态, PENDING:待审核, REJECTED:已拒绝, PASSED:已通过',
  `generate_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '地址生成状态, NOTYET:未生成, SUCCESS:生成完成',
  `order_create_time` datetime(0) NOT NULL COMMENT '订单生成时间',
  `audit_complete_time` datetime(0) NULL DEFAULT NULL COMMENT '订单审核完成(通过或拒绝)时间',
  `order_complete_time` datetime(0) NULL DEFAULT NULL COMMENT '订单完成时间',
  `order_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '地址生成状态, PROCESSING:处理中, SUCCESS:成功, FAIL:失败',
  `remark` varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '备注',
  `active_status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '启用状态, NO:未启用, YES:已启用',
  `pro_id` int(11) NULL DEFAULT NULL COMMENT '项目方ID',
  PRIMARY KEY (`order_id`) USING BTREE,
  INDEX `pro_id`(`pro_id`) USING BTREE,
  CONSTRAINT `tb_add_address_order_ibfk_1` FOREIGN KEY (`pro_id`) REFERENCES `tb_project` (`pro_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_address
-- ----------------------------
DROP TABLE IF EXISTS `tb_address`;
CREATE TABLE `tb_address`  (
  `address` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '地址',
  `token_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '币种名',
  `account_index` int(11) NOT NULL COMMENT '账户索引',
  `address_index` int(11) NOT NULL COMMENT '地址索引',
  `create_time` datetime(0) NOT NULL COMMENT '添加的时间',
  `pro_id` int(11) NULL DEFAULT NULL COMMENT '项目方ID',
  PRIMARY KEY (`address`) USING BTREE,
  INDEX `pro_id`(`pro_id`) USING BTREE,
  CONSTRAINT `tb_address_ibfk_1` FOREIGN KEY (`pro_id`) REFERENCES `tb_project` (`pro_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_collection_config
-- ----------------------------
DROP TABLE IF EXISTS `tb_collection_config`;
CREATE TABLE `tb_collection_config`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id 自增',
  `token_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '币种名',
  `collection_dst_addr` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '出币地址',
  `min_amount_to_collect` decimal(28, 8) NOT NULL COMMENT '最小归集金额',
  `pro_id` int(11) NULL DEFAULT NULL COMMENT '项目方ID',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uidx_token_name_pro_id`(`token_name`, `pro_id`) USING BTREE,
  INDEX `pro_id`(`pro_id`) USING BTREE,
  CONSTRAINT `tb_collection_config_ibfk_1` FOREIGN KEY (`pro_id`) REFERENCES `tb_project` (`pro_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 31 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_collection_fee_config
-- ----------------------------
DROP TABLE IF EXISTS `tb_collection_fee_config`;
CREATE TABLE `tb_collection_fee_config`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id 自增',
  `token_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '币种名',
  `address` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '出币地址',
  `pro_id` int(11) NULL DEFAULT NULL COMMENT '项目方ID',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uidx_token_name_pro_id`(`token_name`, `pro_id`) USING BTREE,
  INDEX `pro_id`(`pro_id`) USING BTREE,
  CONSTRAINT `tb_collection_fee_config_ibfk_1` FOREIGN KEY (`pro_id`) REFERENCES `tb_project` (`pro_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_collection_records
-- ----------------------------
DROP TABLE IF EXISTS `tb_collection_records`;
CREATE TABLE `tb_collection_records`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id 自增',
  `token_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '币种名',
  `from_address` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '源地址',
  `to_address` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '目的地址',
  `amount` decimal(28, 8) NOT NULL COMMENT '归集金额',
  `complete_time` datetime(0) NULL DEFAULT NULL COMMENT '完成时间',
  `block_height` bigint(20) NOT NULL COMMENT '交易所在区块高度',
  `block_time` datetime(0) NULL DEFAULT NULL COMMENT '区块时间戳',
  `transaction_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '交易状态, NOTYET:尚未汇出, PENDING:已转出,等待交易为被打包进区块, FAIL :交易失败, SUCCESS : 交易成功 ',
  `collection_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '归集类型',
  `tx_hash` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '交易hash(txid)',
  `pro_id` int(11) NULL DEFAULT NULL COMMENT '项目方ID',
  `tx_confirmations` int(11) NOT NULL COMMENT '交易的区块确认数',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `pro_id`(`pro_id`) USING BTREE,
  CONSTRAINT `tb_collection_records_ibfk_1` FOREIGN KEY (`pro_id`) REFERENCES `tb_project` (`pro_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1612 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_deposit
-- ----------------------------
DROP TABLE IF EXISTS `tb_deposit`;
CREATE TABLE `tb_deposit`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id 自增',
  `pro_id` int(11) NULL DEFAULT NULL COMMENT '项目方ID',
  `token_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '币种',
  `tx_hash` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '交易hash(txid)',
  `from_addr` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '源地址',
  `to_addr` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '目的地址',
  `memo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '转账备注(memo), 有些币种需要带memo, 例如 EOS, XRP',
  `amount` decimal(28, 8) NOT NULL COMMENT '充币金额',
  `block_height` bigint(20) NOT NULL COMMENT '交易所在区块高度',
  `block_time` datetime(0) NOT NULL COMMENT '区块时间戳',
  `notify_status` int(11) NOT NULL COMMENT '通知状态, 0:未通知, 1: 通知成功 , 2:通知失败',
  `tx_confirmations` int(11) NOT NULL COMMENT '交易的区块确认数',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uidx_pro_id_token_name_tx_hash`(`pro_id`, `token_name`, `tx_hash`) USING BTREE,
  INDEX `idx_for_query_by_block_height`(`pro_id`, `token_name`, `block_height`) USING BTREE,
  INDEX `ix_tb_deposit_block_time`(`block_time`) USING BTREE,
  INDEX `ix_tb_deposit_block_height`(`block_height`) USING BTREE,
  INDEX `idx_for_query_by_block_time`(`pro_id`, `token_name`, `block_time`) USING BTREE,
  CONSTRAINT `tb_deposit_ibfk_1` FOREIGN KEY (`pro_id`) REFERENCES `tb_project` (`pro_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3268 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_project
-- ----------------------------
DROP TABLE IF EXISTS `tb_project`;
CREATE TABLE `tb_project`  (
  `pro_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '项目方id',
  `pro_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '项目方名称',
  `tel_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '项目方电话号码',
  `email` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '项目方邮箱',
  `api_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '项目方的API_KEY',
  `account_status` int(11) NOT NULL COMMENT '账户状态, 0:未激活, 1:正常 , 2:已冻结 , 3:已禁用',
  `bip44_account_index` int(11) NOT NULL COMMENT 'BIP44的账户索引,正常情况下,此值和pro_id相等',
  `create_time` datetime(0) NOT NULL COMMENT '创建时间',
  `client_sign_key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '客户端私钥',
  `client_verify_key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '客户端公钥',
  `server_sign_key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '服务端私钥',
  `server_verify_key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '服务端公钥',
  PRIMARY KEY (`pro_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_scan_start_height
-- ----------------------------
DROP TABLE IF EXISTS `tb_scan_start_height`;
CREATE TABLE `tb_scan_start_height`  (
  `token_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '币种, 统一使用大写!',
  `block_height` int(11) NOT NULL COMMENT '区块高度',
  PRIMARY KEY (`token_name`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_withdraw_config
-- ----------------------------
DROP TABLE IF EXISTS `tb_withdraw_config`;
CREATE TABLE `tb_withdraw_config`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id 自增',
  `token_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '币种名',
  `address` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '出币地址',
  `min_amount` decimal(28, 8) NOT NULL COMMENT '最大提币金额',
  `max_amount` decimal(28, 8) NOT NULL COMMENT '最小提币金额',
  `balance_threshold_to_sms` decimal(28, 8) NOT NULL COMMENT '短信通知阈值',
  `is_open` tinyint(1) NULL DEFAULT NULL COMMENT '提币通过是否开启',
  `pro_id` int(11) NULL DEFAULT NULL COMMENT '项目方ID',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uidx_token_name_pro_id`(`token_name`, `pro_id`) USING BTREE,
  INDEX `pro_id`(`pro_id`) USING BTREE,
  CONSTRAINT `tb_withdraw_config_ibfk_1` FOREIGN KEY (`pro_id`) REFERENCES `tb_project` (`pro_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 31 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_withdraw_order
-- ----------------------------
DROP TABLE IF EXISTS `tb_withdraw_order`;
CREATE TABLE `tb_withdraw_order`  (
  `serial_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '支付网关系统自己生成的流水id',
  `order_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '用户传来的order_id',
  `pro_id` int(11) NULL DEFAULT NULL COMMENT '项目方ID',
  `token_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '币种名',
  `from_addr` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '源地址',
  `to_addr` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '目的地址',
  `memo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '转账备注(memo), 有些币种需要带memo, 例如 EOS, XRP',
  `amount` decimal(28, 8) NOT NULL COMMENT '金额',
  `block_height` bigint(20) NOT NULL COMMENT '交易所在区块高度',
  `tx_hash` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '交易hash(txid)',
  `callback_url` varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '回调通知接口url',
  `tx_confirmations` int(11) NOT NULL COMMENT '交易的区块确认数',
  `order_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '订单状态, PROCESSING:处理中, SUCCESS:已成功, FAIL:已失败',
  `transaction_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '交易状态, NOTYET:尚未汇出, PENDING:已转出,等待交易为被打包进区块, FAIL :交易失败, SUCCESS : 交易成功 ',
  `notify_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '通知状态, NOTYET:尚未通知, FIRSTSUCCESS:\"已汇出\"通知成功, FIRSTFAIL:\"已汇出\"通知失败, SECONDSUCCESS:第二次通知成功, SECONDFAIL:第二次通知失败',
  `notify_times` int(11) NOT NULL COMMENT '通知次数, 记录通知的次数(包括成功和失败)',
  `block_time` datetime(0) NULL DEFAULT NULL COMMENT '区块时间戳',
  `complete_time` datetime(0) NULL DEFAULT NULL COMMENT '订单完成时间',
  `remark` varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '订单说明,保存一些说明信息',
  PRIMARY KEY (`serial_id`) USING BTREE,
  INDEX `pro_id`(`pro_id`) USING BTREE,
  INDEX `ix_tb_withdraw_order_order_id`(`order_id`) USING BTREE,
  CONSTRAINT `tb_withdraw_order_ibfk_1` FOREIGN KEY (`pro_id`) REFERENCES `tb_project` (`pro_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
