from django.template import Context, loader
from django.http import HttpResponse
import django


def index(request):
    t = loader.get_template('albuns/index.html')
    c = Context({
        'version': django.get_version()
    })
    return HttpResponse(t.render(c))
