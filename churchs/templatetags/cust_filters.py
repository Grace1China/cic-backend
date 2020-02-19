from django import template
from django.utils.html import conditional_escape
import boto3;
from django.conf import settings
# from django.utils.safestring import mark_safe   

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
    
register.filter('str2varname', str2varname)
register.filter('pre_signed_url', pre_signed_url)
register.filter('tofilename', tofilename)
register.filter('timeticks', timeticks)
register.filter('jsondumps', jsondumps)



