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
