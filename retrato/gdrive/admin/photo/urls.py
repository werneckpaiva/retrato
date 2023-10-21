from django.urls import path

from retrato.gdrive.admin.photo.views import GdrivePhotoAdminView

urlpatterns = [
    path('<path:photo>', GdrivePhotoAdminView.as_view(), name='gdrive_admin_photo')
]
