from functools import wraps
from django.utils.decorators import available_attrs
from django.contrib.auth.decorators import login_required
from retrato.album.models import Album
from retrato.album.views import AlbumView


def is_album_token_valid(request):
    token = request.GET.get("token", None)
    album_path = request.path.replace("/album", "")
    album_base = AlbumView.get_album_base()
    album = Album(album_base, album_path)
    config = album.config_file()
    if not config:
        return False

    return config.get("token") == token


def login_or_token_required(function=None):

    login_required_function = login_required(function)

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _token_based_view(request, *args, **kwargs):
            if is_album_token_valid(request):
                return view_func(request, *args, **kwargs)
            else:
                return login_required_function(request, *args, **kwargs)
        return _token_based_view
    if function:
        return decorator(function)
    return decorator
