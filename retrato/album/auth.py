from functools import wraps
from django.utils.decorators import available_attrs
from django.contrib.auth.decorators import login_required
from retrato.album.models import Album
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.encoding import force_str
from django.conf import settings
from django.shortcuts import resolve_url
from django.contrib.auth.views import redirect_to_login as base_redirect_to_login


class UnauthorizedUserException(Exception):
    pass


def is_album_token_valid(request, album=None):
    from retrato.album.views import AlbumView
    token = request.GET.get("token", None)
    if album is None:
        album_path = request.path.replace("/album", "", 1)
        album_base = AlbumView.get_album_base()
        album = Album(album_base, album_path)
    config = album.config_file()
    if not config:
        return False

    return str(config.get("token")) == str(token)


def check_album_token_valid_or_user_authenticated(request, album=None):
    if not settings.REQUIRE_AUTHENTICATION:
        return True
    if is_album_token_valid(request, album) or request.user.is_authenticated():
        return True
    raise UnauthorizedUserException()


def redirect_to_login(request):
    resolved_login_url = force_str(resolve_url(settings.LOGIN_URL))
    path = request.get_full_path()
    return base_redirect_to_login(path, resolved_login_url, REDIRECT_FIELD_NAME)


def login_or_token_required(function=None):

    login_required_function = login_required(function)

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _token_based_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)

            if is_album_token_valid(request):
                return view_func(request, *args, **kwargs)
            else:
                return login_required_function(request, *args, **kwargs)
        return _token_based_view
    if function:
        return decorator(function)
    return decorator
