# pyblog

## 主要功能：
- 文章分类(弃用)、标签
- 支持markdown编辑文章
- 按时间归档
- 嵌套评论

### 安装
```
# git clone https://github.com/bzyy/pyblog.git
# cd pyblog && pip install -r requirements.txt
```
### 配置
- 创建数据库以及用户:
	```
	> create database pyblog charset=utf8;
	> create user 'pyblog'@'localhost' identified by '123456';
	> grant all privileges on `pyblog`.* to 'pyblog'@'%' identified by '123456';
	```

- 复制pyblog/settings.example.py 到 pyblog/settings.py并修改以下内容:
	```
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.mysql',
			'OPTIONS': {
				"database": 'pyblog',
				'user': 'pyblog',
				'password': '123456',
				'charset': 'utf8mb4',
				'host': 'localhost',
				'port': 3306,
			}
		}
	}
	```
- 建表
	```
	# python manage.py makemigrations
	# python manage.py migrate
	```
- 创建超级用户
	```
	python manage.py createsuperuser
	```
### 运行
```
python manage.py runserver
```
浏览器访问 127.0.0.1:8000即可看到效果

## 服务器部署
> nginx + uwsgi + virtualenv

### 使用virtualenv运行pyblog
```
# 安装virtualenv,并创建环境
# python3 -m pip install --user virtualenv
# python3 -m venv .venv

# 进入virtualenv,安装依赖包
# source .venv/bin/activate
# pip install -r requirements.txt

# 收集静态文件
# python manage.py collectstatic --noinput
```
其它数据库配置同上
	
### NGINX

- 配置如下:
	```
	upstream django {
		server unix:///home/ubuntu/.github/pyblog/pyblog.sock; # for a file socket
		# server 127.0.0.1:2000; # for a web port socket (we'll use this first)
	}

	# configuration of the server
	server {
		# the port your site will be served on
		listen      80;
		# the domain name it will serve for

		# 请改为自己的域名
		server_name blog.sadeye.cn;
		charset     utf-8;

		# max upload size
		client_max_body_size 75M;   # adjust to taste

		# Django media
		location /media  {
			alias  /home/ubuntu/.github/pyblog/media;  # your Django project's media files - amend as required
		}

		location /static {
			alias  /home/ubuntu/.github/pyblog/.static; # your Django project's static files - amend as required
		}
		# Finally, send all non-media requests to the Django server.
		location / {
			uwsgi_pass  django;
			include     uwsgi_params; # the uwsgi_params file you installed
		}
	}
	```
- 重启nginx：
	```
	service nginx restart
	```

### UWSGI
- 安装:
	```
	sudo pip3 install uwsgi
	```

- 编写配置文件uwsgi.yml
	```
	uwsgi:
	chdir: /home/ubuntu/.github/pyblog  # (这里改为你自己的项目路径)
	module: pyblog.wsgi
	home: /home/ubuntu/.github/pyblog/.venv  # (创建的virtualenv路径)
	master: true
	processes: 10
	#http: :8000
	#socket: 127.0.0.1:2000
	socket: /home/ubuntu/.github/pyblog/pyblog.sock
	vacuum: true
	```
- 运行:
	```
	uwsgi  --yml uwsgi.yml
	```

- 访问您的nginx配置域名即可看到效果


## 扩展配置

### 使用systemd管理uwsgi：
- 创建文件 /etc/systemd/system/pyblog.uwsgi.service 写入如下内容:
	```
	[Unit]
	Description=uWSGI Emperor
	After=mysql.target

	[Service]
	WorkingDirectory=/home/ubuntu/.github/pyblog
	ExecStart=/usr/local/bin/uwsgi --yml /home/ubuntu/.github/pyblog/uwsgi.yml
	#ExecStart=/usr/local/bin/uwsgi --yml uwsgi.yml
	# Requires systemd version 211 or newer
	RuntimeDirectory=uwsgi
	Restart=always
	KillSignal=SIGQUIT
	Type=notify
	StandardError=syslog
	NotifyAccess=all

	[Install]
	WantedBy=multi-user.target
	```
- 使用systemctl管理
	```
	# systemctl enable pyblog.uwsgi   //开启开机启动
	# systemctl disable pyblog.uwsgi  //关闭开机启动
	# systemctl restart pyblog.uwsgi  //重启pyblog服务 
	# systemctl stop pyblog.uwsgi     //关闭pyblog服务
	```
### 定时备份数据库上传至腾讯云对象存储
> 相关文档，上腾讯云官网了解一下  
> 备注: 该脚本备份的文件默认在.backup文件夹中  
> 备份策略: 上传(会先压缩)到腾讯云之前，会与本地备份的文件比较,如果相同，且已上传，本次备份将停止上传至腾讯云，只保存在本地。
- 复制脚本
	```
	cp backup-db.example.py backup-db.py
	```
- 修改backup-db.py配置项:
	```
	# tencent settings
	secret_id = '替换为你自己的secret_id'
	secret_key = '替换为你自己的secret_key'
	region = 'ap-shanghai(根据情况替换)'
	bucket = '替换为你自己的桶名'
	...
	# mysql settings
	mysql_user = 'pyblog'
	mysql_password = '123456'
	mysql_backup_db_name = 'pyblog'
	```
- 每天凌晨1点自动备份一次数据库
	```
	00 01 * * * /home/ubuntu/.github/pyblog/.venv/bin/python /home/ubuntu/.github/pyblog/backup-db.py
	```