from django import template
from django.utils.html import conditional_escape
import boto3;
from django.conf import settings
import os,sys,json,base64,time,platform
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import jsonpickle # pip install jsonpickle
import json
# from django.utils.safestring import mark_safe   

import yaml # pip install pyyaml


import logging
theLogger = logging.getLogger('church.all')

register = template.Library()

# @register.filter()
def pre_signed_url(url):
    print('---------pre_signed_url----------')
    print(url)
    if url == None or len(url) == 0:
        return url
    import logging
    logging.debug(url)
    logging.debug(settings.AWS_STORAGE_BUCKET_NAME)
    if url.index(settings.AWS_STORAGE_BUCKET_NAME) >= 0:
        url = url.split('%s/' % settings.AWS_STORAGE_BUCKET_NAME)[1]
        s3_client = boto3.client('s3',aws_access_key_id=settings.AWS_ACCESS_KEY_ID,aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        try:
            response = s3_client.generate_presigned_url('get_object',Params={ 'Bucket': settings.AWS_STORAGE_BUCKET_NAME,'Key': url },ExpiresIn=3600)
        except Exception as e:
            return str(e)
        return response
    else:
        return url
# @register.filter()
def str2varname(astr):
    '''
    '''
    if astr == None or len(astr) == 0:
        return astr
    else:
        return astr.replace('-','_')
def tofilename(astr):
    '''
    '''
    ar = astr.split('/')
    return ar[len(ar)-1]
def timeticks(t):
    '''
    '''
    import time
    ticks = time.time()
    return int(ticks)
def jsondumps(v):
    '''
    '''
    import json
    return json.dumps(v) 


def __get_config(name):
    value = os.environ.get(name, getattr(settings, name, None))

    return value


@register.filter
def get_config(key):
    return __get_config(key)

# 从配置中读取图标
def get_config_icon(name):
    _config_icon = __get_config('SIMPLEUI_ICON')
    if _config_icon is None:
        return ''

    if name in _config_icon:
        return _config_icon.get(name)
    else:
        return ''

def get_icon(obj, name=None):
    temp = get_config_icon(name)
    if temp != '':
        return temp

    _dict = {
        'auth': 'fas fa-shield-alt',
        'User': 'far fa-user',
        'Group': 'fas fa-users-cog'
    }
    temp = _dict.get(obj)
    if not temp:
        _default = __get_config('SIMPLEUI_DEFAULT_ICON')
        if _default is None or _default:
            return 'far fa-file'
        else:
            return ''
    return temp

PY_VER = sys.version[0]  # 2 or 3

if PY_VER != '2':
    from importlib import reload

def unicode_to_str(u):
    if PY_VER != '2':
        return u
    return u.encode()

class LazyEncoder(DjangoJSONEncoder):
    """
        解决json __proxy__ 问题
    """

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


@register.simple_tag(takes_context=True)
def church_menus(context, _get_config=None):
    data = []

    # return request.user.has_perm("%s.%s" % (opts.app_label, codename))
    if not _get_config:
        _get_config = get_config

    config = _get_config('CHURCH_CONFIG')
    if not config:
        config = {}

    if config.get('dynamic', False) is True:
        config = _import_reload(_get_config('DJANGO_SETTINGS_MODULE')).CHURCH_CONFIG

    app_list = context.get('app_list')
    idx = 1
    firstApp = None
    req = context.get('request')

    for app in app_list:
        if app.get('app_label') == 'account' or app.get('app_label') == 'sites' or app.get('app_label') == 'authtoken':
            continue#去掉不要的菜单分组
        _models = [
            {
                'name': m.get('name'),
                'app_label': m.get('app_label'),
                'icon': get_icon(m.get('object_name'), unicode_to_str(m.get('name'))),
                'url': m.get('admin_url'),
                'addUrl': m.get('add_url'),
                'breadcrumbs': [{
                    'name': app.get('name'),
                    'icon': get_icon(app.get('app_label'), app.get('name'))
                }, {
                    'name': m.get('name'),
                    'icon': get_icon(m.get('object_name'), unicode_to_str(m.get('name')))
                }]
            }

            for m in app.get('models')
        ] if app.get('models') else []

        if not req.user.is_superuser :
            if firstApp is None:
                firstApp = {
                    'name': '教会管理',#app.get('name'),
                    'icon': get_icon(app.get('app_label'), app.get('name')),
                    'models': _models
                }
            else:
                firstApp['models']=firstApp.get('models') + _models
        else:
            module = {
                'name': app.get('name'),
                'icon': get_icon(app.get('app_label'), app.get('name')),
                'models': _models
            }
            data.append(module)
    if len(data) == 0:
        data.append(firstApp) 


    # 如果有menu 就读取，没有就调用系统的
    key = 'system_keep'
    if config and 'menus' in config:
        if key in config and config.get(key) != False:
            temp = config.get('menus')
            for i in temp:
                # 处理面包屑
                if 'models' in i:
                    for k in i.get('models'):
                        k['breadcrumbs'] = [{
                            'name': i.get('name'),
                            'icon': i.get('icon')
                        }, {
                            'name': k.get('name'),
                            'icon': k.get('icon')
                        }]
                else:
                    i['breadcrumbs'] = [{
                        'name': i.get('name'),
                        'icon': i.get('icon')
                    }]
                data.append(i)
        else:
            data = config.get('menus')

    # 获取侧边栏排序, 如果设置了就按照设置的内容排序, 留空则表示默认排序以及全部显示
    if config.get('menu_display') is not None:
        display_data = list()
        for _app in data:
            if _app['name'] not in config.get('menu_display'):
                continue
            _app['_weight'] = config.get('menu_display').index(_app['name'])
            display_data.append(_app)
        display_data.sort(key=lambda x: x['_weight'])
        data = display_data

    # 给每个菜单增加一个唯一标识，用于tab页判断
    eid = 1000
    for i in data:
        eid += 1
        i['eid'] = eid
        if 'models' in i:
            for k in i.get('models'):
                eid += 1
                k['eid'] = eid
    
    # theLogger.info(context)
    # theLogger.info('-------------request-----------------')
    
    # theLogger.info(req.user)
    # theLogger.info(context.get('request'))
    # theLogger.info(data)
    

    return '<script type="text/javascript">var menus={}</script>'.format(json.dumps(data, cls=LazyEncoder))
from church.models import Church

@register.simple_tag(takes_context=True)
def managed_church(context, _get_config=None):
    req = context.get('request')
    # chs = Church.objects.filter(manager=req.user)
    ret = req.user.church.name
    theLogger.info('-------------managed_church-----------------')
    theLogger.info(ret)
    # for c in chs:
    #     cd = {
    #             'name': c.code,
    #             'value':c.id,
    #             'label': c.name
    #         }
    #     ret.append(cd)
    return '<script type="text/javascript">var managed_church="{}"</script>'.format(ret)

# Custom tag for diagnostics
@register.simple_tag()
def debug_object_dump(var):
    return vars(var)
    # serialized = jsonpickle.encode(var)
    # return json.dumps(json.loads(serialized), indent=2)

@register.simple_tag()
def dumpthings(var):
    return vars(var)
    # serialized = jsonpickle.encode(var)
    # return json.dumps(json.loads(serialized), indent=2)


    
register.filter('str2varname', str2varname)
register.filter('pre_signed_url', pre_signed_url)
register.filter('tofilename', tofilename)
register.filter('timeticks', timeticks)
register.filter('jsondumps', jsondumps)



@register.filter
def datetime_to_date(dt):
    if dt is None:
        raise Exception('datetime should not be none')
    rt1 = dt.split('T')
    rt2 = dt.split(' ')
    if (len(rt1) != 2) and (len(rt2) != 2):
        raise Exception('datetime should be have T or space in it')
    return rt1[0] if len(rt1)==2 else rt2[0]




