"""
Django settings for church project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'zkt!bwt)@1jx3#a&9d@65+3aqm^rru32s+-qamngqi8)8gn^-s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

IAP_IS_SANDBOX = False
PAYPAL_IS_SANEBOX = False

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=7),
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

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
        'NAME': 'test_cic',  # 数据库名，先前创建的
        'USER': 'backend_user',     # 用户名，可以自己创建用户
        'PASSWORD': '11/28/2019',  # 密码
        'HOST': '13.231.255.163',  # mysql服务所在的主机ip 54.169.143.92
        'PORT': '3306',         # mysql服务端口
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
        },
        #'TEST': {
        #    'NAME': 'test_cic',
        #    'USER': 'backend_user',
        #    'CHARSET': "utf8",
        #    'COLLATION': "utf8_general_ci"
        #},
        
        # 'NAME': 'church',  # 数据库名，先前创建的
        # 'USER': 'root',     # 用户名，可以自己创建用户
        # 'PASSWORD': 'root',  # 密码
        # 'HOST': '127.0.0.1',  # mysql服务所在的主机ip
        # 'PORT': '3306',         # mysql服务端口
    }
}


LOGGING = {
    #在调试的时候，要把信息log到console和文件； 不调试时只输出到文件；选定的消息，如上传视频成功，可以发送邮件
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
            'format': '{levelname} {module} {lineno:d} {message}',
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
        'InfoFilter':{
            '()':'apiprj.settings.InfoFilter'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true','InfoFilter'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'console_err': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file_info': {
            'level': 'INFO',
            'filters': ['InfoFilter'],
            'class': 'logging.FileHandler',
            'formatter': 'simple'
            'filename': '/data/log/django/l3sandbox/info.log', #本机data/log/django/error.log
        },
        'file_err': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/data/log/django/l3sandbox/error.log',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['special']
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
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False
        }
        'church.all': {
            'handlers': ['console', 'console_err','file_info','file_err'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}
