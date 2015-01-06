from django.contrib.auth.backends import ModelBackend
from retrato.auth.models import FacebookUser


class FacebookAuthenticationBackend(ModelBackend):

    def authenticate(self, facebookUserID, facebookAccessToken):
        facebook_user = FacebookUser.get_or_create(userID=facebookUserID,
                                                   accessToken=facebookAccessToken)
        return facebook_user

    def get_user(self, user_id):
        try:
            return FacebookUser.objects.get(pk=user_id)
        except FacebookUser.DoesNotExist:
            return None
