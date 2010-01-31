if not globals().has_key('applet_options'):
    print "Running initialization code"
    from django.conf import settings
    applet_options = []
    applet_groups = [x
            for x in settings.INSTALLED_APPS if x.startswith('cms.applets.')]
    for applet_group in applet_groups:
        temp = __import__(applet_group, globals(), locals(),
            ['SiteOptionsForm', 'site_options', 'EntryOptionsForm',
            'entry_options'], -1)
        applet_options.append({
            'applet_group':     applet_group,
            'SiteOptionsForm':  temp.__dict__.get('SiteOptionsForm', None),
            'site_options':     temp.__dict__.get('site_options', None),
            'EntryOptionsForm': temp.__dict__.get('EntryOptionsForm', None),
            'entry_options':    temp.__dict__.get('entry_options', None),
        })
else:
    print "Initialization code already run, skipped"
