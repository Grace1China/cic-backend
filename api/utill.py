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
    def signurl(self,key='', whichbucket='source'):
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
