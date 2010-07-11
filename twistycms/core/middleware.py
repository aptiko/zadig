import settings

class GeneralMiddleware(object):
    def process_request(self, request):
        if 'set_language' in request.GET:
            lang = request.GET['set_language']
            if lang in settings.LANGUAGES:
                request.session['language'] = lang
            if not 'language' in request.session:
                request.session['language'] = settings.LANGUAGES[0]
        return None
