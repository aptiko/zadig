if not globals().has_key('applet_options'):
    # Run initialization code
    from django.conf import settings
    applet_options = []
    applet_groups = [x for x in settings.INSTALLED_APPS
                                        if x.startswith('twistycms.applets.')]
    for applet_group in applet_groups:
        temp = __import__(applet_group, globals(), locals(),
            ['EntryOptionsForm', 'entry_options', 'portlets'], -1)
        applet_options.append({
            'applet_group':     applet_group,
            'EntryOptionsForm': temp.__dict__.get('EntryOptionsForm', None),
            'entry_options':    temp.__dict__.get('entry_options', None),
            'portlets':         temp.__dict__.get('portlets', None),
        })
