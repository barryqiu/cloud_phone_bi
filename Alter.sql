CREATE TABLE `tb_business` (
`id`  int NOT NULL AUTO_INCREMENT ,
`business_name`  varchar(32) NULL ,
`business_desc`  text NULL ,
`allot_limit_type`  tinyint NULL ,
`allot_limit_num`  int NULL ,
`add_time`  datetime NULL ,
PRIMARY KEY (`id`)
);

ALTER TABLE `tb_game_server`
ADD COLUMN `qr_url`  varchar(150) NULL AFTER `add_time`,
ADD COLUMN `apk_url`  varchar(150) NULL AFTER `qr_url`;

ALTER TABLE `tb_agent_record`
ADD COLUMN `business_id`  int NULL AFTER `address_map`;

CREATE TABLE `tb_device_queue` (
`business_id`  int NULL ,
`game_id`  int NULL ,
`server_id`  int NULL ,
`device_id`  int NULL ,
`add_time`  datetime NULL ,
PRIMARY KEY (`device_id`)
)
;

ALTER TABLE `tb_game`
ADD COLUMN `banner_side`  varchar(150) NULL AFTER `qr_url`,
ADD COLUMN `square_img`  varchar(150) NULL AFTER `banner_side`;

ALTER TABLE `tb_game`
ADD COLUMN `allow_allot`  tinyint NULL AFTER `gift_url`;

ALTER TABLE `tb_user`
ADD COLUMN `role`  int NULL ;

ALTER TABLE `tb_agent_record`
ADD COLUMN `remark`  varchar(150) NULL;