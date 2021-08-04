CREATE TABLE `host` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` int(10) unsigned NOT NULL,
  `ip_str` varchar(20) DEFAULT NULL,
  `port` int(11) NOT NULL,
  `hostname` varchar(50) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `product` varchar(50) DEFAULT NULL,
  `version` varchar(100) DEFAULT NULL,
  `os` varchar(20) DEFAULT NULL,
  `isp` varchar(50) DEFAULT NULL,
  `org` varchar(20) DEFAULT NULL,
  `asn` varchar(20) DEFAULT NULL,
  `transport` varchar(5) DEFAULT NULL,
  `first_seen` date DEFAULT NULL,
  `last_seen` date DEFAULT NULL,
  `last_update` date DEFAULT NULL,
  PRIMARY KEY (`ip`,`port`),
  UNIQUE KEY `host_id_key` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `host_LastImport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` int(10) unsigned NOT NULL,
  `ip_str` varchar(20) DEFAULT NULL,
  `port` int(11) NOT NULL,
  `hostname` varchar(50) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `product` varchar(50) DEFAULT NULL,
  `version` varchar(100) DEFAULT NULL,
  `os` varchar(20) DEFAULT NULL,
  `isp` varchar(50) DEFAULT NULL,
  `org` varchar(20) DEFAULT NULL,
  `asn` varchar(20) DEFAULT NULL,
  `transport` varchar(5) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`ip`,`port`),
  UNIQUE KEY `host_LastImport_id_key` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;