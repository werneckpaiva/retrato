from retrato.album.models import Album
from django.utils import timezone
from django.conf import settings
from django.db import models, transaction
from django.contrib.auth.models import User
import facebook
from datetime import timedelta

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
    if request.user.is_authenticated():
        return True
    if is_album_token_valid(request, album):
        return True
    raise UnauthorizedUserException()


class FacebookUser(User):

    class Meta:
        verbose_name = 'Facebook user'
        verbose_name_plural = 'Facebook users'
        db_table = 'facebook_user'

    userID = models.CharField(max_length=50, unique=True)
    date_authorized = models.DateTimeField('date authorized', null=True)
    accessToken = None
    tokenTimeout = None
    friend_list = None

    @classmethod
    @transaction.atomic
    def get_or_create(cls, userID, accessToken):
        try:
            user = cls.objects.get(userID=userID)
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
        except FacebookUser.DoesNotExist:
            profile = FacebookUser.retrieve_profile(accessToken)
            user = FacebookUser(userID=userID,
                        first_name=profile.get('first_name'),
                        last_name=profile.get('last_name'),
                        username=userID,
                        email=profile.get('email'),
                        is_staff=False,
                        is_superuser=False)
            user.accessToken = accessToken

            found = False
            for friend_id in settings.FACEBOOK_FRIENDS_ID_LIST:
                found = found or user.has_friendship_with(friend_id)
            if not found:
                return None
            user.last_login = timezone.now()
            user.save()
        return user

    @classmethod
    def retrieve_profile(cls, accessToken):
        graph = facebook.GraphAPI(accessToken)
        profile = graph.get_object("me")
        return profile

    @classmethod
    def retrieve_friend_list(cls, accessToken):
        graph = facebook.GraphAPI(accessToken)
        friends = graph.get_connections("me", "friends")
        return friends

    def has_friendship_with(self, friend_id):
        if friend_id == self.userID:
            return True
        if self.friend_list is None:
            data = FacebookUser.retrieve_friend_list(self.accessToken)
            self.friend_list = data.get('data', None)
        for friend in self.friend_list:
            if friend['id'] == friend_id:
                return True
        return False

    def is_authenticated(self):
        if self.date_authorized is not None:
            return True
        time_to_expire = timedelta(seconds=settings.FACEBOOK_FRIEND_NOT_AUTHORIZED_PERIOD)
        expired = (self.date_joined + time_to_expire < timezone.now())
        return not expired
