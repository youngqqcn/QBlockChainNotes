
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for t_btc_address
-- ----------------------------
DROP TABLE IF EXISTS `t_btc_address`;
CREATE TABLE `t_btc_address`  (
  `no` bigint(20) NOT NULL AUTO_INCREMENT,
  `address` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`no`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 701 CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_eth_accounts
-- ----------------------------
DROP TABLE IF EXISTS `t_eth_accounts`;
CREATE TABLE `t_eth_accounts`  (
  `no` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '序号',
  `address` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT '地址',
  PRIMARY KEY (`no`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 601 CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_eth_charge
-- ----------------------------
DROP TABLE IF EXISTS `t_eth_charge`;
CREATE TABLE `t_eth_charge`  (
  `height` bigint(20) UNSIGNED NOT NULL,
  `txdata` json NOT NULL,
  PRIMARY KEY (`height`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_htdf_accounts
-- ----------------------------
DROP TABLE IF EXISTS `t_htdf_accounts`;
CREATE TABLE `t_htdf_accounts`  (
  `no` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '序号',
  `address` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  PRIMARY KEY (`no`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 301 CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_htdf_charge
-- ----------------------------
DROP TABLE IF EXISTS `t_htdf_charge`;
CREATE TABLE `t_htdf_charge`  (
  `height` bigint(20) UNSIGNED NOT NULL COMMENT '区块高度',
  `txdata` json NOT NULL COMMENT '交易数据',
  PRIMARY KEY (`height`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_usdp_accounts
-- ----------------------------
DROP TABLE IF EXISTS `t_usdp_accounts`;
CREATE TABLE `t_usdp_accounts`  (
  `no` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '序号',
  `address` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`no`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 301 CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_usdp_charge
-- ----------------------------
DROP TABLE IF EXISTS `t_usdp_charge`;
CREATE TABLE `t_usdp_charge`  (
  `height` bigint(20) UNSIGNED NOT NULL,
  `txdata` json NOT NULL,
  PRIMARY KEY (`height`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
