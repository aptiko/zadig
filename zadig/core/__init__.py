if not globals().has_key('application_options'):
    # Run initialization code
    from django.conf import settings
    application_options = []
    zadig_applications = [x for x in settings.INSTALLED_APPS
               if x.startswith('zadig.') and not x.startswith('zadig.core.')]
    for zadig_application in zadig_applications:
        temp = __import__(zadig_application, globals(), locals(),
                ['EntryOptionsForm', 'entry_options', 'portlets'], -1)
        application_options.append({
            'application':      zadig_application,
            'EntryOptionsForm': temp.__dict__.get('EntryOptionsForm', None),
            'entry_options':    temp.__dict__.get('entry_options', None),
            'portlets':         temp.__dict__.get('portlets', None),
        })
