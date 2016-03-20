# cloud_phone_bi

CLOUD PHONE BI


pip install gunicorn
 
gunicron -w4 -b0.0.0.0:6000 manage:app
 
pip install supervisor
echo_supervisord_conf > supervisor.conf   # 生成 supervisor 默认配置文件
vim supervisor.conf                       # 修改 supervisor 配置文件，添加 gunicorn 进程管理

supervisor.conf 放在/opt/supervisor/

supervisor.conf 配置文件底部添加
[program:cloudphone]
command=/usr/local/bin/cloudphonebi/bin/gunicorn -w4 -b0.0.0.0:6000 manage:app          ; supervisor启动命令
directory=/opt/cloudphonebi/cloud_phone_bi                                              ; 项目的文件夹路径
startsecs=0                                                                             ; 启动时间
stopwaitsecs=0                                                                          ; 终止等待时间
autostart=false                                                                         ; 是否自动启动
autorestart=false                                                                       ; 是否自动重启
stdout_logfile=/opt/cloudphonebi/cloud_phone_bi/log/gunicorn.log                        ; log 日志
stderr_logfile=/opt/cloudphonebi/cloud_phone_bi/log/gunicorn.err                        ; 错误日志

supervisor的基本使用命令
supervisord -c supervisor.conf                             通过配置文件启动supervisor
supervisorctl -c supervisor.conf status                    察看supervisor的状态
supervisorctl -c supervisor.conf reload                    重新载入 配置文件
supervisorctl -c supervisor.conf start [all]|[appname]     启动指定/所有 supervisor管理的程序进程
supervisorctl -c supervisor.conf stop [all]|[appname]      关闭指定/所有 supervisor管理的程序进程

supervisor 还有一个web的管理界面，可以激活。更改下配置
[inet_http_server]         ; inet (TCP) server disabled by default
port=127.0.0.1:9001        ; (ip_address:port specifier, *:port for all iface)
username=user              ; (default is no username (open server))
password=123               ; (default is no password (open server))

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock ; use a unix:// URL  for a unix socket
serverurl=http://127.0.0.1:9001 ; use an http:// url to specify an inet socket
username=user              ; should be same as http_username if set
password=123                ; should be same as http_password if set
;prompt=mysupervisor         ; cmd line prompt (default "supervisor")
;history_file=~/.sc_history  ; use readline history if available

pip install  Flask==0.10.1 Flask-Bootstrap==3.3.5.7 Flask-HTTPAuth==2.7.0 Flask-Login==0.2.11 Flask-Mail==0.9.1 Flask-Migrate==1.6.0 Flask-Moment==0.5.1 Flask-PageDown==0.2.1 Flask-Redis==0.1.0 Flask-Script==2.0.5 Flask-SQLAlchemy==2.1 Flask-SSLify==0.1.5 Flask-WTF==0.12