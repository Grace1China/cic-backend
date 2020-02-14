# from churchs.models import Church

# def getChurchByCode(church_code):
#     Church.objects.get(Q(invate=data.get("username", "")))
from rest_framework.renderers import BrowsableAPIRenderer
import oss2
from django.conf import settings

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

        obj = str.replace(obj, '%s.' % settings.ALIOSS_DESTINATION_BUCKET_NAME,'')
        obj = str.replace(obj, '%s/' % settings.ALIOSS_DESTINATION_ENDPOINT,'')
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
        key = CICUtill. getObjectKey(key)
        auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
        bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATIONS[dest]['endpoint'], settings.ALIOSS_DESTINATIONS[dest]['bucket'])
        retval = bucket.sign_url('GET', key, settings.ALIOSS_EXPIRES)
        return retval

    def isReadable(key='',dest='source'):
        key = CICUtill. getObjectKey(key)
        auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
        bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATIONS[dest]['endpoint'], settings.ALIOSS_DESTINATIONS[dest]['bucket'])
        if bucket.get_object_acl(key).acl == oss2.OBJECT_ACL_PUBLIC_READ or bucket.get_object_acl(key).acl == oss2.OBJECT_ACL_PUBLIC_READ_WRITE:
            return True
        else:
            return False

