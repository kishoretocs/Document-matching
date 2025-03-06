
from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("request-credits/", views.request_credits, name="request_credits"),
    path("list-requests/",views.list_credit_requests,name='request_list'),
    path("approve-credits/<int:request_id>/", views.approve_credits, name="approve_credits"),
]
