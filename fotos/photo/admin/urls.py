from django.conf.urls import patterns, url
from fotos.photo.admin.views import PhotoAdminView


urlpatterns = patterns('',
    url(r'^/(?P<photo>.*)$', PhotoAdminView.as_view(), name='admin_photo')
)
