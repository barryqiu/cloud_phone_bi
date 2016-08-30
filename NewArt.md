Table：

* Business
* Game: 
* GameServer
* Device
* AgentRecord
* DeviceQueue

Business

```
id
business_name
business_desc
allot_limit_type
allot_limit_num
add_time
```

Game：

```
id
game_name
icon_url
banner_url
data_file_names
game_desc
gift_desc
gift_url
music_url
package_name
qr_url
apk_url
add_time
state
```

GameServer

```
id
game_id
server_des
server_name
data_file_names
package_name
qr_url
apk_url
add_time
```


Device

```
不变
```

AgentRecord
```
新增 bussiness_id，其他不变
```

DeviceQueue
```
business_id
game_id
server_id
device_id
add_time
```


Redis

* business-game; KEY: `business_id`, VALUE: `game_id zset`
* game-server; KEY: `game_id`, VALUE: `server_id list` 
* apk-device; KEY: `business_id:game_id:server_id` VALUE: `device_id set`
* free device; KEY: , VALUE: `device_id set`
* device-game; KEY: `device_id`,  VALUE: `json_encode(business_id, game_id,server_id) zset`
* user-num; KEY: `user_id`, VALUE: `allot_num, allot_limit hash`



