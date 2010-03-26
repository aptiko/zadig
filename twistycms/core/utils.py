def get_current_path(request):
    path = request.path
    assert(path[0] == '/')
    path = path[1:]
    if path.endswith('/'): path = path[:-1]
    path_items = path.split('/')
    for i,p in enumerate(path_items):
        if p.startswith('__') and p.endswith('__'):
            path_items = path_items[:i]
            break
    result = '/' + '/'.join(path_items)
    if result != '/': result += '/'
    return result

def split_twisty_path(twisty_path):
    from twistycms.core.models import Site
    if twisty_path.startswith('/'):
        twisty_path = twisty_path[1:]
    components = twisty_path.split('/', 1)
    if len(components)==1:
        components.append('')
    if components[0] in [x.name for x in Site.objects.all()]:
        return components
    else:
        return ('main', twisty_path)

def join_twisty_path(site, path):
    if path.startswith('/'): path = path[1:]
    if site=='main':
        return path
    else:
        return '/'.join(site, path)
