from django.conf import settings

def zadig_media(request):
    zadig_media_url = settings.ZADIG_MEDIA_URL
    if not zadig_media_url.endswith('/'): zadig_media_url += '/'
    return { 'ZADIG_MEDIA_URL': zadig_media_url }
