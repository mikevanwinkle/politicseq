CREATE TABLE stat (
  `id` BIGINT unsigned NOT NULL AUTO_INCREMENT,
  `stat_key` VARCHAR(50) NOT NULL,
  `stat_value` FLOAT(10,2) NOT NULL,
  `stat_type` VARCHAR(20) NULL,
  `stat_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `article_id` BIGINT unsigned NOT NULL,
  PRIMARY KEY (`id`)
  ) ENGINE=innodb DEFAULT CHARSET=utf8;