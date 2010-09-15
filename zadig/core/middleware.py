import settings

class GeneralMiddleware(object):

    def process_request(self, request):
        if 'set_language' in request.GET:
            lang = request.GET['set_language']
            if lang in (x[0] for x in settings.ZADIG_LANGUAGES):
                request.session['language'] = lang
        request.multilingual_groups_to_check = set()
        return None

    def process_response(self, request, response):
        from zadig.core.models import MultilingualGroup
        for mgid in request.multilingual_groups_to_check:
            MultilingualGroup.objects.get(id=mgid).check()
        return response
