
from .base import *

DEBUG = True 
SECRET_KEY = '123dev'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
        'NAME': 'cic',  # 数据库名，先前创建的
        'USER': 'backend_user',     # 用户名，可以自己创建用户
        'PASSWORD': '11/28/2019',  # 密码
        'HOST': '13.231.255.163',  # mysql服务所在的主机ip 54.169.143.92
        'PORT': '3306',         # mysql服务端口
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
        },
        'TEST': {
            'NAME': 'test_cic',
            'USER': 'backend_user',
            'CHARSET': "utf8",
            'COLLATION': "utf8_general_ci"
        },
        
        # 'NAME': 'church',  # 数据库名，先前创建的
        # 'USER': 'root',     # 用户名，可以自己创建用户
        # 'PASSWORD': 'root',  # 密码
        # 'HOST': '127.0.0.1',  # mysql服务所在的主机ip
        # 'PORT': '3306',         # mysql服务端口
    }
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INSTALLED_APPS += [
    'debug_toolbar',
]

