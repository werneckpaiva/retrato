from django.contrib.auth.backends import ModelBackend
from retrato.auth.models import FacebookUser
from django.contrib.auth.models import User


class FacebookAuthenticationBackend(ModelBackend):

    def authenticate(self, facebookUserID, facebookAccessToken):
        facebook_user = FacebookUser.get_or_create(userID=facebookUserID,
                                                   accessToken=facebookAccessToken)
        return facebook_user.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
