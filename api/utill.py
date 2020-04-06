# from churchs.models import Church

# def getChurchByCode(church_code):
#     Church.objects.get(Q(invate=data.get("username", "")))
from rest_framework.renderers import BrowsableAPIRenderer
import oss2
from django.conf import settings
from rest_framework.permissions import IsAuthenticated,AllowAny


class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):
    """Renders the browsable api, but excludes the forms."""

    def get_context(self, *args, **kwargs):
        ctx = super().get_context(*args, **kwargs)
        ctx['display_edit_forms'] = True
        return ctx
class CICUtill():
    '''
    一些有用的方法
    '''
    def getObjectKey(obj):
        #https://bicf-media-source.oss-cn-beijing.aliyuncs.com/l3/ddd.mp3
        import re
        obj = re.sub('^.*(https://|http://)(.*?)/','',obj,count=1)
        obj = re.sub(r'\?.*$','',obj,count=1)
        # https://bicf-media-source.oss-cn-beijing.aliyuncs.com/L3/f6.mp4?OSSAccessKeyId=LTAI4Fd1JMHM3WSUN4vrHcj8&Expires=1584879612&Signature=rJmz9enxjtuY0y9qwgV1OLhaW5U=
        # obj = str.replace(obj, '%s.' % settings.ALIOSS_DESTINATION_BUCKET_NAME,'')
        # obj = str.replace(obj, '%s/' % settings.ALIOSS_DESTINATION_ENDPOINT,'')
        return obj
    def signurl(key='', whichbucket='source'):
        key = CICUtill. getObjectKey(key)
        if whichbucket == 'destination':
            auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
            retval = bucket.sign_url('GET', key, settings.ALIOSS_EXPIRES)
            return retval
        elif whichbucket == 'source':
            auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            bucket = oss2.Bucket(auth, settings.ALIOSS_SOURCE_ENDPOINT, settings.ALIOSS_SOURCE_BUCKET_NAME)
            retval = bucket.sign_url('GET', key, settings.ALIOSS_EXPIRES)
            return retval
        else:
            raise Exception('no such bucket')

    def signurl1(key='', dest='source'):
        # from django.conf import settings
        if key is None or key == '':
            return None
        key = CICUtill. getObjectKey(key)
        auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
        bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATIONS[dest]['endpoint'], settings.ALIOSS_DESTINATIONS[dest]['bucket'])
        retval = bucket.sign_url('GET', key, settings.ALIOSS_EXPIRES)
        # retval = retval.replace('%s.%s' % (settings.ALIOSS_DESTINATION_BUCKET_NAME,settings.ALIOSS_DESTINATION_LOCATION),settings.MEDIABASE_PREFIX)
        retval = CICUtill.redirectWith(dest=dest,url=retval)
        if settings.ALIOSS_DESTINATIONS[dest]['redirecturl'] not in retval :
            raise Exception('%s:%s' % ('no right redirecturl',retval)) 
        import logging
        logger = logging.getLogger('dev.error')
        logger.error('%s.%s' % (settings.ALIOSS_DESTINATION_BUCKET_NAME,settings.ALIOSS_DESTINATION_LOCATION))
        logger.error(retval)
        return retval

    def isReadable(key='',dest='source'):
        if key is None or key == '':
            return None
        print('--------key-------------')
        print(key)
        key = CICUtill. getObjectKey(key)
        print('--------key-------------')
        print(key)
        auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
        bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATIONS[dest]['endpoint'], settings.ALIOSS_DESTINATIONS[dest]['bucket'])
        if bucket.get_object_acl(key).acl == oss2.OBJECT_ACL_PUBLIC_READ or bucket.get_object_acl(key).acl == oss2.OBJECT_ACL_PUBLIC_READ_WRITE:
            return True
        else:
            return False
    def redirectWith(dest="destination",url=''):
        url = url.replace('%s.%s' % (settings.ALIOSS_DESTINATIONS[dest]['bucket'],settings.ALIOSS_DESTINATIONS[dest]['location']),settings.ALIOSS_DESTINATIONS[dest]['redirecturl'])
        return url
    
    def getPermissionClass():
        from django.conf import settings
        if settings.RUNTIME == 'sandbox' : #or settings.RUNTIME =='development'
            return AllowAny
        else:
            return IsAuthenticated


