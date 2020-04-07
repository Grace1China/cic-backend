from .base import *

DEBUG = True
RUNTIME = 'development'

SECRET_KEY = '123dev'

IAP_IS_SANDBOX = True
PAYPAL_IS_SANEBOX = True
DEFAULT_CHURCH_CODE = 'ims'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=7),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=30),
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'NAME': 'cic_20200323',  # test_cic数据库名，先前创建的

        # 本地 
        'USER': 'root',  # 用户名，可以自己创建用户
        'PASSWORD': '',  # 密码
        'HOST': '127.0.0.1',  # mysql服务所在的主机ip 54.169.143.92

        # 测试
        # 'NAME': 'cic_20200323',  # test_cic数据库名，先前创建的
        # 'USER': 'backend_user',     # 用户名，可以自己创建用户
        # 'PASSWORD': '11/28/2019',  # 密码
        # 'HOST': '13.231.255.163',  # mysql服务所在的主机ip 54.169.143.92

        'PORT': '3306',  # mysql服务端口
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
            # 'charset': 'utf8md4',
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
INSTALLED_APPS += [
    'debug_toolbar',
]
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

INTERNAL_IPS = ('127.0.0.1',)

MAINSITE_API_V1 = 'http://127.0.0.1:8200/mainsite_api_v1/mst/MakeSermon'
APP_SERVER_IP = "13.231.255.163"  # singpore 54.169.143.92

import os

save_dir = "data/log/django/l3dev/" #本地环境 /data/log/django/l3dev/
if os.path.exists(save_dir) is False:
    os.makedirs(save_dir)

LOGGING = {
    # 在调试的时候，要把信息log到console和文件； 不调试时只输出到文件；选定的消息，如上传视频成功，可以发送邮件
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {lineno:d} {process:d} {thread:d} {message}',
            # Attribute name											Format											Description
            # args											You shouldn’t need to format this yourself.			The tuple of arguments merged into msg to produce message, or a dict whose values are used for the merge (when there is only one argument, and it is a dictionary).
            # asctime											%(asctime)s											Human-readable time when the LogRecord was created. By default this is of the form ‘2003-07-08 16:49:45,896’ (the numbers after the comma are millisecond portion of the time).
            # created											%(created)f											Time when the LogRecord was created (as returned by time.time()).
            # exc_info										You shouldn’t need to format this yourself.		Exception tuple (à la sys.exc_info) or, if no exception has occurred, None.
            # filename										%(filename)s									Filename portion of pathname.
            # funcName										%(funcName)s									Name of function containing the logging call.
            # levelname										%(levelname)s									Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
            # levelno											%(levelno)s											Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            # lineno											%(lineno)d											Source line number where the logging call was issued (if available).
            # message											%(message)s											The logged message, computed as msg % args. This is set when Formatter.format() is invoked.
            # module											%(module)s											Module (name portion of filename).
            # msecs											%(msecs)d											Millisecond portion of the time when the LogRecord was created.
            # msg											You shouldn’t need to format this yourself.				The format string passed in the original logging call. Merged with args to produce message, or an arbitrary object (see Using arbitrary objects as messages).
            # name											%(name)s											Name of the logger used to log the call.
            # pathname										%(pathname)s									Full pathname of the source file where the logging call was issued (if available).
            # process											%(process)d											Process ID (if available).
            # processName										%(processName)s									Process name (if available).
            # relativeCreated									%(relativeCreated)d							Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.
            # stack_info										You shouldn’t need to format this yourself.		Stack frame information (where available) from the bottom of the stack in the current thread, up to and including the stack frame of the logging call which resulted in the creation of this record.
            # thread											%(thread)d											Thread ID (if available).
            # threadName										%(threadName)s									Thread name (if available).

            'style': '{',
        },
        'simple': {
            'format': '{levelname} {module} {lineno:d} {message} {pathname}',
            'style': '{',
        },
    },
    'filters': {
        'special': {
            # '()': 'project.logging.SpecialFilter',
            'foo': 'bar',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'InfoFilter': {
            '()': 'church.confs.base.InfoFilter'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true', 'InfoFilter'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console_err': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file_info': {
            'level': 'INFO',
            'filters': ['InfoFilter'],
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'data/log/django/l3dev/info.log',  # 本机data/log/django/error.log
            'encoding': 'utf8',
        },
        'file_err': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'data/log/django/l3dev/error.log',
            'formatter': 'verbose',
            'encoding': 'utf8',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['special'],
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'dev.error': {
            'handlers': ['file_err'],  # dev.error is the old version
            'level': 'ERROR',
            'propagate': False
        },
        'church.all': {
            'handlers': ['file_info', 'file_err'],  # 'console', 'console_err',,
            'level': 'INFO',
            'propagate': False,
        }
    }
}

