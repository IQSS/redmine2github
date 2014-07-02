

def get_translate_dict():
    d = {}
    for hlevel in range(1, 7):
        d['h%s.' % hlevel] = '#' * hlevel        # e.g. d['h2.'] = '##'
    d['\n# '] = '\n1. '  # lists
    d['<pre>'] = '```'  # code block
    d['</pre>'] = '\n```'  # code block
    return d

def translate_for_github(content):
    if not content:
        return None
    
    for k, v in get_translate_dict().items():
        content = content.replace(k, v)

    return content
    