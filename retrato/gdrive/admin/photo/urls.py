from django.urls import path
from retrato.admin.photo.views import PhotoAdminView


urlpatterns = [
    path('<path:photo>', PhotoAdminView.as_view(), name='admin_photo')
]
