from retrato.album.models import Album
from django.utils import timezone
from django.conf import settings
from django.db import models, transaction
from django.contrib.auth.models import User
import facebook


class UnauthorizedUserException(Exception):
    pass


def is_album_token_valid(request, album=None):
    from retrato.album.views import AlbumView
    token = request.GET.get("token", None)
    if album is None:
        album_path = request.path.replace("/album", "", 1)
        album_base = AlbumView.get_album_base()
        album = Album(album_base, album_path)
    config = album.config()
    if not config:
        return False

    return str(config.get("token")) == str(token)


def check_album_token_valid_or_user_authenticated(request, album=None):
    if not settings.REQUIRE_AUTHENTICATION:
        return True
    if is_album_token_valid(request, album) or request.user.is_authenticated():
        return True
    raise UnauthorizedUserException()


class FacebookUser(models.Model):

    class Meta:
        verbose_name = 'Facebook user'
        verbose_name_plural = 'Facebook users'
        db_table = 'facebook_user'

    userID = models.CharField('name', max_length=80, unique=True)
    user = models.OneToOneField(User)
    date_authorized = models.DateTimeField('date authorized', null=True)
    accessToken = None
    tokenTimeout = None

    @classmethod
    @transaction.atomic
    def get_or_create(cls, userID, accessToken):
        try:
            facebook_user = FacebookUser.objects.select_related('user').get(userID=userID)
            facebook_user.user.last_login = timezone.now()
            facebook_user.user.save(update_fields=['last_login'])
        except FacebookUser.DoesNotExist:
            profile = FacebookUser.retrieve_profile(accessToken)
            user = User(first_name=profile.get('first_name'),
                        last_name=profile.get('last_name'),
                        username=userID,
                        email=profile.get('email'),
                        is_staff=False,
                        is_superuser=False)
            user.save()
            facebook_user = FacebookUser(userID=userID, user=user)
            facebook_user.save()
        return facebook_user

    @classmethod
    def retrieve_profile(cls, accessToken):
        graph = facebook.GraphAPI(accessToken)
        profile = graph.get_object("me")
        return profile
