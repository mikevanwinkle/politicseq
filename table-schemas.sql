CREATE TABLE stat (
  `id` BIGINT unsigned NOT NULL AUTO_INCREMENT,
  `stat_key` VARCHAR(50) NOT NULL,
  `stat_value` FLOAT(10,2) NOT NULL,
  `stat_type` VARCHAR(20) NULL,
  `stat_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `article_id` BIGINT unsigned NOT NULL,
  PRIMARY KEY (`id`)
  ) ENGINE=innodb DEFAULT CHARSET=utf8;

CREATE TABLE `article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `summary` varchar(255) NOT NULL,
  `source` int(11) NOT NULL,
  `author_id` int(11) DEFAULT NULL,
  `content` longtext,
  `date` datetime DEFAULT CURRENT_TIMESTAMP,
  `link` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_article__source` (`source`),
  CONSTRAINT `fk_article__source` FOREIGN KEY (`source`) REFERENCES `source` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=226 DEFAULT CHARSET=utf8

CREATE TABLE `entity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `article_id` int(11) NOT NULL,
  `type` varchar(255) NOT NULL,
  `sentiment` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `entity_article_id` (`article_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
