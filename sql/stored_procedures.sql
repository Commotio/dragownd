DELIMITER $$
CREATE DEFINER=`dragownd`@`%` PROCEDURE `Merge_LastImport`()
BEGIN

# Insert new hosts and update seen hosts 'last_seen'
INSERT INTO `dragownd`.`host` (`ip`, `ip_str`, `port`, `hostname`, `active`, `product`, `version`, `os`, `isp`, `org`, `asn`, `transport`, `first_seen`, `last_seen`, `last_update`)
	SELECT  `host_LastImport`.`ip`,
			`host_LastImport`.`ip_str`,
			`host_LastImport`.`port`,
			`host_LastImport`.`hostname`,
			`host_LastImport`.`active`,
			`host_LastImport`.`product`,
			`host_LastImport`.`version`,
			`host_LastImport`.`os`,
			`host_LastImport`.`isp`,
			`host_LastImport`.`org`,
			`host_LastImport`.`asn`,
			`host_LastImport`.`transport`,
			`host_LastImport`.`date`,
            `host_LastImport`.`date`,
            `host_LastImport`.`date`
	FROM `dragownd`.`host_LastImport`
ON DUPLICATE KEY UPDATE
	`host`.`active` = 1,
	`host`.`last_seen` = `host_LastImport`.`date`,
	`host`.`last_update` = `host_LastImport`.`date`;


# Update seen hosts that aren't in LastImport to not active
UPDATE `dragownd`.`host`
SET `host`.`active` = 0,
	`host`.`last_update` = curdate()
WHERE `host`.id NOT IN
	(SELECT h.id
	 FROM host h
	 JOIN host_LastImport hLI
		ON h.ip = hLI.ip
		AND h.port = hLI.port);

# Truncate LastImport
TRUNCATE TABLE `dragownd`.`host_LastImport`;

END$$
DELIMITER ;
