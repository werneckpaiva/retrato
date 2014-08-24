from django.conf.urls import patterns, url
from retrato.photo.admin.views import PhotoAdminView


urlpatterns = patterns('',
    url(r'^/(?P<photo>.*)$', PhotoAdminView.as_view(), name='admin_photo')
)
