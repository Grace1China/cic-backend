"""
Django settings for church project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
# import storage_backends

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'zkt!bwt)@1jx3#a&9d@65+3aqm^rru32s+-qamngqi8)8gn^-s'

# # SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False

ALLOWED_HOSTS = ['*']

APPEND_SLASH = True

# X_FRAME_OPTIONS = 'ALLOW-FROM *'

AUTH_USER_MODEL = 'users.CustomUser'
SIMPLEUI_HOME_INFO = False
# Application definition

INSTALLED_APPS = [
    'simpleui',
    'corsheaders',
    'drf_yasg',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    "church.apps.ChurchConfig",
    'churchs.apps.ChurchsConfig',
    'api.apps.ApiConfig',
    'users.apps.UsersConfig',
    # 'photos.apps.PhotosConfig',
    's3direct',
    #'debug_toolbar',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'rest_auth',
    'rest_auth.registration',
    'allauth',
    'allauth.account',
    'storages',
    'ckeditor',
    'ckeditor_uploader',
    'djoser',
    'rest_framework_simplejwt',
    'parsley'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

ROOT_URLCONF = 'church.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR+"/templates",],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'church.wsgi.application'

SWAGGER_SETTINGS = {
    # 基础样式
    'SECURITY_DEFINITIONS': {
        "basic":{
            'type': 'basic'
        }
    },
    # 如果需要登录才能够查看接口文档, 登录的链接使用restframework自带的.
    'LOGIN_URL': 'rest_framework:login',
    'LOGOUT_URL': 'rest_framework:logout',
    # 'DOC_EXPANSION': None,
    # 'SHOW_REQUEST_HEADERS':True,
    'USE_SESSION_AUTH': True,
    # 'DOC_EXPANSION': 'list',
    # 接口文档中方法列表以首字母升序排列
    'APIS_SORTER': 'alpha',
    # 如果支持json提交, 则接口文档中包含json输入框
    'JSON_EDITOR': True,
    # 方法列表字母排序
    'OPERATIONS_SORTER': 'alpha',
    'VALIDATOR_URL': None,
}


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
#         'NAME': 'cic',  # 数据库名，先前创建的
#         'USER': 'backend_user',     # 用户名，可以自己创建用户
#         'PASSWORD': '11/28/2019',  # 密码
#         'HOST': '13.231.255.163',  # mysql服务所在的主机ip 54.169.143.92
#         'PORT': '3306',         # mysql服务端口
#         'OPTIONS': {
#             "init_command": "SET foreign_key_checks = 0;",
#         },
#         'TEST': {
#             'NAME': 'test_cic',
#             'USER': 'backend_user',
#             'CHARSET': "utf8",
#             'COLLATION': "utf8_general_ci"
#         },
        
#         # 'NAME': 'church',  # 数据库名，先前创建的
#         # 'USER': 'root',     # 用户名，可以自己创建用户
#         # 'PASSWORD': 'root',  # 密码
#         # 'HOST': '127.0.0.1',  # mysql服务所在的主机ip
#         # 'PORT': '3306',         # mysql服务端口
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/' 

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]
# STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_ROOT = 'uploads/'
MEDIA_URL = '/uploads/'


REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS':'rest_framework.schemas.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES' : (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ),
    'DEFAULT_METADATA_CLASS': 'api.metadata.MinimalMetadata',
    # 'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata'
     'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'api.utill.BrowsableAPIRendererWithoutForms',
    ),
    
}

from datetime import timedelta


SIMPLEUI_STATIC_OFFLINE =True


INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

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

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)
SIMPLEUI_LOGIN_PARTICLES = False

def create_filename(filename):
    import uuid
    ext = filename.split('.')[-1]
    filename = '%s.%s' % (uuid.uuid4().hex, ext)
    return os.path.join('custom', filename)


S3DIRECT_DESTINATIONS = {
    # Allow anybody to upload any MIME type
    'misc': {
        'key': '/'
    },

    # Allow staff users to upload any MIME type
    'pdfs': {
        'key': 'uploads/pdfs',
        'auth': lambda u: u.is_staff,
        'acl': 'public-read',
        'allowed': [
            'file/pdf',
        ],

    },

    # Allow anybody to upload jpeg's and png's. Limit sizes to 5kb - 20mb
    'images': {
        'key': 'uploads/images',
        'auth': lambda u: True,
        'acl': 'public-read',
        'allowed': [
            'image/png'
            'image/jpeg',
        ],
        'content_length_range': (5000, 20000000),
        'allow_existence_optimization': True
    },

    # Allow authenticated users to upload mp4's
    'videos': {
        'key': 'uploads/videos',
        'auth': lambda u: u.is_authenticated,
        'acl': 'private',
        'allowed': ['video/mp4']
    },
    # Allow authenticated users to upload mp3's
    'audios': {
        'key': 'uploads/audios',
        'auth': lambda u: u.is_authenticated,
        'acl': 'private',
        'allowed': ['audio/mp3']
    },
    
    # "acl" [optional] Custom ACL for object, default is 'public-read'
    #       String: ACL
    'acl': 'private',


    # Allow anybody to upload any MIME type with a custom name function
    'custom_filename': {
        'key': create_filename
    },
}

# REST_AUTH_SERIALIZERS = [
    # 'LOGIN_SERIALIZER': 'path.to.custom.LoginSerializer',
    # 'TOKEN_SERIALIZER': 'path.to.custom.TokenSerializer',
# ]

SITE_ID = 1
DEFAULT_CHURCH_CODE = 'ims'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = []
CORS_ALLOW_HEADERS = []



AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'AKIA5YH7P4SOQO6ZMJHM')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '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')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'video-transcoding-061-source-9bbsedar323y')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', 'https://s3.ap-northeast-1.amazonaws.com')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-1')

AWS_DEFAULT_ACL = None
# AWS_DEFAULT_ACL = 'public-read'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'

ALIOSS_ACCESS_KEY_ID = os.environ.get('ALIOSS_ACCESS_KEY_ID', 'LTAI4Fd1JMHM3WSUN4vrHcj8')
ALIOSS_SECRET_ACCESS_KEY = os.environ.get('ALIOSS_SECRET_ACCESS_KEY', 'pXfMGYs2xAjjWHSKVoIaDuAC5ze49I')
ALIOSS_SOURCE_ENDPOINT = os.environ.get('ALIOSS_SOURCE_BUCKET_NAME', 'https://oss-cn-beijing.aliyuncs.com')
ALIOSS_DESTINATION_ENDPOINT = os.environ.get('ALIOSS_DESTINATION_BUCKET_NAME', 'https://oss-cn-beijing.aliyuncs.com')


ALIOSS_SOURCE_LOCATION = os.environ.get('ALIOSS_SOURCE_LOCATION', 'oss-cn-beijing.aliyuncs.com')
ALIOSS_DESTINATION_LOCATION = os.environ.get('ALIOSS_DESTINATION_LOCATION', 'oss-cn-beijing.aliyuncs.com')

ALIOSS_SOURCE_BUCKET_NAME = os.environ.get('ALIOSS_SOURCE_BUCKET_NAME', 'bicf-media-source')
ALIOSS_DESTINATION_BUCKET_NAME = os.environ.get('ALIOSS_DESTINATION_BUCKET_NAME', 'bicf-media-destination')
ALIOSS_EXPIRES = os.environ.get('ALIOSS_EXPIRES',24*3600)

MEDIABASE_PREFIX='api.bicf.org/mediabase'
ALIOSS_RedirectUrl = {
    'source':'api.bicf.org/mediasource',
    'destination':'api.bicf.org/mediabase'
}

# from django.conf import settings
ALIOSS_DESTINATIONS = {
    'images':{
        'endpoint':ALIOSS_DESTINATION_ENDPOINT,
        'location':ALIOSS_DESTINATION_LOCATION,
        'bucket':ALIOSS_DESTINATION_BUCKET_NAME,
        'redirecturl':'api.bicf.org/mediabase',
        'x-oss-object-acl':'public-read'   #public-read、private、public-read-write
    },
    'pdfs':{
        'endpoint':ALIOSS_DESTINATION_ENDPOINT,
        'location':ALIOSS_DESTINATION_LOCATION,
        'bucket':ALIOSS_DESTINATION_BUCKET_NAME,
        'redirecturl':'api.bicf.org/mediabase',
        'x-oss-object-acl':'private'   #public-read、private、public-read-write
    },
    'source':{
        'endpoint':ALIOSS_SOURCE_ENDPOINT,
        'location':ALIOSS_SOURCE_LOCATION,
        'bucket':ALIOSS_SOURCE_BUCKET_NAME,
        'redirecturl':'api.bicf.org/mediasource',
        'x-oss-object-acl':'private'   #public-read、private、public-read-write
    },
    'destination':{
        'endpoint':ALIOSS_DESTINATION_ENDPOINT,
        'location':ALIOSS_DESTINATION_LOCATION,
        'bucket':ALIOSS_DESTINATION_BUCKET_NAME,
        'redirecturl':'api.bicf.org/mediabase',
        'x-oss-object-acl':'private'   #public-read、private、public-read-write
    },
    'audios':{
        'endpoint':ALIOSS_DESTINATION_ENDPOINT,
        'location':ALIOSS_DESTINATION_LOCATION,
        'bucket':ALIOSS_DESTINATION_BUCKET_NAME,
        'redirecturl':'api.bicf.org/mediabase',
        'x-oss-object-acl':'private'   #public-read、private、public-read-write
    }
}


DEFAULT_FILE_STORAGE = 'church.storage_backends.MediaStorage'
AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
DEFAULT_FILE_STORAGE = 'church.storage_backends.PublicMediaStorage'

AWS_PRIVATE_MEDIA_LOCATION = 'media/private'
PRIVATE_FILE_STORAGE = 'church.storage_backends.PrivateMediaStorage'

CKEDITOR_UPLOAD_PATH = "uploads/"
# AWS_QUERYSTRING_AUTH = False

APP_SERVER_IP = "13.231.255.163"  #singpore 54.169.143.92


CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        # 'skin': 'office2013',
        'language': 'zh-cn',
        'uiColor': '#AADC6E',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language', 'CodeSnippet', 'CodeSnippetGeshi']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
            '/',  # put this to force next toolbar on new line
            {'name': 'yourcustomtools', 'items': [
                # put the name of your editor.ui.addButton here
                'Preview',
                'Maximize',

            ]},
        ],
        'toolbar': 'YourCustomToolbarConfig',  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        # 'height': 291,
        # 'width': '100%',
        # 'filebrowserWindowHeight': 725,
        # 'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage', # the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath',
            'codesnippet',
        ]),
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {filename} {funcName} {lineno} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'formatter':'verbose',
            'class': 'logging.FileHandler',
            'filename': '/data/log/django/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'dev.error': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False
        }
    },
}


