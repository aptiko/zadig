import settings
import threading

threadlocals = threading.local()

class GeneralMiddleware(object):

    def process_request(self, request):
        if 'set_language' in request.GET:
            lang = request.GET['set_language']
            if lang in (x[0] for x in settings.ZADIG_LANGUAGES):
                request.session['language'] = lang
        threadlocals.multilingual_groups_to_check = set()
        threadlocals.request = request
        return None

    def process_response(self, request, response):
        from zadig.core.models import MultilingualGroup
        if hasattr(threadlocals.__dict__, 'multilingual_groups_to_check'):
            for mgid in threadlocals.multilingual_groups_to_check:
                MultilingualGroup.objects.get(id=mgid).check()
        return response
