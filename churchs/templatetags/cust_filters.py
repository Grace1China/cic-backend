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
    url = url.split('%s/'.format(settings.AWS_STORAGE_BUCKET_NAME))[1]
    print(url)
    s3_client = boto3.client('s3',aws_access_key_id=settings.AWS_ACCESS_KEY_ID,aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    
    try:
        # response = s3_client.generate_presigned_url('get_object',Params={'Bucket': 'cic-bankend','Key': 'uploads/pdfs/20191215IMS-1024.jpg'},ExpiresIn=3600)
        response = s3_client.generate_presigned_url('get_object',Params={ 'Bucket': settings.AWS_STORAGE_BUCKET_NAME,'Key': url },ExpiresIn=3600)
    except Exception as e:
        return str(e)

    return response
register.filter('pre_signed_url', pre_signed_url)