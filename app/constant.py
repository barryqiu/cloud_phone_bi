# device properties
DEVICE_ID = 'device_id'
IP_ADDRESS = 'ip_address'
SERIAL = 'serial'
MAC = 'mac'
SYSTEM_VERSION = 'system_version'
USER_FLAG = 'use_flag'
HARD_STATE = 'hard_state'
SERVICE_STATE = 'service_state'
IMG_URL_LIST = 'img_url_list'
USE_TIMES = 'use_times'
ALLOT_TIME = 'allot_time'
DATA_PARTITION = 'data_partition'
SDCARD_PARTITION = 'sdcard_partition'
USED_CPU = 'used_cpu'
USED_MEMORY = 'used_memory'
RUN_TIME = 'runtime'
SERVICE_VERSION = 'service_version'

# List Device Info
LIST_DEVICE_INFO = {
    DEVICE_ID: 0,
    IP_ADDRESS: '',
    SERIAL: '',
    MAC: '',
    USER_FLAG: 0,
    HARD_STATE: 0,
    SERVICE_STATE: 0,
    IMG_URL_LIST: ''
}

# Detail Device Info
DETAIL_DEVICE_INFO = {
    DEVICE_ID: 0,
    IP_ADDRESS: '',
    SERIAL: '',
    MAC: '',
    SYSTEM_VERSION: '',
    USER_FLAG: 0,
    HARD_STATE: 0,
    SERVICE_STATE: 0,
    IMG_URL_LIST: '',
    USE_TIMES: 0,
    ALLOT_TIME: 0,
    DATA_PARTITION: '',
    SDCARD_PARTITION: '',
    USED_CPU: '',
    USED_MEMORY: '',
    RUN_TIME: 0,
    SERVICE_VERSION: ''
}

# DEVICE REDIS HASH KEY
START_USE_TIME = "start_use_time"

# msg send to device
MSG_TYPE_START_APP = "startapp"
MSG_TYPE_CLEAR = "clear"
MSG_TYPE_REBOOT = "reboot"
MSG_TYPE_KILL = "kill"
MSG_TYPE_RESTART = "restart"
MSG_TYPE_DOWNLOAD = "download"
MSG_TYPE_UNINSTALL = "uninstall"
MSG_TYPE_NAKED = "naked"
MSG_TYPE_SELF_UPDATE_SYS = "selfupdate_sys"
MSG_TYPE_CHANGE_INPUT = "changeinput"
MSG_TYPE_DISABLE_COMPONENT = "disable_component"
MSG_TYPE_ENABLE_COMPONENT = "enable_component"
MSG_TYPE_REDUCE_SYS = "reduce_sys"
MSG_TYPE_REDUCE_DATA = "reduce_data"
MSG_TYPE_DOWNLOAD_SYS_LIB = "download_sys_lib"
MSG_TYPE_CLEAR_LOG = "clearlog"
MSG_TYPE_DOWNLOAD_2_MOVE = "download2move"
MSG_TYPE_UNINSTALL_WEBKEY = "uninstall_webkey"
MSG_TYPE_SET_TIME = "settime"

