from django.urls import path
from . import views
# from .views import UploadDocumentView
urlpatterns = [
    path("ScanUpload/", views.upload_document, name="upload_document"),
    path("detail/<int:doc_id>/", views.document_detail, name="document_detail"),
    path("matches/<int:doc_id>/", views.document_matches, name="document_matches"),
    path("dashboard/",views.analytics_dashboard, name="dashboard")
]
